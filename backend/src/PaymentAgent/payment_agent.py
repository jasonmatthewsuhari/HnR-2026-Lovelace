"""
Agentic Commerce Payment Agent

Main agent that orchestrates:
- Gemini AI for intent understanding and conversation
- Stripe tools for payment operations
- UCP client for protocol-compliant checkouts
- Browser automation fallback for non-UCP merchants
"""

import os
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from enum import Enum
import google.generativeai as genai
from dotenv import load_dotenv

from .stripe_tools import StripeTools
from .ucp_client import UCPClient, LineItem, BuyerInfo, Address
from .browser_automation import BrowserAutomation

load_dotenv()


class PurchaseIntent(str, Enum):
    """Purchase intent types"""
    SEARCH = "search"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT = "checkout"
    ORDER_STATUS = "order_status"
    CANCEL = "cancel"
    GENERAL = "general"


class PaymentAgent:
    """
    Agentic Commerce Payment Agent
    
    Orchestrates AI-driven shopping and checkout experiences using:
    - Gemini for conversation and intent understanding
    - Stripe for payments and product catalog
    - UCP for standardized checkout protocol
    - Browser automation as fallback
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        stripe_api_key: Optional[str] = None,
        enable_browser_fallback: bool = True
    ):
        """
        Initialize Payment Agent
        
        Args:
            gemini_api_key: Google Gemini API key (or from env)
            stripe_api_key: Stripe API key (or from env)
            enable_browser_fallback: Enable browser automation fallback
        """
        # Initialize Gemini
        gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # Initialize Stripe tools
        self.stripe_tools = StripeTools(api_key=stripe_api_key)
        
        # Browser automation
        self.enable_browser_fallback = enable_browser_fallback
        self.browser_automation: Optional[BrowserAutomation] = None
        if enable_browser_fallback:
            self.browser_automation = BrowserAutomation()
        
        # Session state
        self.conversation_history: List[Dict[str, str]] = []
        self.current_cart: List[Dict[str, Any]] = []
        self.current_checkout: Optional[Dict[str, Any]] = None
        
        # Tool definitions for function calling
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define tools for Gemini function calling"""
        return [
            {
                "name": "search_products",
                "description": "Search for products in the catalog",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for products"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "add_to_cart",
                "description": "Add a product to the shopping cart",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "Product ID to add"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity to add",
                            "default": 1
                        },
                        "price_id": {
                            "type": "string",
                            "description": "Specific price ID if multiple options"
                        }
                    },
                    "required": ["product_id"]
                }
            },
            {
                "name": "view_cart",
                "description": "View current items in shopping cart",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_checkout",
                "description": "Create a checkout session for current cart",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "merchant_url": {
                            "type": "string",
                            "description": "Merchant base URL"
                        },
                        "buyer_email": {
                            "type": "string",
                            "description": "Buyer email address"
                        },
                        "buyer_name": {
                            "type": "string",
                            "description": "Buyer name"
                        },
                        "shipping_address": {
                            "type": "object",
                            "description": "Shipping address details"
                        }
                    },
                    "required": ["merchant_url", "buyer_email"]
                }
            },
            {
                "name": "complete_checkout",
                "description": "Complete checkout with payment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checkout_id": {
                            "type": "string",
                            "description": "Checkout session ID"
                        },
                        "confirm_purchase": {
                            "type": "boolean",
                            "description": "User confirmation to proceed with payment"
                        }
                    },
                    "required": ["checkout_id", "confirm_purchase"]
                }
            },
            {
                "name": "check_order_status",
                "description": "Check status of an order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "Order or session ID to check"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        ]
    
    async def chat(self, user_message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process user message and return agent response
        
        Args:
            user_message: User's message
            user_context: Optional context (user profile, calendar events, etc.)
            
        Returns:
            Agent's response
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Build system prompt with context
        system_prompt = self._build_system_prompt(user_context)
        
        # Prepare chat with function calling
        chat = self.model.start_chat(history=[])
        
        try:
            # Send message with tools
            response = chat.send_message(
                f"{system_prompt}\n\nUser: {user_message}",
                tools=self._gemini_tools()
            )
            
            # Handle function calls
            if response.candidates[0].content.parts[0].function_call:
                function_response = await self._handle_function_call(
                    response.candidates[0].content.parts[0].function_call
                )
                
                # Send function response back to model
                response = chat.send_message(
                    genai.types.Content(
                        parts=[genai.types.Part(
                            function_response=genai.types.FunctionResponse(
                                name=response.candidates[0].content.parts[0].function_call.name,
                                response=function_response
                            )
                        )]
                    )
                )
            
            agent_response = response.text
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            return agent_response
            
        except Exception as e:
            error_message = f"I encountered an error: {str(e)}"
            self.conversation_history.append({
                "role": "assistant",
                "content": error_message
            })
            return error_message
    
    def _build_system_prompt(self, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt with context"""
        prompt = """You are a helpful shopping assistant integrated into the Lovelace app.
You help users discover products, manage their shopping cart, and complete purchases.

You have access to the following tools:
- search_products: Search for products
- add_to_cart: Add items to cart
- view_cart: View current cart
- create_checkout: Start checkout process
- complete_checkout: Finalize purchase
- check_order_status: Check order status

Always be helpful, conversational, and guide users through the shopping experience.
When completing purchases, always confirm total amount and get explicit user consent before finalizing."""
        
        if user_context:
            prompt += f"\n\nUser Context: {user_context}"
        
        return prompt
    
    def _gemini_tools(self) -> List[genai.types.Tool]:
        """Convert tool definitions to Gemini format"""
        # Gemini will use function calling based on tool definitions
        # This is a simplified version - in production, properly format tools
        return []
    
    async def _handle_function_call(self, function_call: Any) -> Dict[str, Any]:
        """Handle function call from Gemini"""
        function_name = function_call.name
        args = dict(function_call.args)
        
        if function_name == "search_products":
            return await self._search_products(**args)
        elif function_name == "add_to_cart":
            return await self._add_to_cart(**args)
        elif function_name == "view_cart":
            return await self._view_cart()
        elif function_name == "create_checkout":
            return await self._create_checkout(**args)
        elif function_name == "complete_checkout":
            return await self._complete_checkout(**args)
        elif function_name == "check_order_status":
            return await self._check_order_status(**args)
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    async def _search_products(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search products tool implementation"""
        try:
            products = self.stripe_tools.search_products(query, limit)
            return {
                "success": True,
                "products": products,
                "count": len(products)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _add_to_cart(
        self, 
        product_id: str, 
        quantity: int = 1,
        price_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add to cart tool implementation"""
        try:
            cart_item = {
                "product_id": product_id,
                "quantity": quantity,
                "price_id": price_id,
                "added_at": asyncio.get_event_loop().time()
            }
            self.current_cart.append(cart_item)
            
            return {
                "success": True,
                "message": f"Added {quantity} item(s) to cart",
                "cart_size": len(self.current_cart)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _view_cart(self) -> Dict[str, Any]:
        """View cart tool implementation"""
        return {
            "success": True,
            "cart": self.current_cart,
            "item_count": len(self.current_cart)
        }
    
    async def _create_checkout(
        self,
        merchant_url: str,
        buyer_email: str,
        buyer_name: Optional[str] = None,
        shipping_address: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create checkout tool implementation"""
        try:
            # Initialize UCP client
            ucp_client = UCPClient(merchant_url)
            
            # Check if merchant supports UCP
            supports_ucp = await ucp_client.supports_ucp()
            
            if supports_ucp:
                # Use UCP protocol
                items = [
                    LineItem(
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price_id=item.get("price_id")
                    )
                    for item in self.current_cart
                ]
                
                buyer = BuyerInfo(
                    email=buyer_email,
                    name=buyer_name
                )
                
                address = None
                if shipping_address:
                    address = Address(**shipping_address)
                
                checkout = await ucp_client.create_checkout(
                    items=items,
                    buyer=buyer,
                    fulfillment_address=address
                )
                
                self.current_checkout = checkout
                
                return {
                    "success": True,
                    "protocol": "UCP",
                    "checkout": checkout
                }
            else:
                # Fallback to browser automation or Stripe Checkout
                if self.enable_browser_fallback and self.browser_automation:
                    result = await self.browser_automation.automate_checkout(
                        merchant_url=merchant_url,
                        cart_items=self.current_cart,
                        buyer_email=buyer_email,
                        shipping_address=shipping_address
                    )
                    return result
                else:
                    # Use Stripe Checkout Session as fallback
                    line_items = [
                        {
                            "price": item.get("price_id") or item["product_id"],
                            "quantity": item["quantity"]
                        }
                        for item in self.current_cart
                    ]
                    
                    session = self.stripe_tools.create_checkout_session(
                        line_items=line_items,
                        success_url=f"{merchant_url}/success",
                        cancel_url=f"{merchant_url}/cancel",
                        customer_email=buyer_email
                    )
                    
                    self.current_checkout = session
                    
                    return {
                        "success": True,
                        "protocol": "Stripe Checkout",
                        "checkout": session
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _complete_checkout(
        self,
        checkout_id: str,
        confirm_purchase: bool
    ) -> Dict[str, Any]:
        """Complete checkout tool implementation"""
        if not confirm_purchase:
            return {
                "success": False,
                "message": "Purchase not confirmed by user"
            }
        
        try:
            if not self.current_checkout:
                return {"success": False, "error": "No active checkout"}
            
            # Check if UCP checkout or Stripe checkout
            if "protocol" in self.current_checkout and self.current_checkout["protocol"] == "UCP":
                # Get merchant URL from checkout
                merchant_url = self.current_checkout.get("merchant_url")
                ucp_client = UCPClient(merchant_url)
                
                # Create Shared Payment Token
                checkout_total = self.current_checkout.get("amount_total", 0)
                merchant_account = self.current_checkout.get("merchant_account_id")
                
                spt_result = self.stripe_tools.create_shared_payment_token(
                    amount=checkout_total,
                    merchant_account_id=merchant_account
                )
                
                # Complete checkout with SPT
                order = await ucp_client.complete_checkout(
                    checkout_id=checkout_id,
                    payment_token=spt_result["token"],
                    idempotency_key=str(uuid.uuid4())
                )
                
                # Clear cart
                self.current_cart = []
                self.current_checkout = None
                
                return {
                    "success": True,
                    "order": order,
                    "message": "Purchase completed successfully!"
                }
            else:
                # Stripe Checkout - just return the URL for user to complete
                return {
                    "success": True,
                    "checkout_url": self.current_checkout.get("url"),
                    "message": "Please complete payment at the checkout URL"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_order_status(self, order_id: str) -> Dict[str, Any]:
        """Check order status tool implementation"""
        try:
            status = self.stripe_tools.check_order_status(order_id)
            return {
                "success": True,
                "status": status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
