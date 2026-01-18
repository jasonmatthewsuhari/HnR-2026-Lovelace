"""
Browser Automation Fallback

Uses Playwright to automate checkout on non-UCP-compliant merchant sites.
This is a fallback mechanism when merchants don't support the Universal Checkout Protocol.

Security Notes:
- Payment details should use tokenized methods when possible
- Never store raw card data
- Use secure credential management
"""

import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import logging

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """
    Headless browser automation for non-UCP merchants
    
    Handles:
    - Product search and selection
    - Cart management
    - Checkout form filling
    - Address entry
    - Secure payment (via saved methods or tokens)
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 60000,  # 60 seconds
        screenshot_on_error: bool = True
    ):
        """
        Initialize browser automation
        
        Args:
            headless: Run browser in headless mode
            timeout: Default timeout for operations in milliseconds
            screenshot_on_error: Take screenshots on errors for debugging
        """
        self.headless = headless
        self.timeout = timeout
        self.screenshot_on_error = screenshot_on_error
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.stop()
    
    async def start(self):
        """Start browser instance"""
        if self.browser:
            return
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with realistic user agent
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )
    
    async def stop(self):
        """Stop browser instance"""
        if self.context:
            await self.context.close()
            self.context = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def automate_checkout(
        self,
        merchant_url: str,
        cart_items: List[Dict[str, Any]],
        buyer_email: str,
        buyer_name: Optional[str] = None,
        shipping_address: Optional[Dict[str, str]] = None,
        payment_method: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Automate checkout on merchant site
        
        Args:
            merchant_url: Merchant website URL
            cart_items: Items to add to cart
            buyer_email: Buyer email
            buyer_name: Buyer name
            shipping_address: Shipping address dict
            payment_method: Payment method details (tokenized)
            
        Returns:
            Result dict with success status and order details
        """
        if not self.browser:
            await self.start()
        
        page = await self.context.new_page()
        
        try:
            logger.info(f"Starting automated checkout for {merchant_url}")
            
            # Navigate to merchant site
            await page.goto(merchant_url, wait_until='networkidle', timeout=self.timeout)
            
            # Step 1: Add items to cart
            for item in cart_items:
                success = await self._add_to_cart_generic(page, item)
                if not success:
                    return {
                        "success": False,
                        "error": f"Failed to add item {item.get('product_id')} to cart"
                    }
            
            # Step 2: Navigate to checkout
            await self._navigate_to_checkout(page)
            
            # Step 3: Fill shipping information
            if shipping_address:
                await self._fill_shipping_address(page, shipping_address, buyer_email, buyer_name)
            
            # Step 4: Handle payment
            # Note: This is sensitive - should use saved payment methods or tokens
            payment_result = await self._handle_payment(page, payment_method)
            
            if not payment_result.get("success"):
                return payment_result
            
            # Step 5: Complete order
            order_result = await self._complete_order(page)
            
            logger.info("Automated checkout completed successfully")
            return order_result
            
        except Exception as e:
            logger.error(f"Browser automation failed: {str(e)}")
            
            if self.screenshot_on_error:
                screenshot_path = f"error_screenshot_{asyncio.get_event_loop().time()}.png"
                await page.screenshot(path=screenshot_path)
                logger.info(f"Error screenshot saved to {screenshot_path}")
            
            return {
                "success": False,
                "error": str(e),
                "screenshot": screenshot_path if self.screenshot_on_error else None
            }
        finally:
            await page.close()
    
    async def _add_to_cart_generic(self, page: Page, item: Dict[str, Any]) -> bool:
        """
        Generic add to cart logic - attempts common patterns
        
        Args:
            page: Playwright page
            item: Item dict with product_id and quantity
            
        Returns:
            True if successful
        """
        try:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            # Common selectors for "Add to Cart" buttons
            add_to_cart_selectors = [
                'button:has-text("Add to Cart")',
                'button:has-text("Add to Bag")',
                '[data-testid="add-to-cart"]',
                '.add-to-cart-button',
                '#add-to-cart',
                'button[type="submit"]:has-text("Add")'
            ]
            
            # Try to find and click add to cart button
            for selector in add_to_cart_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        await button.click()
                        logger.info(f"Added item to cart using selector: {selector}")
                        
                        # Wait for cart update
                        await page.wait_for_timeout(1000)
                        return True
                except:
                    continue
            
            logger.warning(f"Could not find add to cart button for item {product_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to add item to cart: {str(e)}")
            return False
    
    async def _navigate_to_checkout(self, page: Page):
        """Navigate to checkout page"""
        # Common checkout navigation patterns
        checkout_selectors = [
            'a:has-text("Checkout")',
            'button:has-text("Checkout")',
            '[data-testid="checkout-button"]',
            '.checkout-button',
            '#checkout',
            'a[href*="checkout"]'
        ]
        
        for selector in checkout_selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible(timeout=2000):
                    await button.click()
                    await page.wait_for_load_state('networkidle')
                    logger.info("Navigated to checkout")
                    return
            except:
                continue
        
        raise Exception("Could not find checkout button")
    
    async def _fill_shipping_address(
        self,
        page: Page,
        address: Dict[str, str],
        email: str,
        name: Optional[str] = None
    ):
        """Fill shipping address form"""
        try:
            # Common form field mappings
            field_mappings = {
                "email": ["#email", 'input[name="email"]', 'input[type="email"]'],
                "name": ["#name", 'input[name="name"]', 'input[name="fullName"]'],
                "address1": ["#address1", 'input[name="address1"]', 'input[name="line1"]'],
                "address2": ["#address2", 'input[name="address2"]', 'input[name="line2"]'],
                "city": ["#city", 'input[name="city"]'],
                "state": ["#state", 'select[name="state"]', 'input[name="state"]'],
                "zip": ["#zip", 'input[name="zip"]', 'input[name="postalCode"]'],
                "country": ["#country", 'select[name="country"]']
            }
            
            # Fill email
            await self._fill_field(page, field_mappings["email"], email)
            
            # Fill name
            if name:
                await self._fill_field(page, field_mappings["name"], name)
            
            # Fill address fields
            if "line1" in address:
                await self._fill_field(page, field_mappings["address1"], address["line1"])
            
            if "line2" in address:
                await self._fill_field(page, field_mappings["address2"], address["line2"])
            
            if "city" in address:
                await self._fill_field(page, field_mappings["city"], address["city"])
            
            if "state" in address:
                await self._fill_field(page, field_mappings["state"], address["state"])
            
            if "postal_code" in address:
                await self._fill_field(page, field_mappings["zip"], address["postal_code"])
            
            if "country" in address:
                await self._fill_field(page, field_mappings["country"], address["country"])
            
            logger.info("Filled shipping address form")
            
        except Exception as e:
            logger.error(f"Failed to fill shipping address: {str(e)}")
            raise
    
    async def _fill_field(self, page: Page, selectors: List[str], value: str):
        """Try to fill a field using multiple selectors"""
        for selector in selectors:
            try:
                field = page.locator(selector).first
                if await field.is_visible(timeout=1000):
                    await field.fill(value)
                    return
            except:
                continue
        
        logger.warning(f"Could not find field for selectors: {selectors}")
    
    async def _handle_payment(
        self,
        page: Page,
        payment_method: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Handle payment step
        
        Note: This should ideally use saved payment methods or tokens.
        Direct card entry requires PCI compliance and is NOT recommended.
        """
        try:
            # Look for saved payment method selection
            saved_payment_selector = 'input[type="radio"][name="paymentMethod"]'
            saved_payments = page.locator(saved_payment_selector)
            
            count = await saved_payments.count()
            if count > 0:
                # Select first saved payment method
                await saved_payments.first.check()
                logger.info("Selected saved payment method")
                return {"success": True}
            
            # If no saved method, look for Stripe/PayPal/etc buttons
            alt_payment_selectors = [
                'button:has-text("PayPal")',
                '[data-testid="apple-pay"]',
                '[data-testid="google-pay"]'
            ]
            
            for selector in alt_payment_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        logger.info(f"Found alternative payment method: {selector}")
                        # Would need user interaction for these
                        return {
                            "success": False,
                            "error": "Alternative payment method requires user interaction",
                            "method": selector
                        }
                except:
                    continue
            
            # If we reach here, payment automation is not possible
            return {
                "success": False,
                "error": "No automatable payment method found. User interaction required."
            }
            
        except Exception as e:
            logger.error(f"Payment handling failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _complete_order(self, page: Page) -> Dict[str, Any]:
        """Complete the order"""
        try:
            # Look for final "Place Order" or "Complete Purchase" button
            complete_selectors = [
                'button:has-text("Place Order")',
                'button:has-text("Complete Purchase")',
                'button:has-text("Complete Order")',
                '[data-testid="complete-order"]',
                '#complete-order'
            ]
            
            for selector in complete_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        await button.click()
                        
                        # Wait for order confirmation
                        await page.wait_for_load_state('networkidle', timeout=30000)
                        
                        # Try to extract order number
                        order_number = await self._extract_order_number(page)
                        
                        return {
                            "success": True,
                            "order_number": order_number,
                            "message": "Order completed successfully"
                        }
                except:
                    continue
            
            return {
                "success": False,
                "error": "Could not find order completion button"
            }
            
        except Exception as e:
            logger.error(f"Order completion failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _extract_order_number(self, page: Page) -> Optional[str]:
        """Try to extract order number from confirmation page"""
        try:
            # Common patterns for order numbers
            order_selectors = [
                '.order-number',
                '[data-testid="order-number"]',
                '#order-number',
                'text=/Order #[A-Z0-9-]+/',
                'text=/Order Number: [A-Z0-9-]+/'
            ]
            
            for selector in order_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        text = await element.text_content()
                        logger.info(f"Found order number: {text}")
                        return text
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract order number: {str(e)}")
            return None
