"""
Price Comparison API Agent
Compares prices across multiple retailers and tracks price history.
"""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class PriceComparisonAgent(BaseAgent):
    """Agent responsible for comparing prices across retailers and tracking price history."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Price Comparison Agent.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        super().__init__("PriceComparisonAgent", config)
        self.api_keys = self.config.get("api_keys", {})
        self.timeout = self.config.get("timeout", 10)
        
        # In-memory price history (in production, use a database)
        self.price_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Price comparison API configuration
        self.use_priceapi = self.config.get("use_priceapi", False)
        self.priceapi_key = self.api_keys.get("priceapi", "")
        
        # Google Custom Search API (for Google Shopping)
        self.google_api_key = self.api_keys.get("google_api_key", "")
        self.google_cx = self.config.get("google_cx", "")  # Custom Search Engine ID
        self.use_google_shopping = self.config.get("use_google_shopping", False)
        
    async def _get_prices_from_product_search(self, product_name: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract price information from product search results.
        
        Args:
            product_name: Name of the product to compare
            products: List of products from ProductSearchAgent
            
        Returns:
            List of price comparison dictionaries
        """
        prices = []
        
        for product in products:
            # Group by retailer and find best price per retailer
            retailer = product.get("retailer", "Unknown")
            price = product.get("total_price", product.get("price", 0))
            shipping_cost = product.get("shipping_cost", 0)
            
            price_data = {
                "retailer": retailer,
                "price": round(product.get("price", price), 2),
                "shipping_cost": round(shipping_cost, 2),
                "total_cost": round(price, 2),
                "currency": product.get("currency", "USD"),
                "product_id": product.get("product_id", ""),
                "product_name": product.get("name", product_name),
                "url": product.get("url", ""),
                "availability": "In Stock",  # Default assumption
                "last_updated": datetime.now().isoformat(),
                "rating": product.get("rating"),
                "review_count": product.get("review_count")
            }
            
            prices.append(price_data)
        
        return prices
    
    async def _get_prices_from_google_shopping(self, product_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get prices from Google Shopping via Google Custom Search API.
        
        Args:
            product_name: Name of the product to search
            max_results: Maximum number of results to return
            
        Returns:
            List of price comparison dictionaries
        """
        if not self.google_api_key or not self.google_cx:
            self.logger.warning("Google API key or CX not configured, skipping Google Shopping")
            return []
        
        try:
            # Google Custom Search API endpoint
            url = "https://www.googleapis.com/customsearch/v1"
            
            params = {
                "key": self.google_api_key,
                "cx": self.google_cx,
                "q": product_name,
                "num": min(max_results, 10),  # Max 10 per request
                "safe": "off"
            }
            
            # Add site restriction for shopping results
            # Google Shopping results typically come from shopping.google.com
            params["siteSearch"] = "shopping.google.com"
            params["siteSearchFilter"] = "i"  # Include results from this site
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_google_shopping_response(result)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Google Shopping API error: {response.status} - {error_text}")
                        return []
                        
        except asyncio.TimeoutError:
            self.logger.error("Google Shopping API timeout")
            return []
        except Exception as e:
            self.logger.error(f"Error calling Google Shopping API: {e}")
            return []
    
    def _parse_google_shopping_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Google Custom Search API response for Shopping results.
        
        Args:
            response: JSON response from Google Custom Search API
            
        Returns:
            List of price comparison dictionaries
        """
        prices = []
        
        try:
            items = response.get("items", [])
            
            for item in items:
                try:
                    # Extract product information from Google Shopping results
                    title = item.get("title", "")
                    link = item.get("link", "")
                    snippet = item.get("snippet", "")
                    
                    # Try to extract price from snippet or title
                    # Google Shopping snippets often contain price information
                    price = self._extract_price_from_text(snippet + " " + title)
                    
                    # Extract retailer from display link or snippet
                    display_link = item.get("displayLink", "")
                    retailer = self._extract_retailer_from_link(link, display_link)
                    
                    if price > 0:  # Only add if we found a valid price
                        price_data = {
                            "retailer": retailer,
                            "price": round(price, 2),
                            "shipping_cost": 0.0,  # Google Shopping doesn't always provide shipping
                            "total_cost": round(price, 2),
                            "currency": "USD",
                            "product_id": item.get("cacheId", ""),
                            "product_name": title,
                            "url": link,
                            "availability": "In Stock",  # Default assumption
                            "last_updated": datetime.now().isoformat(),
                            "rating": None,  # Google Shopping API doesn't provide ratings
                            "review_count": None
                        }
                        
                        prices.append(price_data)
                        
                except Exception as e:
                    self.logger.warning(f"Error parsing Google Shopping item: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Google Shopping response: {e}")
        
        return prices
    
    def _extract_price_from_text(self, text: str) -> float:
        """
        Extract price from text (snippet or title).
        
        Args:
            text: Text that may contain price information
            
        Returns:
            Extracted price as float, or 0.0 if not found
        """
        import re
        
        # Common price patterns: $29.99, $1,234.56, 29.99 USD, etc.
        patterns = [
            r'\$[\d,]+\.?\d*',  # $29.99 or $1,234.56
            r'[\d,]+\.?\d*\s*(?:USD|dollars?)',  # 29.99 USD
            r'Price[:\s]+\$?([\d,]+\.?\d*)',  # Price: $29.99
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Get the first match and extract numeric value
                price_str = matches[0].replace('$', '').replace(',', '').strip()
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_retailer_from_link(self, link: str, display_link: str) -> str:
        """
        Extract retailer name from URL.
        
        Args:
            link: Full URL
            display_link: Display link from Google
            
        Returns:
            Retailer name
        """
        # Use display link if available
        if display_link:
            # Remove common prefixes
            retailer = display_link.replace("www.", "").split(".")[0]
            return retailer.capitalize()
        
        # Extract from full URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(link)
            domain = parsed.netloc.replace("www.", "")
            retailer = domain.split(".")[0]
            return retailer.capitalize()
        except Exception:
            return "Google Shopping"
    
    async def _get_prices_from_priceapi(self, product_name: str) -> List[Dict[str, Any]]:
        """
        Get prices from PriceAPI service (if configured).
        
        Args:
            product_name: Name of the product to compare
            
        Returns:
            List of price comparison dictionaries
        """
        if not self.priceapi_key:
            self.logger.warning("PriceAPI key not configured, skipping PriceAPI")
            return []
        
        try:
            # PriceAPI uses a job-based async API
            # First, create a job
            create_job_url = "https://api.priceapi.com/v2/jobs"
            headers = {
                "Authorization": f"Bearer {self.priceapi_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "token": self.priceapi_key,
                "source": "google_shopping",
                "country": "us",
                "topic": "search_results",
                "key": "term",
                "values": [product_name],
                "max_pages": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    create_job_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        job_data = await response.json()
                        job_id = job_data.get("job_id")
                        
                        if job_id:
                            # Poll for results (simplified - in production, use proper polling)
                            await asyncio.sleep(2)  # Wait for job to process
                            
                            results_url = f"https://api.priceapi.com/v2/jobs/{job_id}/download"
                            async with session.get(
                                results_url,
                                headers=headers,
                                timeout=aiohttp.ClientTimeout(total=self.timeout)
                            ) as results_response:
                                if results_response.status == 200:
                                    results = await results_response.json()
                                    return self._parse_priceapi_response(results)
                    
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error calling PriceAPI: {e}")
            return []
    
    def _parse_priceapi_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse PriceAPI response into price comparison format.
        
        Args:
            response: JSON response from PriceAPI
            
        Returns:
            List of price comparison dictionaries
        """
        prices = []
        
        try:
            # PriceAPI response structure varies, this is a generic parser
            results = response.get("results", [])
            
            for item in results:
                price_data = {
                    "retailer": item.get("merchant", "Unknown"),
                    "price": float(item.get("price", 0)),
                    "shipping_cost": float(item.get("shipping", 0)),
                    "total_cost": float(item.get("price", 0)) + float(item.get("shipping", 0)),
                    "currency": item.get("currency", "USD"),
                    "product_id": item.get("id", ""),
                    "product_name": item.get("title", ""),
                    "url": item.get("link", ""),
                    "availability": item.get("availability", "In Stock"),
                    "last_updated": datetime.now().isoformat()
                }
                prices.append(price_data)
                
        except Exception as e:
            self.logger.error(f"Error parsing PriceAPI response: {e}")
        
        return prices
    
    def _update_price_history(self, product_name: str, prices: List[Dict[str, Any]]) -> None:
        """
        Update price history for a product.
        
        Args:
            product_name: Name of the product
            prices: List of price data dictionaries
        """
        if product_name not in self.price_history:
            self.price_history[product_name] = []
        
        for price_data in prices:
            history_entry = {
                "retailer": price_data["retailer"],
                "price": price_data["price"],
                "total_cost": price_data["total_cost"],
                "timestamp": datetime.now().isoformat()
            }
            self.price_history[product_name].append(history_entry)
            
            # Keep only last 30 days of history
            cutoff_date = datetime.now() - timedelta(days=30)
            self.price_history[product_name] = [
                entry for entry in self.price_history[product_name]
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
            ]
    
    def _calculate_price_trend(self, product_name: str, retailer: str) -> Dict[str, Any]:
        """
        Calculate price trend for a product from a specific retailer.
        
        Args:
            product_name: Name of the product
            retailer: Name of the retailer
            
        Returns:
            Dictionary with trend information
        """
        if product_name not in self.price_history:
            return {"trend": "no_data", "change_percent": 0.0}
        
        retailer_history = [
            entry for entry in self.price_history[product_name]
            if entry["retailer"] == retailer
        ]
        
        if len(retailer_history) < 2:
            return {"trend": "insufficient_data", "change_percent": 0.0}
        
        # Get oldest and newest prices
        sorted_history = sorted(
            retailer_history,
            key=lambda x: x["timestamp"]
        )
        oldest_price = sorted_history[0]["total_cost"]
        newest_price = sorted_history[-1]["total_cost"]
        
        change_percent = ((newest_price - oldest_price) / oldest_price) * 100 if oldest_price > 0 else 0
        
        if change_percent > 5:
            trend = "increasing"
        elif change_percent < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "oldest_price": round(oldest_price, 2),
            "newest_price": round(newest_price, 2),
            "data_points": len(retailer_history)
        }
    
    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute price comparison across retailers.
        
        Args:
            query: Dictionary containing:
                - product_name: Name of the product to compare (required)
                - products: Optional list of products from ProductSearchAgent
                - retailers: List of retailer names to compare (optional)
                - include_history: Whether to include price history (default: False)
                - use_google_shopping: Whether to use Google Shopping API (default: False)
                - use_priceapi: Whether to use PriceAPI service (default: False)
                - max_results: Maximum results from Google Shopping (default: 10)
                
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - comparisons: List of price comparisons per retailer
                - best_deal: Information about the best price
                - price_trends: Price trend analysis (if include_history is True)
        """
        required_fields = ["product_name"]
        if not self.validate_input(query, required_fields):
            return {
                "success": False,
                "error": "Missing required field: product_name",
                "comparisons": []
            }
        
        product_name = query.get("product_name")
        products = query.get("products", [])
        include_history = query.get("include_history", False)
        use_priceapi = query.get("use_priceapi", self.use_priceapi)
        
        self.logger.info(f"Comparing prices for '{product_name}'")
        
        try:
            # Get prices from different sources
            all_prices = []
            
            # Method 1: Use products from ProductSearchAgent if provided
            if products:
                prices_from_products = await self._get_prices_from_product_search(product_name, products)
                all_prices.extend(prices_from_products)
                self.logger.info(f"Got {len(prices_from_products)} prices from product search")
            
            # Method 2: Use Google Shopping API if configured and requested
            use_google = query.get("use_google_shopping", self.use_google_shopping)
            if use_google and self.google_api_key and self.google_cx:
                max_results = query.get("max_results", 10)
                prices_from_google = await self._get_prices_from_google_shopping(product_name, max_results)
                all_prices.extend(prices_from_google)
                self.logger.info(f"Got {len(prices_from_google)} prices from Google Shopping")
            
            # Method 3: Use PriceAPI if configured and requested
            if use_priceapi and self.priceapi_key:
                prices_from_api = await self._get_prices_from_priceapi(product_name)
                all_prices.extend(prices_from_api)
                self.logger.info(f"Got {len(prices_from_api)} prices from PriceAPI")
            
            # If no prices found, return error
            if not all_prices:
                return {
                    "success": False,
                    "error": "No price data available. Provide products from ProductSearchAgent, configure Google Shopping API, or configure PriceAPI.",
                    "comparisons": []
                }
            
            # Update price history
            self._update_price_history(product_name, all_prices)
            
            # Group by retailer and find best price per retailer
            retailer_prices: Dict[str, List[Dict[str, Any]]] = {}
            for price_data in all_prices:
                retailer = price_data["retailer"]
                if retailer not in retailer_prices:
                    retailer_prices[retailer] = []
                retailer_prices[retailer].append(price_data)
            
            # Find best deal per retailer (lowest total cost)
            comparisons = []
            for retailer, prices in retailer_prices.items():
                best_price = min(prices, key=lambda x: x["total_cost"])
                
                comparison = {
                    "retailer": retailer,
                    "price": best_price["price"],
                    "shipping_cost": best_price["shipping_cost"],
                    "total_cost": round(best_price["total_cost"], 2),
                    "currency": best_price["currency"],
                    "product_id": best_price.get("product_id", ""),
                    "product_name": best_price.get("product_name", product_name),
                    "url": best_price.get("url", ""),
                    "availability": best_price.get("availability", "In Stock"),
                    "last_updated": best_price["last_updated"],
                    "rating": best_price.get("rating"),
                    "review_count": best_price.get("review_count"),
                    "options_count": len(prices)  # Number of options from this retailer
                }
                
                if include_history:
                    trend = self._calculate_price_trend(product_name, retailer)
                    comparison["price_trend"] = trend
                
                comparisons.append(comparison)
            
            # Find overall best deal (lowest total cost)
            if comparisons:
                best_deal = min(comparisons, key=lambda x: x["total_cost"])
                
                # Calculate savings compared to highest price
                highest_price = max(comparisons, key=lambda x: x["total_cost"])
                savings = round(highest_price["total_cost"] - best_deal["total_cost"], 2)
                savings_percent = round((savings / highest_price["total_cost"]) * 100, 2) if highest_price["total_cost"] > 0 else 0
                
                result = {
                    "success": True,
                    "product_name": product_name,
                    "comparisons": comparisons,
                    "best_deal": {
                        "retailer": best_deal["retailer"],
                        "total_cost": best_deal["total_cost"],
                        "price": best_deal["price"],
                        "shipping_cost": best_deal["shipping_cost"],
                        "savings": savings,
                        "savings_percent": savings_percent,
                        "url": best_deal["url"],
                        "product_name": best_deal["product_name"]
                    },
                    "comparison_date": datetime.now().isoformat(),
                    "total_retailers": len(comparisons)
                }
                
                self.logger.info(f"Best deal found: {best_deal['retailer']} at ${best_deal['total_cost']:.2f}")
                
                return result
            else:
                return {
                    "success": False,
                    "error": "No price comparisons available",
                    "comparisons": []
                }
            
        except Exception as e:
            self.logger.error(f"Error executing price comparison: {e}")
            return {
                "success": False,
                "error": str(e),
                "comparisons": []
            }
