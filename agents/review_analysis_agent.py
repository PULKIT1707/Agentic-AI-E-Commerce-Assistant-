"""
Review Analysis Agent
Analyzes customer reviews and extracts sentiment insights using HuggingFace Inference API.
"""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class ReviewAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing customer reviews using sentiment analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Review Analysis Agent.
        
        Args:
            config: Configuration dictionary with API keys and endpoints
        """
        super().__init__("ReviewAnalysisAgent", config)
        self.huggingface_api_key = self.config.get("huggingface_api_key", "")
        self.huggingface_api_url = self.config.get(
            "huggingface_api_url",
            "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        self.timeout = self.config.get("timeout", 30)
        
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single review using HuggingFace Inference API.
        
        Args:
            text: Review text to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        if not self.huggingface_api_key:
            # Mock sentiment analysis if no API key provided
            self.logger.warning("No HuggingFace API key provided, using mock analysis")
            await asyncio.sleep(0.2)
            
            # Simple mock sentiment based on keywords
            text_lower = text.lower()
            positive_words = ["good", "great", "excellent", "love", "amazing", "perfect", "wonderful", "awesome", "fantastic"]
            negative_words = ["bad", "terrible", "awful", "hate", "disappointed", "poor", "worst", "horrible", "waste"]
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                label = "POSITIVE"
                score = 0.7 + min(positive_count * 0.1, 0.2)
            elif negative_count > positive_count:
                label = "NEGATIVE"
                score = 0.7 + min(negative_count * 0.1, 0.2)
            else:
                label = "NEUTRAL"
                score = 0.5
            
            return {
                "label": label,
                "score": min(score, 0.99)
            }
        
        # Actual HuggingFace API call
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {"inputs": text}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.huggingface_api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # HuggingFace returns a list of predictions
                        if isinstance(result, list) and len(result) > 0:
                            # Find the label with highest score
                            best_result = max(result[0], key=lambda x: x.get("score", 0))
                            return {
                                "label": best_result.get("label", "NEUTRAL").upper(),
                                "score": best_result.get("score", 0.5)
                            }
                        elif isinstance(result, dict):
                            return result
                        else:
                            return {"label": "NEUTRAL", "score": 0.5}
                    elif response.status == 503:
                        # Model is loading, wait and retry
                        self.logger.warning("HuggingFace model is loading, using mock analysis")
                        await asyncio.sleep(2)
                        return await self._analyze_sentiment(text)  # Retry once
                    else:
                        error_text = await response.text()
                        self.logger.error(f"HuggingFace API error: {response.status} - {error_text}")
                        return {"label": "NEUTRAL", "score": 0.5}
                        
        except asyncio.TimeoutError:
            self.logger.error("HuggingFace API timeout")
            return {"label": "NEUTRAL", "score": 0.5}
        except Exception as e:
            self.logger.error(f"Error calling HuggingFace API: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
    
    def _extract_themes(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract common themes from reviews.
        
        Args:
            reviews: List of review dictionaries with sentiment analysis
            
        Returns:
            List of theme dictionaries
        """
        # Theme keywords for common product review topics
        theme_keywords = {
            "quality": ["quality", "durable", "well-made", "sturdy", "cheap", "flimsy", "build", "material", "construction"],
            "price": ["price", "expensive", "affordable", "value", "worth", "cost", "money", "budget", "deal"],
            "shipping": ["shipping", "delivery", "fast", "slow", "arrived", "package", "received", "time"],
            "customer_service": ["service", "support", "helpful", "responsive", "customer", "contact", "return", "refund"],
            "functionality": ["works", "easy", "difficult", "feature", "function", "use", "setup", "install", "operate"],
            "performance": ["performance", "speed", "fast", "slow", "efficient", "powerful", "battery", "life"],
            "design": ["design", "look", "appearance", "style", "color", "size", "weight", "comfortable"]
        }
        
        theme_counts = {theme: {"positive": 0, "negative": 0, "neutral": 0} for theme in theme_keywords.keys()}
        
        for review in reviews:
            text_lower = review.get("text", "").lower()
            sentiment = review.get("sentiment", {}).get("label", "NEUTRAL")
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    if sentiment == "POSITIVE":
                        theme_counts[theme]["positive"] += 1
                    elif sentiment == "NEGATIVE":
                        theme_counts[theme]["negative"] += 1
                    else:
                        theme_counts[theme]["neutral"] += 1
        
        # Convert to theme list
        themes = []
        for theme, counts in theme_counts.items():
            total_mentions = counts["positive"] + counts["negative"] + counts["neutral"]
            if total_mentions > 0:
                positive_pct = (counts["positive"] / total_mentions) * 100 if total_mentions > 0 else 0
                negative_pct = (counts["negative"] / total_mentions) * 100 if total_mentions > 0 else 0
                
                themes.append({
                    "theme": theme,
                    "total_mentions": total_mentions,
                    "positive_mentions": counts["positive"],
                    "negative_mentions": counts["negative"],
                    "neutral_mentions": counts["neutral"],
                    "positive_percent": round(positive_pct, 2),
                    "negative_percent": round(negative_pct, 2),
                    "sentiment_ratio": round(counts["positive"] / total_mentions, 2) if total_mentions > 0 else 0.5
                })
        
        # Sort by total mentions
        themes.sort(key=lambda x: x["total_mentions"], reverse=True)
        
        return themes[:5]  # Return top 5 themes
    
    async def execute(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute review analysis on customer reviews.
        
        Args:
            query: Dictionary containing:
                - reviews: List of review dictionaries with "text" field (required)
                - extract_themes: Whether to extract common themes (default: True)
                
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - analyzed_reviews: List of reviews with sentiment analysis
                - sentiment_summary: Overall sentiment statistics
                - themes: Common themes extracted (if extract_themes is True)
        """
        required_fields = ["reviews"]
        if not self.validate_input(query, required_fields):
            return {
                "success": False,
                "error": "Missing required field: reviews",
                "analyzed_reviews": []
            }
        
        reviews = query.get("reviews", [])
        extract_themes = query.get("extract_themes", True)
        
        if not reviews:
            return {
                "success": False,
                "error": "No reviews provided",
                "analyzed_reviews": []
            }
        
        self.logger.info(f"Analyzing {len(reviews)} reviews")
        
        try:
            # Analyze sentiment for all reviews concurrently
            tasks = [self._analyze_sentiment(review.get("text", "")) for review in reviews]
            sentiment_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine reviews with sentiment analysis
            analyzed_reviews = []
            sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            total_score = 0.0
            
            for i, (review, sentiment_result) in enumerate(zip(reviews, sentiment_results)):
                if isinstance(sentiment_result, Exception):
                    self.logger.error(f"Error analyzing review {i}: {sentiment_result}")
                    sentiment_result = {"label": "NEUTRAL", "score": 0.5}
                
                analyzed_review = {
                    **review,
                    "sentiment": sentiment_result
                }
                analyzed_reviews.append(analyzed_review)
                
                label = sentiment_result.get("label", "NEUTRAL")
                score = sentiment_result.get("score", 0.5)
                
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
                total_score += score
            
            # Calculate sentiment summary
            total_reviews = len(analyzed_reviews)
            avg_sentiment_score = total_score / total_reviews if total_reviews > 0 else 0.5
            
            sentiment_summary = {
                "total_reviews": total_reviews,
                "positive_count": sentiment_counts["POSITIVE"],
                "negative_count": sentiment_counts["NEGATIVE"],
                "neutral_count": sentiment_counts["NEUTRAL"],
                "positive_percent": round((sentiment_counts["POSITIVE"] / total_reviews) * 100, 2) if total_reviews > 0 else 0,
                "negative_percent": round((sentiment_counts["NEGATIVE"] / total_reviews) * 100, 2) if total_reviews > 0 else 0,
                "average_sentiment_score": round(avg_sentiment_score, 3),
                "overall_sentiment": (
                    "POSITIVE" if avg_sentiment_score > 0.6
                    else "NEGATIVE" if avg_sentiment_score < 0.4
                    else "NEUTRAL"
                )
            }
            
            result = {
                "success": True,
                "analyzed_reviews": analyzed_reviews,
                "sentiment_summary": sentiment_summary
            }
            
            # Extract themes if requested
            if extract_themes:
                themes = self._extract_themes(analyzed_reviews)
                result["themes"] = themes
            
            self.logger.info(f"Analysis complete: {sentiment_summary['overall_sentiment']} sentiment")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing review analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "analyzed_reviews": []
            }

