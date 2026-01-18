"""
Stripe Tools for Agentic Commerce

Provides Stripe API integrations for:
- Product search and catalog management
- Checkout session creation
- Order status tracking
- Shared Payment Token (SPT) generation
"""

import os
import stripe
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class ProductSearchParams(BaseModel):
    """Parameters for product search"""
    query: str
    limit: int = 10
    categories: Optional[List[str]] = None


class CheckoutSessionParams(BaseModel):
    """Parameters for creating a checkout session"""
    line_items: List[Dict[str, Any]]
    customer_email: Optional[str] = None
    success_url: str
    cancel_url: str
    mode: str = "payment"  # payment, subscription, or setup


class SharedPaymentTokenParams(BaseModel):
    """Parameters for creating a Shared Payment Token"""
    amount: int  # in cents
    currency: str = "usd"
    merchant_account_id: str
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class StripeTools:
    """Stripe API tools for agentic commerce"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe tools with optional API key override"""
        if api_key:
            stripe.api_key = api_key
    
    def search_products(
        self, 
        query: str, 
        limit: int = 10,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search products in Stripe catalog
        
        Args:
            query: Search query string
            limit: Maximum number of results
            categories: Optional category filters
            
        Returns:
            List of product dictionaries
        """
        try:
            # Search products using Stripe API
            params = {
                "query": query,
                "limit": limit,
            }
            
            # Note: Stripe's product search API may vary based on catalog setup
            products = stripe.Product.search(**params)
            
            results = []
            for product in products.data:
                # Get associated prices
                prices = stripe.Price.list(product=product.id, active=True)
                
                results.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "images": product.images,
                    "metadata": product.metadata,
                    "prices": [
                        {
                            "id": price.id,
                            "amount": price.unit_amount,
                            "currency": price.currency,
                            "type": price.type,
                        }
                        for price in prices.data
                    ],
                })
            
            return results
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe product search failed: {str(e)}")
    
    def create_checkout_session(
        self,
        line_items: List[Dict[str, Any]],
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        mode: str = "payment",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session
        
        Args:
            line_items: List of items to checkout
            success_url: URL to redirect after success
            cancel_url: URL to redirect on cancel
            customer_email: Optional customer email
            mode: payment, subscription, or setup
            metadata: Optional metadata dict
            
        Returns:
            Checkout session details
        """
        try:
            session_params = {
                "line_items": line_items,
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if customer_email:
                session_params["customer_email"] = customer_email
            
            if metadata:
                session_params["metadata"] = metadata
            
            session = stripe.checkout.Session.create(**session_params)
            
            return {
                "id": session.id,
                "url": session.url,
                "status": session.status,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "customer": session.customer,
                "payment_status": session.payment_status,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe checkout session creation failed: {str(e)}")
    
    def check_order_status(self, session_id: str) -> Dict[str, Any]:
        """
        Check the status of a checkout session/order
        
        Args:
            session_id: Stripe Checkout Session ID
            
        Returns:
            Order status details
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            result = {
                "id": session.id,
                "status": session.status,
                "payment_status": session.payment_status,
                "amount_total": session.amount_total,
                "currency": session.currency,
            }
            
            # Get payment intent if available
            if session.payment_intent:
                payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                result["payment_intent"] = {
                    "id": payment_intent.id,
                    "status": payment_intent.status,
                    "amount": payment_intent.amount,
                    "currency": payment_intent.currency,
                }
            
            return result
        except stripe.error.StripeError as e:
            raise Exception(f"Order status check failed: {str(e)}")
    
    def create_shared_payment_token(
        self,
        amount: int,
        merchant_account_id: str,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Shared Payment Token (SPT) for UCP transactions
        
        Note: This API may be in private preview. Check Stripe docs for access.
        
        Args:
            amount: Amount in cents
            merchant_account_id: Target merchant's Stripe account
            currency: Currency code (default: usd)
            customer_id: Optional Stripe customer ID
            metadata: Optional metadata
            
        Returns:
            SPT details including token ID
        """
        try:
            # Note: The exact API for SharedPaymentToken may vary
            # This is based on the ACP documentation pattern
            
            # For now, create a PaymentIntent with transfer capability
            # In production, use the actual SPT API when available
            payment_intent_params = {
                "amount": amount,
                "currency": currency,
                "transfer_data": {
                    "destination": merchant_account_id,
                },
            }
            
            if customer_id:
                payment_intent_params["customer"] = customer_id
            
            if metadata:
                payment_intent_params["metadata"] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
            
            return {
                "token": payment_intent.client_secret,  # Acts as SPT
                "payment_intent_id": payment_intent.id,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Shared Payment Token creation failed: {str(e)}")
    
    def list_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all products in Stripe catalog
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries
        """
        try:
            products = stripe.Product.list(limit=limit, active=True)
            
            results = []
            for product in products.data:
                prices = stripe.Price.list(product=product.id, active=True)
                
                results.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "images": product.images,
                    "metadata": product.metadata,
                    "prices": [
                        {
                            "id": price.id,
                            "amount": price.unit_amount,
                            "currency": price.currency,
                        }
                        for price in prices.data
                    ],
                })
            
            return results
        except stripe.error.StripeError as e:
            raise Exception(f"Product listing failed: {str(e)}")
