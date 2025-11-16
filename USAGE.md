# How to Run the Agent Manually

## Quick Start

### Option 1: Interactive Mode (Easiest)

Simply run:
```bash
python run_agent.py
```

Then follow the prompts:
- Enter search term (e.g., "wireless headphones")
- Enter max results (default: 5)
- Enter platforms (ebay,amazon or 'all' for both)
- Enter min/max price (optional)

### Option 2: Command-Line Mode

Run with arguments:
```bash
python run_agent.py "wireless headphones"
```

With options:
```bash
python run_agent.py "laptop" --max-results 10 --platforms ebay,amazon --min-price 300 --max-price 1000
```

## Examples

### Basic Search
```bash
python run_agent.py "smartphone"
```

### Search with Price Filter
```bash
python run_agent.py "headphones" --min-price 50 --max-price 200
```

### Search Only eBay
```bash
python run_agent.py "laptop" --platforms ebay --max-results 10
```

### Search Only Amazon (Mock)
```bash
python run_agent.py "tablet" --platforms amazon
```

## Command-Line Options

- `--max-results N`: Maximum number of results (default: 5)
- `--platforms PLATFORMS`: Comma-separated platforms (ebay,amazon)
- `--min-price N`: Minimum price filter
- `--max-price N`: Maximum price filter

## Examples Output

```
🔍 Searching for: 'wireless headphones'
📦 Max results: 5
🛒 Platforms: ebay, amazon

============================================================

✅ Search Status: Success
📊 Total Results: 5
🛒 Platforms Searched: amazon

   Found 5 products:

   1. wireless headphones Product 1 - Amazon (Mock)
      Retailer: Amazon
      Price: $44.99
      Shipping: $0.00
      Total: $44.99
      Rating: 4.3/5.0 (100 reviews)
      URL: https://amazon.com/dp/MOCK1

   ...
```

## Using Python Directly

You can also import and use the agent in your own Python code:

```python
import asyncio
import json
from agents import ProductSearchAgent

async def main():
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    # Initialize agent
    agent = ProductSearchAgent(config.get("agents", {}).get("product_search", {}))
    
    # Search
    result = await agent.execute({
        "search_term": "wireless headphones",
        "max_results": 5,
        "platforms": ["ebay", "amazon"],
        "filters": {
            "min_price": 20,
            "max_price": 100
        }
    })
    
    # Print results
    print(f"Found {result['total_results']} products")
    for product in result['products']:
        print(f"- {product['name']}: ${product['total_price']}")

asyncio.run(main())
```

## Troubleshooting

### "config.json not found"
- Make sure you're in the project directory
- The config.json file should be in the same directory

### "No products found"
- Check that platforms are correct (ebay, amazon)
- Try different search terms
- Check API keys if using real APIs

### Import Errors
- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Make sure you're running from the project root directory

