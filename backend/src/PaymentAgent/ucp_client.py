"""
Universal Checkout Protocol (UCP) Client

Implements the UCP/ACP specification for agentic commerce:
- Discovery: Check merchant UCP support via .well-known/ucp
- Negotiation: Create and update checkout sessions
- Completion: Finalize checkout with Shared Payment Token
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from pydantic import BaseModel, HttpUrl
from enum import Enum


class CheckoutStatus(str, Enum):
    """Checkout session statuses"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Address(BaseModel):
    """Address model for shipping/billing"""
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str


class LineItem(BaseModel):
    """Line item in checkout"""
    product_id: str
    quantity: int
    price_id: Optional[str] = None
    variant_id: Optional[str] = None


class BuyerInfo(BaseModel):
    """Buyer information"""
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None


class CreateCheckoutRequest(BaseModel):
    """Request to create a checkout session"""
    items: List[LineItem]
    buyer: BuyerInfo
    fulfillment_address: Optional[Address] = None
    billing_address: Optional[Address] = None
    metadata: Optional[Dict[str, str]] = None


class UpdateCheckoutRequest(BaseModel):
    """Request to update a checkout session"""
    items: Optional[List[LineItem]] = None
    fulfillment_address: Optional[Address] = None
    billing_address: Optional[Address] = None
    shipping_option_id: Optional[str] = None


class CompleteCheckoutRequest(BaseModel):
    """Request to complete a checkout"""
    payment_token: str  # Shared Payment Token from Stripe
    idempotency_key: Optional[str] = None


class UCPCapabilities(BaseModel):
    """UCP capabilities discovered from merchant"""
    supported: bool
    version: str = "1.0"
    endpoints: Dict[str, str]
    features: List[str] = []


class UCPClient:
    """
    Universal Checkout Protocol Client
    
    Handles discovery, negotiation, and completion of checkouts
    with UCP-compliant merchants.
    """
    
    def __init__(
        self, 
        merchant_base_url: str,
        auth_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize UCP client
        
        Args:
            merchant_base_url: Base URL of merchant (e.g., https://shop.example.com)
            auth_token: Optional bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = merchant_base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._capabilities: Optional[UCPCapabilities] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if available"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Lovelace-PaymentAgent/1.0",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def discover(self) -> UCPCapabilities:
        """
        Discover UCP capabilities via .well-known/ucp endpoint
        
        Returns:
            UCPCapabilities object with merchant's UCP support details
        """
        url = urljoin(self.base_url, "/.well-known/ucp")
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 404:
                        # Merchant doesn't support UCP
                        self._capabilities = UCPCapabilities(
                            supported=False,
                            endpoints={}
                        )
                        return self._capabilities
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    self._capabilities = UCPCapabilities(**data)
                    return self._capabilities
        except aiohttp.ClientError as e:
            raise Exception(f"UCP discovery failed: {str(e)}")
    
    async def supports_ucp(self) -> bool:
        """
        Check if merchant supports UCP
        
        Returns:
            True if merchant supports UCP, False otherwise
        """
        if self._capabilities is None:
            await self.discover()
        return self._capabilities.supported if self._capabilities else False
    
    async def create_checkout(
        self,
        items: List[LineItem],
        buyer: BuyerInfo,
        fulfillment_address: Optional[Address] = None,
        billing_address: Optional[Address] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a checkout session with the merchant
        
        Args:
            items: List of line items to purchase
            buyer: Buyer information
            fulfillment_address: Optional shipping address
            billing_address: Optional billing address
            metadata: Optional metadata
            
        Returns:
            Checkout session object with totals, shipping options, etc.
        """
        if not await self.supports_ucp():
            raise Exception("Merchant does not support UCP")
        
        # Get checkout endpoint from capabilities
        endpoint = self._capabilities.endpoints.get("create_checkout", "/ucp/checkout")
        url = urljoin(self.base_url, endpoint)
        
        request = CreateCheckoutRequest(
            items=items,
            buyer=buyer,
            fulfillment_address=fulfillment_address,
            billing_address=billing_address,
            metadata=metadata
        )
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    url,
                    json=request.dict(exclude_none=True),
                    headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Create checkout failed: {str(e)}")
    
    async def update_checkout(
        self,
        checkout_id: str,
        items: Optional[List[LineItem]] = None,
        fulfillment_address: Optional[Address] = None,
        billing_address: Optional[Address] = None,
        shipping_option_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing checkout session
        
        Args:
            checkout_id: Checkout session ID
            items: Optional updated line items
            fulfillment_address: Optional updated shipping address
            billing_address: Optional updated billing address
            shipping_option_id: Optional selected shipping option
            
        Returns:
            Updated checkout session object
        """
        endpoint = self._capabilities.endpoints.get("update_checkout", f"/ucp/checkout/{checkout_id}")
        url = urljoin(self.base_url, endpoint.replace("{id}", checkout_id))
        
        request = UpdateCheckoutRequest(
            items=items,
            fulfillment_address=fulfillment_address,
            billing_address=billing_address,
            shipping_option_id=shipping_option_id
        )
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.patch(
                    url,
                    json=request.dict(exclude_none=True),
                    headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Update checkout failed: {str(e)}")
    
    async def complete_checkout(
        self,
        checkout_id: str,
        payment_token: str,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete checkout with Shared Payment Token
        
        Args:
            checkout_id: Checkout session ID
            payment_token: Shared Payment Token from Stripe
            idempotency_key: Optional idempotency key for retry safety
            
        Returns:
            Completed order details
        """
        endpoint = self._capabilities.endpoints.get(
            "complete_checkout", 
            f"/ucp/checkout/{checkout_id}/complete"
        )
        url = urljoin(self.base_url, endpoint.replace("{id}", checkout_id))
        
        request = CompleteCheckoutRequest(
            payment_token=payment_token,
            idempotency_key=idempotency_key
        )
        
        headers = self._get_headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    url,
                    json=request.dict(exclude_none=True),
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Complete checkout failed: {str(e)}")
    
    async def cancel_checkout(self, checkout_id: str) -> Dict[str, Any]:
        """
        Cancel a checkout session
        
        Args:
            checkout_id: Checkout session ID
            
        Returns:
            Cancellation confirmation
        """
        endpoint = self._capabilities.endpoints.get(
            "cancel_checkout",
            f"/ucp/checkout/{checkout_id}/cancel"
        )
        url = urljoin(self.base_url, endpoint.replace("{id}", checkout_id))
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    url,
                    headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Cancel checkout failed: {str(e)}")
    
    async def get_checkout(self, checkout_id: str) -> Dict[str, Any]:
        """
        Get checkout session details
        
        Args:
            checkout_id: Checkout session ID
            
        Returns:
            Checkout session object
        """
        endpoint = self._capabilities.endpoints.get(
            "get_checkout",
            f"/ucp/checkout/{checkout_id}"
        )
        url = urljoin(self.base_url, endpoint.replace("{id}", checkout_id))
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    url,
                    headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Get checkout failed: {str(e)}")
