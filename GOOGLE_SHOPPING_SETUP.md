# Google Shopping API Setup Guide

## Overview

The Price Comparison Agent can use Google Shopping via Google Custom Search API to get price comparisons from multiple retailers.

## Prerequisites

- Google account
- Access to Google Cloud Console

## Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "E-Commerce Assistant")
4. Click "Create"

### Step 2: Enable Custom Search API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Custom Search API"
3. Click on it and click "Enable"

### Step 3: Create API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy your API key
4. (Optional) Click "Restrict Key" to limit usage:
   - Under "API restrictions", select "Restrict key"
   - Choose "Custom Search API"
   - Save

### Step 4: Create Custom Search Engine

1. Go to [Google Custom Search](https://programmablesearchengine.google.com/)
2. Click "Add" to create a new search engine
3. Configure:
   - **Sites to search**: `shopping.google.com`
   - **Name**: Your search engine name (e.g., "Shopping Search")
   - **Language**: English (or your preference)
4. Click "Create"
5. Go to "Control Panel" → "Basics"
6. Copy your **Search Engine ID** (CX)

### Step 5: Configure in config.json

Update your `config.json`:

```json
{
  "agents": {
    "price_comparison": {
      "api_keys": {
        "google_api_key": "YOUR_GOOGLE_API_KEY",
        "priceapi": ""
      },
      "timeout": 10,
      "use_google_shopping": true,
      "use_priceapi": false,
      "google_cx": "YOUR_SEARCH_ENGINE_ID"
    }
  }
}
```

**Important Fields:**
- `google_api_key`: Your Google Cloud API key
- `google_cx`: Your Custom Search Engine ID
- `use_google_shopping`: Set to `true` to enable Google Shopping

## Free Tier Limits

- **100 queries per day** (free tier)
- After that, $5 per 1,000 queries
- Very affordable for testing and small projects

## How It Works

1. Agent sends product search query to Google Custom Search API
2. API searches Google Shopping for the product
3. Results include prices from multiple retailers
4. Agent extracts prices and retailer information
5. Compares prices and finds best deals

## Testing

Run the test script:
```bash
python test_price_comparison.py
```

Or use the agent directly:
```python
result = await comparison_agent.execute({
    "product_name": "wireless headphones",
    "use_google_shopping": True
})
```

## Troubleshooting

### "Invalid API Key" Error
- Verify API key is correct
- Check that Custom Search API is enabled
- Ensure API key restrictions allow Custom Search API

### "Invalid CX" Error
- Verify Search Engine ID (CX) is correct
- Check that search engine is configured for shopping.google.com
- Ensure search engine is active

### "Quota Exceeded" Error
- Free tier: 100 queries/day
- Wait 24 hours or upgrade to paid tier
- Check usage in Google Cloud Console

### No Results Returned
- Some products may not have Google Shopping results
- Try different search terms
- Check that search engine includes shopping.google.com

## Alternative: Using ProductSearchAgent Results

If you don't want to set up Google Shopping API, the agent works perfectly with products from ProductSearchAgent (which uses eBay/Amazon APIs). This is the default behavior.

## Cost Considerations

- **Free Tier**: 100 queries/day (perfect for testing)
- **Paid**: $5 per 1,000 queries (very affordable)
- No credit card required for free tier

