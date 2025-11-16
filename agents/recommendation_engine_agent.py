"""
Recommendation Engine Agent
Synthesizes information from other agents to generate personalized product recommendations.
"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import logging
import math

logger = logging.getLogger(__name__)


class RecommendationEngineAgent(BaseAgent):
    """Agent responsible for synthesizing recommendations from multiple data sources."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Recommendation Engine Agent.
        
        Args:
            config: Configuration dictionary with weights and preferences
        """
        super().__init__("RecommendationEngineAgent", config)
        
        # Weights for different factors in recommendation scoring
        self.weights = self.config.get("weights", {
            "price": 0.3,
            "sentiment": 0.4,
            "rating": 0.2,
            "review_count": 0.1
        })
        self.budget_weight = self.config.get("budget_weight", 0.5)
        
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a value to 0-1 range.
        
        Args:
            value: Value to normalize
            min_val: Minimum value in range
            max_val: Maximum value in range
            
        Returns:
            Normalized value between 0 and 1
        """
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    def _calculate_product_score(
        self,
        product: Dict[str, Any],
        price_data: Optional[Dict[str, Any]],
        review_data: Optional[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> float:
        """
        Calculate a recommendation score for a product.
        
        Args:
            product: Product information dictionary
            price_data: Price comparison data for the product
            review_data: Review analysis data for the product
            user_preferences: User preferences including budget
            
        Returns:
            Recommendation score (0-1, higher is better)
        """
        score = 0.0
        
        # Price score (lower price = higher score, but within budget)
        if price_data:
            price = price_data.get("total_cost", product.get("price", 0))
            budget = user_preferences.get("budget", float('inf'))
            
            if price <= budget:
                # Normalize price score (lower is better)
                max_price = user_preferences.get("max_price", budget * 1.5)
                price_score = 1.0 - self._normalize_score(price, 0, max_price)
                score += self.weights["price"] * price_score
            else:
                # Penalty for exceeding budget
                score -= 0.2
        
        # Sentiment score
        if review_data:
            sentiment_summary = review_data.get("sentiment_summary", {})
            avg_sentiment = sentiment_summary.get("average_sentiment_score", 0.5)
            positive_percent = sentiment_summary.get("positive_percent", 50) / 100.0
            
            sentiment_score = (avg_sentiment + positive_percent) / 2.0
            score += self.weights["sentiment"] * sentiment_score
        
        # Rating score
        rating = product.get("rating", 0)
        if rating > 0:
            rating_score = self._normalize_score(rating, 0, 5.0)
            score += self.weights["rating"] * rating_score
        
        # Review count score (more reviews = more reliable)
        review_count = product.get("review_count", 0)
        if review_count > 0:
            # Normalize review count (log scale for diminishing returns)
            review_score = min(math.log10(review_count + 1) / 3.0, 1.0)
            score += self.weights["review_count"] * review_score
        
        # Apply budget constraint multiplier
        if price_data:
            price = price_data.get("total_cost", product.get("price", 0))
            budget = user_preferences.get("budget", float('inf'))
            if price <= budget:
                score *= (1.0 + self.budget_weight)
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def _generate_recommendation_reason(
        self,
        product: Dict[str, Any],
        price_data: Optional[Dict[str, Any]],
        review_data: Optional[Dict[str, Any]],
        score: float
    ) -> str:
        """
        Generate a human-readable reason for the recommendation.
        
        Args:
            product: Product information
            price_data: Price comparison data
            review_data: Review analysis data
            score: Recommendation score
            
        Returns:
            Human-readable reason string
        """
        reasons = []
        
        if price_data:
            best_deal = price_data.get("best_deal", {})
            if best_deal.get("retailer") == product.get("retailer"):
                reasons.append(f"Best price available at ${best_deal.get('total_cost', 0):.2f}")
            elif price_data.get("total_cost", 0) < product.get("price", 0) * 1.1:
                reasons.append(f"Competitive pricing at ${price_data.get('total_cost', 0):.2f}")
        
        if review_data:
            sentiment_summary = review_data.get("sentiment_summary", {})
            overall_sentiment = sentiment_summary.get("overall_sentiment", "NEUTRAL")
            if overall_sentiment == "POSITIVE":
                positive_percent = sentiment_summary.get("positive_percent", 0)
                reasons.append(f"Highly positive reviews ({positive_percent:.1f}% positive)")
            elif overall_sentiment == "NEGATIVE":
                reasons.append("Mixed reviews")
        
        rating = product.get("rating", 0)
        if rating >= 4.5:
            reasons.append(f"Excellent rating ({rating:.1f}/5.0)")
        elif rating >= 4.0:
            reasons.append(f"Good rating ({rating:.1f}/5.0)")
        
        review_count = product.get("review_count", 0)
        if review_count > 100:
            reasons.append(f"Highly reviewed ({review_count} reviews)")
        elif review_count > 50:
            reasons.append(f"Well-reviewed ({review_count} reviews)")
        
        if not reasons:
            reasons.append("Meets basic requirements")
        
        return "; ".join(reasons)
    
    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized product recommendations.
        
        Args:
            query: Dictionary containing:
                - products: List of products from ProductSearchAgent (required)
                - price_comparisons: Price comparison data (optional)
                    Dictionary mapping product_id or product_name to price data
                - review_analyses: Review analysis data (optional)
                    Dictionary mapping product_id or product_name to review data
                - user_preferences: Dictionary with user preferences:
                    - budget: Maximum budget (optional)
                    - max_price: Maximum price for normalization (optional)
                    - min_rating: Minimum rating threshold (optional)
                - max_recommendations: Maximum number of recommendations (default: 5)
                
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - recommendations: List of recommended products with scores
                - summary: Summary of recommendations
        """
        required_fields = ["products"]
        if not self.validate_input(query, required_fields):
            return {
                "success": False,
                "error": "Missing required field: products",
                "recommendations": []
            }
        
        products = query.get("products", [])
        price_comparisons = query.get("price_comparisons", {})
        review_analyses = query.get("review_analyses", {})
        user_preferences = query.get("user_preferences", {})
        max_recommendations = query.get("max_recommendations", 5)
        
        if not products:
            return {
                "success": False,
                "error": "No products provided",
                "recommendations": []
            }
        
        self.logger.info(f"Generating recommendations from {len(products)} products")
        
        try:
            # Score each product
            scored_products = []
            
            for product in products:
                product_id = product.get("product_id", "")
                product_name = product.get("name", "")
                
                # Get related price and review data
                price_data = price_comparisons.get(product_id) or price_comparisons.get(product_name)
                review_data = review_analyses.get(product_id) or review_analyses.get(product_name)
                
                # Calculate recommendation score
                score = self._calculate_product_score(
                    product,
                    price_data,
                    review_data,
                    user_preferences
                )
                
                # Apply filters
                min_rating = user_preferences.get("min_rating", 0)
                if product.get("rating", 0) < min_rating:
                    continue
                
                # Generate recommendation reason
                reason = self._generate_recommendation_reason(
                    product,
                    price_data,
                    review_data,
                    score
                )
                
                recommendation = {
                    "product": product,
                    "score": round(score, 3),
                    "reason": reason,
                    "price_data": price_data,
                    "review_data": review_data
                }
                
                scored_products.append(recommendation)
            
            # Sort by score (descending)
            scored_products.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top recommendations
            recommendations = scored_products[:max_recommendations]
            
            # Generate summary
            if recommendations:
                avg_score = sum(r["score"] for r in recommendations) / len(recommendations)
                price_range = []
                for rec in recommendations:
                    price = rec["product"].get("price", 0)
                    if price_data := rec.get("price_data"):
                        price = price_data.get("total_cost", price)
                    price_range.append(price)
                
                summary = {
                    "total_recommendations": len(recommendations),
                    "average_score": round(avg_score, 3),
                    "price_range": {
                        "min": round(min(price_range), 2) if price_range else 0,
                        "max": round(max(price_range), 2) if price_range else 0
                    },
                    "top_recommendation": {
                        "name": recommendations[0]["product"].get("name", ""),
                        "score": recommendations[0]["score"],
                        "reason": recommendations[0]["reason"]
                    }
                }
            else:
                summary = {
                    "total_recommendations": 0,
                    "message": "No products met the criteria"
                }
            
            result = {
                "success": True,
                "recommendations": recommendations,
                "summary": summary
            }
            
            self.logger.info(f"Generated {len(recommendations)} recommendations")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
