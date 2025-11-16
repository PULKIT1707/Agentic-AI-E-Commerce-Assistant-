"""
Centralized Workflow Manager
Orchestrates all agents to facilitate communication and execute the complete e-commerce assistant workflow.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from .product_search_agent import ProductSearchAgent
from .price_comparison_agent import PriceComparisonAgent
from .review_analysis_agent import ReviewAnalysisAgent
from .recommendation_engine_agent import RecommendationEngineAgent

logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Centralized workflow manager that orchestrates all agents.
    Facilitates communication between agents and manages the complete workflow.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Workflow Manager with all agents.
        
        Args:
            config: Configuration dictionary containing agent configurations
        """
        if config is None:
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
            except FileNotFoundError:
                logger.warning("config.json not found. Using default configuration.")
                config = {}
        
        self.config = config
        agent_configs = config.get("agents", {})
        
        # Initialize all agents
        self.search_agent = ProductSearchAgent(
            agent_configs.get("product_search", {})
        )
        self.comparison_agent = PriceComparisonAgent(
            agent_configs.get("price_comparison", {})
        )
        self.review_agent = ReviewAnalysisAgent(
            agent_configs.get("review_analysis", {})
        )
        self.recommendation_agent = RecommendationEngineAgent(
            agent_configs.get("recommendation_engine", {})
        )
        
        self.logger = logging.getLogger(f"{__name__}.WorkflowManager")
    
    async def execute_workflow(
        self,
        user_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow: Search → Compare → Analyze → Recommend.
        
        Args:
            user_query: Dictionary containing:
                - search_term: Product name or description to search (required)
                - max_results: Maximum number of results (default: 10)
                - platforms: List of platforms to search (default: ["ebay", "amazon"])
                - filters: Optional filters dictionary:
                    - min_price: Minimum price filter
                    - max_price: Maximum price filter
                - user_preferences: Dictionary with user preferences:
                    - budget: Maximum budget (optional)
                    - min_rating: Minimum rating threshold (optional)
                    - max_recommendations: Maximum number of recommendations (default: 5)
                - include_price_comparison: Whether to compare prices (default: True)
                - include_review_analysis: Whether to analyze reviews (default: True)
                - use_google_shopping: Whether to use Google Shopping API (default: False)
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating overall success
                - workflow_steps: Dictionary with results from each step
                - recommendations: Final recommendations (if successful)
                - summary: Summary of the workflow execution
                - error: Error message (if failed)
        """
        workflow_result = {
            "success": False,
            "workflow_steps": {},
            "recommendations": [],
            "summary": {},
            "error": None
        }
        
        try:
            # Validate required fields
            if "search_term" not in user_query:
                workflow_result["error"] = "Missing required field: search_term"
                return workflow_result
            
            search_term = user_query.get("search_term")
            max_results = user_query.get("max_results", 10)
            platforms = user_query.get("platforms", ["ebay", "amazon"])
            filters = user_query.get("filters", {})
            user_preferences = user_query.get("user_preferences", {})
            include_price_comparison = user_query.get("include_price_comparison", True)
            include_review_analysis = user_query.get("include_review_analysis", True)
            use_google_shopping = user_query.get("use_google_shopping", False)
            
            self.logger.info(f"Starting workflow for search term: '{search_term}'")
            
            # Step 1: Product Search
            self.logger.info("Step 1: Executing Product Search Agent")
            search_query = {
                "search_term": search_term,
                "max_results": max_results,
                "platforms": platforms,
                "filters": filters
            }
            
            search_result = await self.search_agent.execute(search_query)
            workflow_result["workflow_steps"]["product_search"] = search_result
            
            if not search_result.get("success") or not search_result.get("products"):
                workflow_result["error"] = "Product search failed or no products found"
                workflow_result["summary"] = {
                    "step": "product_search",
                    "message": "No products found matching the search criteria"
                }
                return workflow_result
            
            products = search_result["products"]
            self.logger.info(f"Found {len(products)} products")
            
            # Step 2: Price Comparison (if enabled)
            price_comparisons = {}
            if include_price_comparison:
                self.logger.info("Step 2: Executing Price Comparison Agent")
                comparison_query = {
                    "product_name": search_term,
                    "products": products,
                    "include_history": False,
                    "use_google_shopping": use_google_shopping
                }
                
                comparison_result = await self.comparison_agent.execute(comparison_query)
                workflow_result["workflow_steps"]["price_comparison"] = comparison_result
                
                if comparison_result.get("success"):
                    # Map price comparisons by product_id
                    for comp in comparison_result.get("comparisons", []):
                        product_id = comp.get("product_id", "")
                        if product_id:
                            price_comparisons[product_id] = comp
                    self.logger.info(f"Compared prices for {len(price_comparisons)} products")
                else:
                    self.logger.warning("Price comparison failed, continuing without price data")
            else:
                self.logger.info("Step 2: Skipping Price Comparison")
                workflow_result["workflow_steps"]["price_comparison"] = {
                    "success": False,
                    "skipped": True
                }
            
            # Step 3: Review Analysis (if enabled)
            review_analyses = {}
            if include_review_analysis:
                self.logger.info("Step 3: Executing Review Analysis Agent")
                
                # Extract reviews from products (if available)
                # In production, reviews would come from product search results
                # For now, we'll generate mock reviews based on product ratings
                reviews_by_product = self._extract_reviews_from_products(products)
                
                # Analyze reviews for each product concurrently
                review_tasks = []
                for product_id, reviews in reviews_by_product.items():
                    if reviews:
                        review_tasks.append(
                            self._analyze_product_reviews(product_id, reviews)
                        )
                
                if review_tasks:
                    review_results = await asyncio.gather(*review_tasks, return_exceptions=True)
                    
                    for result in review_results:
                        if isinstance(result, Exception):
                            self.logger.error(f"Review analysis error: {result}")
                            continue
                        if result.get("success"):
                            product_id = result.get("product_id")
                            review_analyses[product_id] = result
                    
                    self.logger.info(f"Analyzed reviews for {len(review_analyses)} products")
                else:
                    self.logger.warning("No reviews found for analysis")
                
                workflow_result["workflow_steps"]["review_analysis"] = {
                    "success": len(review_analyses) > 0,
                    "products_analyzed": len(review_analyses)
                }
            else:
                self.logger.info("Step 3: Skipping Review Analysis")
                workflow_result["workflow_steps"]["review_analysis"] = {
                    "success": False,
                    "skipped": True
                }
            
            # Step 4: Generate Recommendations
            self.logger.info("Step 4: Executing Recommendation Engine Agent")
            recommendation_query = {
                "products": products,
                "price_comparisons": price_comparisons,
                "review_analyses": review_analyses,
                "user_preferences": user_preferences,
                "max_recommendations": user_preferences.get("max_recommendations", 5)
            }
            
            recommendation_result = await self.recommendation_agent.execute(recommendation_query)
            workflow_result["workflow_steps"]["recommendation"] = recommendation_result
            
            if recommendation_result.get("success"):
                workflow_result["success"] = True
                workflow_result["recommendations"] = recommendation_result.get("recommendations", [])
                workflow_result["summary"] = recommendation_result.get("summary", {})
                workflow_result["summary"]["workflow_completed"] = True
                workflow_result["summary"]["total_products_found"] = len(products)
                workflow_result["summary"]["price_comparisons_count"] = len(price_comparisons)
                workflow_result["summary"]["review_analyses_count"] = len(review_analyses)
                
                self.logger.info(
                    f"Workflow completed successfully. "
                    f"Generated {len(workflow_result['recommendations'])} recommendations"
                )
            else:
                workflow_result["error"] = recommendation_result.get("error", "Recommendation generation failed")
                workflow_result["summary"] = {
                    "step": "recommendation",
                    "message": "Failed to generate recommendations"
                }
            
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}", exc_info=True)
            workflow_result["error"] = str(e)
            workflow_result["summary"] = {
                "error": str(e),
                "workflow_failed": True
            }
            return workflow_result
    
    def _extract_reviews_from_products(self, products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract or generate reviews from products.
        In production, reviews would come from product search results.
        
        Args:
            products: List of product dictionaries
        
        Returns:
            Dictionary mapping product_id to list of reviews
        """
        reviews_by_product = {}
        
        for product in products:
            product_id = product.get("product_id", "")
            rating = product.get("rating", 4.0)
            
            # Generate mock reviews based on rating
            # In production, these would come from the product search API
            reviews = []
            if rating >= 4.5:
                reviews = [
                    {"text": "Excellent product! Highly recommend!", "rating": 5},
                    {"text": "Great quality and fast shipping. Love it!", "rating": 5},
                    {"text": "Amazing value for money. Very satisfied!", "rating": 5},
                    {"text": "Perfect! Exceeded my expectations.", "rating": 5},
                    {"text": "Good product, works as expected.", "rating": 4}
                ]
            elif rating >= 4.0:
                reviews = [
                    {"text": "Good product, worth the price.", "rating": 4},
                    {"text": "Decent quality, works fine.", "rating": 4},
                    {"text": "Nice product but could be better.", "rating": 3},
                    {"text": "Satisfied with the purchase.", "rating": 4},
                    {"text": "It's okay, nothing special.", "rating": 3}
                ]
            else:
                reviews = [
                    {"text": "Not great quality, disappointed.", "rating": 2},
                    {"text": "Poor build quality, broke quickly.", "rating": 2},
                    {"text": "Not worth the money.", "rating": 2},
                    {"text": "Terrible product, avoid this.", "rating": 1},
                    {"text": "Very disappointed with this purchase.", "rating": 2}
                ]
            
            if product_id:
                reviews_by_product[product_id] = reviews
        
        return reviews_by_product
    
    async def _analyze_product_reviews(
        self,
        product_id: str,
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze reviews for a single product.
        
        Args:
            product_id: Product identifier
            reviews: List of review dictionaries
        
        Returns:
            Review analysis result dictionary with product_id
        """
        review_result = await self.review_agent.execute({
            "reviews": reviews,
            "extract_themes": True
        })
        
        review_result["product_id"] = product_id
        return review_result
    
    async def search_products_only(
        self,
        search_term: str,
        max_results: int = 10,
        platforms: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute only the product search step.
        
        Args:
            search_term: Product name or description to search
            max_results: Maximum number of results
            platforms: List of platforms to search
            filters: Optional price filters
        
        Returns:
            Product search result dictionary
        """
        query = {
            "search_term": search_term,
            "max_results": max_results,
            "platforms": platforms or ["ebay", "amazon"],
            "filters": filters or {}
        }
        return await self.search_agent.execute(query)
    
    async def compare_prices_only(
        self,
        product_name: str,
        products: List[Dict[str, Any]],
        use_google_shopping: bool = False
    ) -> Dict[str, Any]:
        """
        Execute only the price comparison step.
        
        Args:
            product_name: Name of the product
            products: List of products from search
            use_google_shopping: Whether to use Google Shopping API
        
        Returns:
            Price comparison result dictionary
        """
        query = {
            "product_name": product_name,
            "products": products,
            "include_history": False,
            "use_google_shopping": use_google_shopping
        }
        return await self.comparison_agent.execute(query)
    
    async def analyze_reviews_only(
        self,
        reviews: List[Dict[str, Any]],
        extract_themes: bool = True
    ) -> Dict[str, Any]:
        """
        Execute only the review analysis step.
        
        Args:
            reviews: List of review dictionaries
            extract_themes: Whether to extract themes
        
        Returns:
            Review analysis result dictionary
        """
        query = {
            "reviews": reviews,
            "extract_themes": extract_themes
        }
        return await self.review_agent.execute(query)
    
    async def generate_recommendations_only(
        self,
        products: List[Dict[str, Any]],
        price_comparisons: Optional[Dict[str, Any]] = None,
        review_analyses: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        max_recommendations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute only the recommendation generation step.
        
        Args:
            products: List of products
            price_comparisons: Price comparison data
            review_analyses: Review analysis data
            user_preferences: User preferences
            max_recommendations: Maximum number of recommendations
        
        Returns:
            Recommendation result dictionary
        """
        query = {
            "products": products,
            "price_comparisons": price_comparisons or {},
            "review_analyses": review_analyses or {},
            "user_preferences": user_preferences or {},
            "max_recommendations": max_recommendations
        }
        return await self.recommendation_agent.execute(query)

