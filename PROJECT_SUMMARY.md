# Agentic AI E-Commerce Assistant - Project Summary

## Project Overview

A modular, agent-based AI system that helps users search for, compare prices, analyze reviews, and receive personalized product recommendations. The system integrates with multiple external APIs and uses a sophisticated scoring algorithm to provide the best recommendations.

## Completed Components

### 1. **Product Search Agent** (`agents/product_search_agent.py`)
- **FakeStore API Integration**: Free product search, no authentication required (default)
  - Endpoint: `GET https://fakestoreapi.com/products`
- **DummyJSON API Integration**: Free product search with reviews, no authentication required (default)
  - Search: `GET https://dummyjson.com/products/search?q={query}`
- **eBay Finding API Integration**: Real product search from eBay (optional, free tier: 5,000 calls/day)
- **Amazon PA-API 5.0 Integration**: Full AWS Signature V4 implementation for Amazon product search (optional)
- **Mock Amazon Data**: Fallback to mock data when APIs unavailable
- **Features**:
  - Concurrent multi-platform searches
  - Price filtering (min/max)
  - Platform-specific search
  - Error handling with graceful fallbacks
  - XML parsing for eBay responses
  - JSON parsing for FakeStore, DummyJSON, and Amazon PA-API

**Test File**: `test_product_search.py`
**Setup Guides**: `API_SETUP_GUIDE.md`, `AMAZON_PAAPI_SETUP.md`

### 2. **Price Comparison Agent** (`agents/price_comparison_agent.py`)
- **Multi-Retailer Comparison**: Aggregates prices from ProductSearchAgent results
- **Google Shopping API Integration**: Direct price comparison via Google Custom Search
- **PriceAPI Integration**: Placeholder for paid multi-retailer service
- **Features**:
  - Best deal detection
  - Price history tracking (30-day in-memory storage)
  - Price trend analysis (increasing/decreasing/stable)
  - Savings calculation
  - Automatic price extraction from search snippets

**Test File**: `test_price_comparison.py`
**Setup Guide**: `GOOGLE_SHOPPING_SETUP.md`

### 3. **Review Analysis Agent** (`agents/review_analysis_agent.py`)
- **Review Fetching**: Fetches real reviews from DummyJSON API for numeric product IDs
  - Endpoint: `GET https://dummyjson.com/products/{pid}` (numeric IDs only)
- **HuggingFace Inference API**: Real sentiment analysis using router endpoint
  - Endpoint: `POST https://router.huggingface.co/hf-inference/models/{model}`
  - Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Mock Analysis Fallback**: Works without API keys for testing
- **Features**:
  - Automatic review fetching for DummyJSON products
  - Sentiment classification (POSITIVE, NEGATIVE, NEUTRAL) with confidence scores
  - Theme extraction (quality, price, shipping, functionality, etc.)
  - Batch review processing
  - Sentiment summary statistics
  - Average sentiment score calculation

**Test File**: `test_review_analysis.py`
**Setup Guide**: `HUGGINGFACE_SETUP.md`

### 4. **Recommendation Engine Agent** (`agents/recommendation_engine_agent.py`)
- **Multi-Factor Scoring Algorithm**: Combines price, sentiment, rating, and review count
- **Budget-Aware Recommendations**: Prioritizes products within user budget
- **Personalized Ranking**: Configurable weights for different factors
- **Features**:
  - Normalized scoring (0-1 range)
  - Budget constraint enforcement
  - Human-readable recommendation reasons
  - Top-N recommendations
  - Comprehensive summary statistics

**Test File**: `test_recommendation_engine.py` (full workflow test)

### 5. **Workflow Manager** (`agents/workflow_manager.py`)
- **Centralized Orchestration**: Single entry point for complete workflow
- **Agent Communication**: Facilitates data flow between all agents
- **Complete Workflow**: Search → Compare → Analyze → Recommend
- **Features**:
  - Orchestrates all 4 agents in sequence
  - Manages data flow between agents
  - Handles errors and graceful degradation
  - Supports partial workflow execution (individual steps)
  - Comprehensive error handling and logging
  - Configurable workflow steps (can skip price comparison or review analysis)

