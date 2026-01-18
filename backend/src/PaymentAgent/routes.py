"""
FastAPI Routes for Payment Agent

Provides REST API endpoints for:
- Chat with payment agent
- Product search
- Cart management
- Checkout operations
- Order status tracking
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import asyncio

from .payment_agent import PaymentAgent
from .stripe_tools import StripeTools
from .ucp_client import UCPClient, Address as UCPAddress

router = APIRouter(prefix="/payment-agent", tags=["Payment Agent"])

# Global agent instance (in production, use dependency injection with proper lifecycle)
_agent_instance: Optional[PaymentAgent] = None


def get_agent() -> PaymentAgent:
    """Get or create payment agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PaymentAgent()
    return _agent_instance


# Request/Response Models

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat message response"""
    response: str
    conversation_id: Optional[str] = None


class ProductSearchRequest(BaseModel):
    """Product search request"""
    query: str
    limit: int = 10
    categories: Optional[List[str]] = None


class ProductSearchResponse(BaseModel):
    """Product search response"""
    products: List[Dict[str, Any]]
    count: int


class AddToCartRequest(BaseModel):
    """Add to cart request"""
    product_id: str
    quantity: int = 1
    price_id: Optional[str] = None


class AddToCartResponse(BaseModel):
    """Add to cart response"""
    success: bool
    message: str
    cart_size: int


class ViewCartResponse(BaseModel):
    """View cart response"""
    items: List[Dict[str, Any]]
    item_count: int


class Address(BaseModel):
    """Address model"""
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str


class CreateCheckoutRequest(BaseModel):
    """Create checkout request"""
    merchant_url: str
    buyer_email: EmailStr
    buyer_name: Optional[str] = None
    shipping_address: Optional[Address] = None


class CreateCheckoutResponse(BaseModel):
    """Create checkout response"""
    success: bool
    protocol: str
    checkout_id: str
    checkout_url: Optional[str] = None
    amount_total: Optional[int] = None
    currency: Optional[str] = None


class CompleteCheckoutRequest(BaseModel):
    """Complete checkout request"""
    checkout_id: str
    confirm_purchase: bool


class CompleteCheckoutResponse(BaseModel):
    """Complete checkout response"""
    success: bool
    order_id: Optional[str] = None
    order_number: Optional[str] = None
    message: str


class OrderStatusRequest(BaseModel):
    """Order status request"""
    order_id: str


class OrderStatusResponse(BaseModel):
    """Order status response"""
    success: bool
    status: Optional[str] = None
    payment_status: Optional[str] = None
    amount_total: Optional[int] = None


# Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    agent: PaymentAgent = Depends(get_agent)
) -> ChatResponse:
    """
    Chat with the payment agent
    
    The agent can help with:
    - Product search and discovery
    - Cart management
    - Checkout guidance
    - Order status tracking
    """
    try:
        response = await agent.chat(
            user_message=request.message,
            user_context=request.context
        )
        
        return ChatResponse(
            response=response,
            conversation_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-products", response_model=ProductSearchResponse)
async def search_products(
    request: ProductSearchRequest,
    agent: PaymentAgent = Depends(get_agent)
) -> ProductSearchResponse:
    """Search for products in the catalog"""
    try:
        result = await agent._search_products(
            query=request.query,
            limit=request.limit
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ProductSearchResponse(
            products=result["products"],
            count=result["count"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cart/add", response_model=AddToCartResponse)
async def add_to_cart(
    request: AddToCartRequest,
    agent: PaymentAgent = Depends(get_agent)
) -> AddToCartResponse:
    """Add item to shopping cart"""
    try:
        result = await agent._add_to_cart(
            product_id=request.product_id,
            quantity=request.quantity,
            price_id=request.price_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return AddToCartResponse(
            success=True,
            message=result["message"],
            cart_size=result["cart_size"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cart", response_model=ViewCartResponse)
async def view_cart(
    agent: PaymentAgent = Depends(get_agent)
) -> ViewCartResponse:
    """View current shopping cart"""
    try:
        result = await agent._view_cart()
        
        return ViewCartResponse(
            items=result["cart"],
            item_count=result["item_count"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart/clear")
async def clear_cart(
    agent: PaymentAgent = Depends(get_agent)
) -> Dict[str, str]:
    """Clear shopping cart"""
    try:
        agent.current_cart = []
        return {"message": "Cart cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/create", response_model=CreateCheckoutResponse)
async def create_checkout(
    request: CreateCheckoutRequest,
    agent: PaymentAgent = Depends(get_agent)
) -> CreateCheckoutResponse:
    """Create a checkout session"""
    try:
        # Convert address if provided
        shipping_address = None
        if request.shipping_address:
            shipping_address = request.shipping_address.dict()
        
        result = await agent._create_checkout(
            merchant_url=request.merchant_url,
            buyer_email=request.buyer_email,
            buyer_name=request.buyer_name,
            shipping_address=shipping_address
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        checkout = result.get("checkout", {})
        
        return CreateCheckoutResponse(
            success=True,
            protocol=result.get("protocol", "unknown"),
            checkout_id=checkout.get("id", ""),
            checkout_url=checkout.get("url"),
            amount_total=checkout.get("amount_total"),
            currency=checkout.get("currency")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/complete", response_model=CompleteCheckoutResponse)
async def complete_checkout(
    request: CompleteCheckoutRequest,
    agent: PaymentAgent = Depends(get_agent)
) -> CompleteCheckoutResponse:
    """Complete checkout and process payment"""
    try:
        result = await agent._complete_checkout(
            checkout_id=request.checkout_id,
            confirm_purchase=request.confirm_purchase
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        order = result.get("order", {})
        
        return CompleteCheckoutResponse(
            success=True,
            order_id=order.get("id"),
            order_number=order.get("order_number"),
            message=result.get("message", "Checkout completed")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/order/status", response_model=OrderStatusResponse)
async def check_order_status(
    request: OrderStatusRequest,
    agent: PaymentAgent = Depends(get_agent)
) -> OrderStatusResponse:
    """Check order status"""
    try:
        result = await agent._check_order_status(order_id=request.order_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        status_data = result.get("status", {})
        
        return OrderStatusResponse(
            success=True,
            status=status_data.get("status"),
            payment_status=status_data.get("payment_status"),
            amount_total=status_data.get("amount_total")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """Get agent capabilities"""
    return {
        "features": [
            "product_search",
            "cart_management",
            "ucp_checkout",
            "stripe_checkout",
            "browser_fallback",
            "order_tracking"
        ],
        "supported_protocols": [
            "UCP",
            "Stripe Checkout",
            "Browser Automation"
        ],
        "ai_model": "Gemini 2.0 Flash"
    }


@router.post("/ucp/discover")
async def discover_merchant_ucp(merchant_url: str) -> Dict[str, Any]:
    """Discover if merchant supports UCP"""
    try:
        client = UCPClient(merchant_url)
        capabilities = await client.discover()
        
        return {
            "merchant_url": merchant_url,
            "supported": capabilities.supported,
            "version": capabilities.version,
            "endpoints": capabilities.endpoints,
            "features": capabilities.features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
