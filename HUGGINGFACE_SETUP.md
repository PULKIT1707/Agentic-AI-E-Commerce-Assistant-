# HuggingFace Inference API Setup Guide

## Overview

The Review Analysis Agent uses HuggingFace Inference API for sentiment analysis. This guide explains how to get a free API key.

## Why HuggingFace?

- **Free Tier Available**: 1,000 requests/month free
- **High Quality Models**: Uses state-of-the-art sentiment analysis models
- **Easy Integration**: Simple REST API
- **No Credit Card Required**: For free tier

## Step-by-Step Setup

### Step 1: Create HuggingFace Account

1. Go to [HuggingFace](https://huggingface.co/)
2. Click "Sign Up" (top right)
3. Sign up with email, Google, or GitHub
4. Verify your email if required

### Step 2: Get API Token

1. After logging in, click your profile icon (top right)
2. Go to **Settings**
3. Click **Access Tokens** in the left sidebar
4. Click **New Token**
5. Fill in:
   - **Token name**: "E-Commerce Assistant" (or any name)
   - **Type**: Select **Read** (sufficient for Inference API)
6. Click **Generate Token**
7. **IMPORTANT**: Copy the token immediately (shown only once!)

### Step 3: Configure in config.json

Update your `config.json`:

```json
{
  "agents": {
    "review_analysis": {
      "huggingface_api_key": "YOUR_HUGGINGFACE_TOKEN_HERE",
      "huggingface_api_url": "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest",
      "timeout": 30
    }
  }
}
```

Replace `YOUR_HUGGINGFACE_TOKEN_HERE` with your actual token.

### Step 4: Test

Run the test script:
```bash
python test_review_analysis.py
```

You should see real sentiment analysis results!

## Model Information

**Default Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Trained on Twitter data
- Supports POSITIVE, NEGATIVE, NEUTRAL labels
- High accuracy for product reviews
- Fast inference

**Alternative Models** (you can change in config):
- `cardiffnlp/twitter-roberta-base-sentiment` (older version)
- `nlptown/bert-base-multilingual-uncased-sentiment` (multilingual)
- `distilbert-base-uncased-finetuned-sst-2-english` (faster, smaller)

## Free Tier Limits

- **1,000 requests/month** (free)
- After that, pay-as-you-go pricing
- Very affordable for testing and small projects

## How It Works

1. Agent sends review text to HuggingFace Inference API
2. Model analyzes sentiment and returns label + confidence score
3. Agent processes all reviews concurrently (async)
4. Aggregates results into sentiment summary
5. Extracts common themes from reviews

## Features

- **Sentiment Analysis**: POSITIVE, NEGATIVE, NEUTRAL classification
- **Confidence Scores**: 0.0 to 1.0 for each prediction
- **Theme Extraction**: Identifies common topics (quality, price, shipping, etc.)
- **Batch Processing**: Analyzes multiple reviews concurrently
- **Automatic Fallback**: Uses mock analysis if API unavailable

## Testing Without API Key

The agent works perfectly without an API key:
- Uses keyword-based mock sentiment analysis
- All functionality works for testing
- Just add API key for production use

## Troubleshooting

### "Invalid API Key" Error
- Verify token is correct (no extra spaces)
- Check that token type is "Read" or "Write"
- Ensure token hasn't been revoked

### "Model Loading" Error (503)
- Model may be loading (cold start)
- Agent automatically retries once
- Wait a few seconds and try again

### "Rate Limit Exceeded" Error
- Free tier: 1,000 requests/month
- Wait for next month or upgrade
- Check usage in HuggingFace dashboard

### No Results Returned
- Check that reviews have text content
- Verify API endpoint URL is correct
- Check network connectivity

## Example Usage

```python
from agents import ReviewAnalysisAgent

agent = ReviewAnalysisAgent(config)

reviews = [
    {"text": "Great product! Love it!", "author": "User1"},
    {"text": "Terrible quality, very disappointed.", "author": "User2"}
]

result = await agent.execute({
    "reviews": reviews,
    "extract_themes": True
})

print(f"Overall sentiment: {result['sentiment_summary']['overall_sentiment']}")
```

## Next Steps

Once configured, the Review Analysis Agent will:
- Analyze product reviews with high accuracy
- Extract sentiment insights
- Identify common themes
- Provide quality assessments

Perfect for the Recommendation Engine Agent!