**Test File**: `test_workflow_manager.py` (comprehensive test suite covering all scenarios)

## Project Structure

```
Lab2/
├── agents/
│   ├── __init__.py                      # Package initialization
│   ├── base_agent.py                    # Abstract base class
│   ├── product_search_agent.py         # Product search (eBay, Amazon)
│   ├── price_comparison_agent.py       # Price comparison & history
│   ├── review_analysis_agent.py        # Sentiment analysis
│   ├── recommendation_engine_agent.py  # Recommendation synthesis
│   └── workflow_manager.py             # Centralized workflow orchestration
├── config.json                          # Centralized configuration
├── requirements.txt                     # Python dependencies
├── README.md                           # Main documentation
├── USAGE.md                            # Usage instructions
├── PROJECT_SUMMARY.md                  # Project summary and status
├── REQUIREMENTS_COMPLIANCE.md          # Requirements compliance analysis
├── test_product_search.py              # Product search tests
├── test_price_comparison.py            # Price comparison tests
├── test_review_analysis.py             # Review analysis tests
├── test_recommendation_engine.py       # Full workflow test
├── test_workflow_manager.py            # Comprehensive workflow tests
├── run_agent.py                        # Manual agent runner
├── API_SETUP_GUIDE.md                  # General API setup
├── AMAZON_PAAPI_SETUP.md               # Amazon PA-API setup
├── GOOGLE_SHOPPING_SETUP.md            # Google Shopping setup
└── HUGGINGFACE_SETUP.md                # HuggingFace API setup
```

## Configuration

All configuration is centralized in `config.json`:

```json
{
  "agents": {
    "product_search": {
      "ebay": "YOUR_EBAY_APP_ID",
      "amazon_access_key": "YOUR_ACCESS_KEY",
      "amazon_secret_key": "YOUR_SECRET_KEY",
      "amazon_associate_tag": "YOUR_ASSOCIATE_TAG",
      "amazon_region": "us-east-1",
      "amazon_host": "webservices.amazon.com"
    },
    "price_comparison": {
      "google_api_key": "YOUR_GOOGLE_API_KEY",
      "google_cx": "YOUR_CUSTOM_SEARCH_ENGINE_ID",
      "use_google_shopping": true
    },
    "review_analysis": {
      "huggingface_api_key": "YOUR_HUGGINGFACE_TOKEN",
      "huggingface_api_url": "https://api-inference.huggingface.co/models/...",
      "timeout": 30
    },
    "recommendation_engine": {
      "weights": {
        "price": 0.3,
        "sentiment": 0.4,
        "rating": 0.2,
        "review_count": 0.1
      },
      "budget_weight": 0.5
    }
  }
}
```

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Complete Workflow (Recommended)
```bash
python test_workflow_manager.py
```
This runs comprehensive tests covering:
- Budget constraints
- Specific requirements
- Comparative shopping
- Individual workflow steps

### Run Full Workflow Test (Legacy)
```bash
python test_recommendation_engine.py
```

### Run Individual Agent Tests
```bash
python test_product_search.py
python test_price_comparison.py
python test_review_analysis.py
```

### Manual Agent Execution
```bash
python run_agent.py
```

### Using Workflow Manager in Code
```python
import asyncio
from agents import WorkflowManager

async def main():
    workflow = WorkflowManager()
    result = await workflow.execute_workflow({
        "search_term": "wireless headphones",
        "max_results": 10,
        "user_preferences": {
            "budget": 100,
            "min_rating": 4.0
        }
    })
    print(result["recommendations"])

asyncio.run(main())
```

## External API Integrations

