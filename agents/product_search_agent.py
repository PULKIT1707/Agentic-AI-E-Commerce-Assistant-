"""
Product Search API Agent
Finds products matching user preferences and requirements from e-commerce APIs.
"""
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import json
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import logging
import urllib.parse

logger = logging.getLogger(__name__)


class ProductSearchAgent(BaseAgent):
    """Agent responsible for searching products across e-commerce platforms."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Product Search Agent.
        
        Args:
            config: Configuration dictionary with API keys and endpoints
        """
        super().__init__("ProductSearchAgent", config)
        self.api_keys = self.config.get("api_keys", {})
        self.timeout = self.config.get("timeout", 10)
        
        # eBay API configuration
        self.ebay_app_id = self.api_keys.get("ebay", "")
        self.ebay_finding_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        
        # Amazon PA-API configuration
        self.amazon_access_key = self.api_keys.get("amazon_access_key", "")
        self.amazon_secret_key = self.api_keys.get("amazon_secret_key", "")
        self.amazon_associate_tag = self.api_keys.get("amazon_associate_tag", "")
        self.amazon_region = self.config.get("amazon_region", "us-east-1")
        self.amazon_host = self.config.get("amazon_host", "webservices.amazon.com")
        self.use_amazon_mock = self.config.get("use_amazon_mock", True)
        
    async def _search_ebay(self, query: str, max_results: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search eBay products using eBay Finding API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Optional filters (price range, etc.)
            
        Returns:
            List of product dictionaries
        """
        if not self.ebay_app_id:
            self.logger.warning("eBay App ID not configured, skipping eBay search")
            return []
        
        try:
            # Build request parameters
            params = {
                "OPERATION-NAME": "findItemsByKeywords",
                "SERVICE-VERSION": "1.0.0",
                "SECURITY-APPNAME": self.ebay_app_id,
                "RESPONSE-DATA-FORMAT": "XML",
                "REST-PAYLOAD": "",
                "keywords": query,
                "paginationInput.entriesPerPage": str(min(max_results, 100))
            }
            
            # Add filters if provided
            if filters:
                if "min_price" in filters:
                    params["itemFilter(0).name"] = "MinPrice"
                    params["itemFilter(0).value"] = str(filters["min_price"])
                if "max_price" in filters:
                    params["itemFilter(1).name"] = "MaxPrice"
                    params["itemFilter(1).value"] = str(filters["max_price"])
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.ebay_finding_api_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_ebay_response(xml_content, max_results)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"eBay API error: {response.status} - {error_text}")
                        return []
                        
        except asyncio.TimeoutError:
            self.logger.error("eBay API timeout")
            return []
        except Exception as e:
            self.logger.error(f"Error calling eBay API: {e}")
            return []
    
    def _parse_ebay_response(self, xml_content: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Parse eBay XML response into product dictionaries.
        
        Args:
            xml_content: XML response from eBay API
            max_results: Maximum number of results to return
            
        Returns:
            List of product dictionaries
        """
        products = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Check for errors
            ack = root.find(".//{http://www.ebay.com/marketplace/search/v1/services}ack")
            if ack is not None and ack.text != "Success":
                error_message = root.find(".//{http://www.ebay.com/marketplace/search/v1/services}errorMessage")
                if error_message is not None:
                    self.logger.error(f"eBay API error: {error_message.text}")
                return []
            
            # Parse search results
            search_results = root.find(".//{http://www.ebay.com/marketplace/search/v1/services}searchResult")
            if search_results is None:
                return []
            
            items = search_results.findall(".//{http://www.ebay.com/marketplace/search/v1/services}item")
            
            for item in items[:max_results]:
                try:
                    # Extract product information
                    item_id = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}itemId")
                    title = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}title")
                    price = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}currentPrice")
                    view_item_url = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}viewItemURL")
                    gallery_url = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}galleryURL")
                    condition = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}condition")
                    seller_info = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}sellerInfo")
                    
                    # Extract shipping cost if available
                    shipping_info = item.find(".//{http://www.ebay.com/marketplace/search/v1/services}shippingInfo")
                    shipping_cost = 0.0
                    if shipping_info is not None:
                        shipping_cost_elem = shipping_info.find(".//{http://www.ebay.com/marketplace/search/v1/services}shippingServiceCost")
                        if shipping_cost_elem is not None:
                            try:
                                shipping_cost = float(shipping_cost_elem.text)
                            except (ValueError, AttributeError):
                                pass
                    
                    # Extract seller rating if available
                    seller_feedback_score = None
                    if seller_info is not None:
                        feedback_score = seller_info.find(".//{http://www.ebay.com/marketplace/search/v1/services}feedbackScore")
                        if feedback_score is not None:
                            try:
                                seller_feedback_score = int(feedback_score.text)
                            except (ValueError, AttributeError):
                                pass
                    
                    # Calculate total price
                    item_price = float(price.text) if price is not None and price.text else 0.0
                    total_price = item_price + shipping_cost
                    
                    product = {
                        "product_id": item_id.text if item_id is not None else "",
                        "name": title.text if title is not None else "Unknown Product",
                        "price": round(item_price, 2),
                        "shipping_cost": round(shipping_cost, 2),
                        "total_price": round(total_price, 2),
                        "currency": price.get("currencyId", "USD") if price is not None else "USD",
                        "retailer": "eBay",
                        "url": view_item_url.text if view_item_url is not None else "",
                        "image_url": gallery_url.text if gallery_url is not None else "",
                        "condition": condition.find(".//{http://www.ebay.com/marketplace/search/v1/services}conditionDisplayName").text if condition is not None else "Unknown",
                        "seller_feedback_score": seller_feedback_score,
                        "rating": None,  # eBay Finding API doesn't provide product ratings
                        "review_count": None  # eBay Finding API doesn't provide review counts
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing eBay item: {e}")
                    continue
            
        except ET.ParseError as e:
            self.logger.error(f"Error parsing eBay XML response: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing eBay response: {e}")
        
        return products
    
    async def _search_amazon_mock(self, query: str, max_results: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate mock Amazon product data for testing.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Optional filters (price range, etc.)
            
        Returns:
            List of mock product dictionaries
        """
        await asyncio.sleep(0.5)  # Simulate API delay
        
        # Generate mock products
        mock_products = []
        base_price = 49.99
        
        for i in range(1, max_results + 1):
            price = base_price + (i * 15) - (i % 2) * 20
            
            # Apply price filters if provided
            if filters:
                if "min_price" in filters and price < filters["min_price"]:
                    price = filters["min_price"] + 5
                if "max_price" in filters and price > filters["max_price"]:
                    price = filters["max_price"] - 5
            
            mock_products.append({
                "product_id": f"AMZ-MOCK-{i}",
                "name": f"{query} Product {i} - Amazon (Mock)",
                "price": round(price, 2),
                "shipping_cost": 0.0 if price > 25 else 5.99,
                "total_price": round(price + (0.0 if price > 25 else 5.99), 2),
                "currency": "USD",
                "retailer": "Amazon",
                "url": f"https://amazon.com/dp/MOCK{i}",
                "image_url": f"https://example.com/amazon_image_{i}.jpg",
                "condition": "New",
                "rating": round(4.0 + (i % 3) * 0.3, 1),
                "review_count": (i + 1) * 50,
                "seller_feedback_score": None
            })
        
        return mock_products
    
    def _generate_amazon_signature(self, payload: Dict[str, Any], method: str = "POST") -> Dict[str, str]:
        """
        Generate AWS Signature V4 for Amazon PA-API 5.0.
        
        Args:
            payload: Request payload
            method: HTTP method
            
        Returns:
            Dictionary with headers including authorization
        """
        import time
        
        service = "ProductAdvertisingAPI"
        endpoint = f"https://{self.amazon_host}/paapi5/searchitems"
        region = self.amazon_region
        
        # Create timestamp
        amz_date = datetime.utcnow().strftime('%Y%m%dT%H%M%S') + 'Z'
        date_stamp = datetime.utcnow().strftime('%Y%m%d')
        
        # Canonical URI
        canonical_uri = "/paapi5/searchitems"
        
        # Canonical query string (empty for POST)
        canonical_querystring = ""
        
        # Create canonical headers
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{self.amazon_host}\nx-amz-date:{amz_date}\n"
        signed_headers = "content-type;host;x-amz-date"
        
        # Create payload hash
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
        
        # Create canonical request
        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # Create string to sign
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        
        # Calculate signature
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
        k_date = sign(('AWS4' + self.amazon_secret_key).encode('utf-8'), date_stamp)
        k_region = sign(k_date, region)
        k_service = sign(k_region, service)
        k_signing = sign(k_service, 'aws4_request')
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Create authorization header
        authorization_header = (
            f"{algorithm} "
            f"Credential={self.amazon_access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        # Return headers
        return {
            "Content-Type": "application/json; charset=utf-8",
            "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
            "X-Amz-Date": amz_date,
            "Authorization": authorization_header
        }
    
    async def _search_amazon_paapi(self, query: str, max_results: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search Amazon products using PA-API 5.0.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Optional filters (price range, etc.)
            
        Returns:
            List of product dictionaries
        """
        if not all([self.amazon_access_key, self.amazon_secret_key, self.amazon_associate_tag]):
            self.logger.warning("Amazon PA-API credentials not fully configured, skipping Amazon search")
            return []
        
        try:
            # Build PA-API 5.0 request payload
            payload = {
                "PartnerType": "Associates",
                "PartnerTag": self.amazon_associate_tag,
                "Keywords": query,
                "SearchIndex": "All",
                "ItemCount": min(max_results, 10),
                "Resources": [
                    "ItemInfo.Title",
                    "ItemInfo.ByLineInfo",
                    "ItemInfo.Classifications",
                    "ItemInfo.ContentInfo",
                    "ItemInfo.ContentRating",
                    "ItemInfo.ExternalIds",
                    "ItemInfo.Features",
                    "ItemInfo.ManufactureInfo",
                    "ItemInfo.ProductInfo",
                    "ItemInfo.TechnicalInfo",
                    "ItemInfo.TradeInInfo",
                    "Offers.Listings.Price",
                    "Offers.Summaries.HighestPrice",
                    "Offers.Summaries.LowestPrice",
                    "Offers.Summaries.OfferCount",
                    "Images.Primary.Large",
                    "Images.Variants.Large",
                    "CustomerReviews.StarRating",
                    "CustomerReviews.Count"
                ]
            }
            
            # Add price filters if provided
            if filters:
                if "min_price" in filters or "max_price" in filters:
                    price_range = {}
                    if "min_price" in filters:
                        price_range["Min"] = filters["min_price"] * 100  # Convert to cents
                    if "max_price" in filters:
                        price_range["Max"] = filters["max_price"] * 100
                    payload["MinPrice"] = price_range
            
            # Generate signature and headers
            headers = self._generate_amazon_signature(payload)
            
            # Make API request
            endpoint = f"https://{self.amazon_host}/paapi5/searchitems"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_amazon_paapi_response(result)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Amazon PA-API error: {response.status} - {error_text}")
                        return []
                        
        except asyncio.TimeoutError:
            self.logger.error("Amazon PA-API timeout")
            return []
        except Exception as e:
            self.logger.error(f"Error calling Amazon PA-API: {e}")
            return []
    
    def _parse_amazon_paapi_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Amazon PA-API 5.0 JSON response into product dictionaries.
        
        Args:
            response: JSON response from Amazon PA-API
            
        Returns:
            List of product dictionaries
        """
        products = []
        
        try:
            search_result = response.get("SearchResult", {})
            items = search_result.get("Items", [])
            
            for item in items:
                try:
                    item_info = item.get("ItemInfo", {})
                    title_info = item_info.get("Title", {})
                    offers = item.get("Offers", {})
                    listings = offers.get("Listings", [])
                    images = item.get("Images", {})
                    customer_reviews = item.get("CustomerReviews", {})
                    
                    # Extract price
                    price = 0.0
                    currency = "USD"
                    if listings:
                        price_info = listings[0].get("Price", {})
                        display_amount = price_info.get("DisplayAmount", "")
                        if display_amount:
                            try:
                                # Extract numeric value from string like "$29.99"
                                price = float(display_amount.replace("$", "").replace(",", ""))
                            except (ValueError, AttributeError):
                                pass
                        currency = price_info.get("Currency", "USD")
                    
                    # Extract rating and review count
                    rating = None
                    review_count = None
                    if customer_reviews:
                        star_rating = customer_reviews.get("StarRating", {})
                        if star_rating:
                            rating = star_rating.get("Value", None)
                        review_count = customer_reviews.get("Count", None)
                    
                    # Extract image URL
                    image_url = ""
                    if images:
                        primary = images.get("Primary", {})
                        if primary:
                            large = primary.get("Large", {})
                            if large:
                                image_url = large.get("URL", "")
                    
                    product = {
                        "product_id": item.get("ASIN", ""),
                        "name": title_info.get("DisplayValue", "Unknown Product"),
                        "price": round(price, 2),
                        "shipping_cost": 0.0,  # Amazon Prime items typically have free shipping
                        "total_price": round(price, 2),
                        "currency": currency,
                        "retailer": "Amazon",
                        "url": item.get("DetailPageURL", ""),
                        "image_url": image_url,
                        "condition": "New",
                        "rating": round(rating, 1) if rating else None,
                        "review_count": review_count,
                        "seller_feedback_score": None
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing Amazon item: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Amazon PA-API response: {e}")
        
        return products
    
    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute product search across multiple e-commerce platforms.
        
        Args:
            query: Dictionary containing:
                - search_term: Product name or description to search
                - max_results: Maximum number of results per platform (default: 5)
                - platforms: List of platforms to search (default: ["ebay", "amazon"])
                - filters: Optional filters dictionary:
                    - min_price: Minimum price filter
                    - max_price: Maximum price filter
                
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - products: List of product dictionaries
                - total_results: Total number of products found
                - platforms_searched: List of platforms that were queried
                - search_term: Original search term
        """
        required_fields = ["search_term"]
        if not self.validate_input(query, required_fields):
            return {
                "success": False,
                "error": "Missing required field: search_term",
                "products": [],
                "total_results": 0,
                "platforms_searched": []
            }
        
        search_term = query.get("search_term")
        max_results = query.get("max_results", 5)
        platforms = query.get("platforms", ["ebay", "amazon"])
        filters = query.get("filters", {})
        
        self.logger.info(f"Searching for '{search_term}' across {platforms}")
        
        products = []
        platforms_searched = []
        
        # Search each platform concurrently
        tasks = []
        
        if "ebay" in platforms:
            tasks.append(("ebay", self._search_ebay(search_term, max_results, filters)))
            platforms_searched.append("ebay")
        
        if "amazon" in platforms:
            # Try real Amazon PA-API first, fallback to mock if not configured
            if all([self.amazon_access_key, self.amazon_secret_key, self.amazon_associate_tag]):
                tasks.append(("amazon", self._search_amazon_paapi(search_term, max_results, filters)))
                platforms_searched.append("amazon")
            elif self.use_amazon_mock:
                tasks.append(("amazon", self._search_amazon_mock(search_term, max_results, filters)))
                platforms_searched.append("amazon")
        
        try:
            # Execute searches concurrently
            results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            
            for (platform, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error searching {platform}: {result}")
                    continue
                products.extend(result)
            
            self.logger.info(f"Found {len(products)} products from {len(platforms_searched)} platform(s)")
            
            return {
                "success": True,
                "products": products,
                "total_results": len(products),
                "platforms_searched": platforms_searched,
                "search_term": search_term
            }
            
        except Exception as e:
            self.logger.error(f"Error executing product search: {e}")
            return {
                "success": False,
                "error": str(e),
                "products": [],
                "total_results": 0,
                "platforms_searched": platforms_searched
            }