### Free APIs (No Cost, No Authentication)
1. **FakeStore API**: Unlimited calls, no authentication required (default)
2. **DummyJSON API**: Unlimited calls, no authentication required (default)
3. **HuggingFace Inference API**: Free tier available (router endpoint)

### Free APIs (Requires API Key)
1. **eBay Finding API**: 5,000 calls/day free tier
2. **Google Custom Search API**: 100 queries/day free tier

### Paid/Requires Setup
1. **Amazon PA-API 5.0**: Requires Amazon Associates account + AWS IAM credentials
2. **PriceAPI**: Optional paid service for multi-retailer price comparison

### Mock Data Fallbacks
- All agents have mock data fallbacks for testing without API keys
- System gracefully degrades when APIs are unavailable

## Testing Status

All agents have individual test files
Full workflow test demonstrates end-to-end integration
Comprehensive workflow manager test suite covering all required scenarios:
   - Budget constraints
   - Specific requirements
   - Comparative shopping
   - Individual workflow steps
Mock data fallbacks tested
Error handling verified
No linter errors

## Key Features

### Architecture
- **Modular Design**: Each agent is independent and replaceable
- **Centralized Workflow**: `WorkflowManager` orchestrates all agents and facilitates communication
- **Async-First**: All operations use `asyncio` for concurrent execution
- **Base Agent Pattern**: Common functionality in `BaseAgent` abstract class
- **Configuration-Driven**: Centralized config with environment variable support
- **Workflow Orchestration**: Single entry point for complete workflow execution

### Recommendation Algorithm
- **Multi-Factor Scoring**: Price (30%), Sentiment (40%), Rating (20%), Review Count (10%)
- **Budget Constraints**: Products exceeding budget are penalized
- **Normalized Scores**: All factors normalized to 0-1 range
- **Explainable**: Each recommendation includes human-readable reasons

### Error Handling
- Graceful API failures with fallbacks
- Comprehensive logging
- Input validation
- Timeout handling

## Documentation

- **README.md**: Main project documentation
- **USAGE.md**: Detailed usage instructions and examples
- **API Setup Guides**: Step-by-step instructions for each API
- **Code Documentation**: Docstrings for all public methods

## Next Steps (Future Enhancements)

1. **Centralized Workflow Manager**: COMPLETED - Orchestrates all agents in a single workflow
2. **FastAPI REST Endpoints**: Expose agents as HTTP API
3. **Comprehensive Test Suite**: COMPLETED - Workflow manager test suite with full coverage
4. **Optional UI**: Streamlit or Gradio interface for demo
5. **Database Integration**: Persistent storage for price history
6. **Caching Layer**: Reduce API calls with intelligent caching
7. **User Preferences**: Learn and store user preferences over time

## Technical Stack

- **Python 3.10+**
- **asyncio**: Asynchronous programming
- **aiohttp**: Async HTTP client
- **json/xml**: Data parsing
- **logging**: Comprehensive logging
- **math**: Score normalization and calculations

## Highlights

- All 4 core agents implemented and tested
- Centralized Workflow Manager for agent orchestration
- Real API integrations with fallbacks
- Complete documentation
- Production-ready error handling
- Modular, extensible architecture
- Zero linter errors
- Full workflow demonstration
- Comprehensive test suite covering all required scenarios

---

## Requirements Compliance

**All requirements from Part 3 are now fully met:**

1. **Product Search API Agent** - Implemented with FakeStore, DummyJSON, eBay and Amazon integration
2. **Price Comparison API Agent** - Implemented with price history tracking
3. **Review Analysis Agent** - Implemented with HuggingFace sentiment analysis and review fetching
4. **Recommendation Engine Agent** - Implemented with multi-factor scoring
5. **Modular Design** - All agents extend BaseAgent, fully modular
6. **Communication Workflow** - Centralized WorkflowManager facilitates agent communication
7. **Testing** - Comprehensive test suite covering budget constraints, specific requirements, and comparative shopping

**Status**: ALL REQUIREMENTS COMPLETE - System ready for deployment and further enhancements.

