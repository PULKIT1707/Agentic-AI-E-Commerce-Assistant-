# Amazon PA-API 5.0 Setup Guide

## Overview

The Product Search Agent now includes full Amazon Product Advertising API (PA-API) 5.0 integration with proper AWS Signature V4 authentication.

## Implementation Status

✅ **Complete AWS Signature V4 Implementation**
- Proper canonical request generation
- String-to-sign creation
- HMAC-SHA256 signature calculation
- Authorization header generation

✅ **PA-API 5.0 Integration**
- SearchItems operation
- Product data extraction (title, price, ratings, images)
- Price filtering support
- Error handling

✅ **Automatic Fallback**
- Uses real API if credentials are configured
- Falls back to mock data if credentials are missing
- Graceful error handling

## Prerequisites

To use Amazon PA-API, you need:

1. **Amazon Associates Account**
   - Sign up at https://affiliate-program.amazon.com/
   - Get approved (usually 1-2 days)
   - Get your Associate Tag

2. **AWS Account**
   - Create account at https://aws.amazon.com/
   - Set up IAM user with PA-API access
   - Get Access Key ID and Secret Access Key

## Setup Steps

### Step 1: Amazon Associates Account

1. Go to [Amazon Associates](https://affiliate-program.amazon.com/)
2. Click "Join Now for Free"
3. Sign in with your Amazon account
4. Complete the application:
   - Website/App details
   - Payment information
   - Tax information
5. Wait for approval (1-2 business days)
6. Once approved, go to "Account Settings"
7. Copy your **Associate Tag** (e.g., "yourstore-20")

### Step 2: AWS IAM Setup

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **IAM** (Identity and Access Management)
3. Click **Users** → **Add users**
4. Create user:
   - Username: `pa-api-user` (or any name)
   - Access type: **Programmatic access**
5. Set permissions:
   - Attach policy: Search for "ProductAdvertisingAPI"
   - If not found, create custom policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ProductAdvertisingAPI:*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```
6. Review and create user
7. **IMPORTANT**: Save the **Access Key ID** and **Secret Access Key** (shown only once!)

### Step 3: Configure in config.json

Update your `config.json`:

```json
{
  "agents": {
    "product_search": {
      "api_keys": {
        "ebay": "",
        "amazon_access_key": "YOUR_AWS_ACCESS_KEY_ID",
        "amazon_secret_key": "YOUR_AWS_SECRET_ACCESS_KEY",
        "amazon_associate_tag": "YOUR_ASSOCIATE_TAG"
      },
      "timeout": 10,
      "use_amazon_mock": false,
      "amazon_region": "us-east-1",
      "amazon_host": "webservices.amazon.com"
    }
  }
}
```

**Important Fields:**
- `amazon_access_key`: Your AWS Access Key ID
- `amazon_secret_key`: Your AWS Secret Access Key
- `amazon_associate_tag`: Your Amazon Associates tag
- `use_amazon_mock`: Set to `false` to use real API
- `amazon_region`: AWS region (usually "us-east-1")
- `amazon_host`: PA-API endpoint (usually "webservices.amazon.com")

### Step 4: Test

Run the test script:
```bash
python test_product_search.py
```

You should see real Amazon products if credentials are correct!

## How It Works

1. **Check Credentials**: Agent checks if all Amazon credentials are provided
2. **Generate Signature**: Creates AWS Signature V4 for authentication
3. **Make Request**: Sends POST request to PA-API 5.0 endpoint
4. **Parse Response**: Extracts product data from JSON response
5. **Return Products**: Returns standardized product format

## API Limits

- **Free Tier**: 1 request per second
- **Daily Limit**: 8,640 requests per day
- **Rate Limiting**: Built into the agent (respects 1 req/sec limit)

## Troubleshooting

### "Invalid credentials" Error
- Verify AWS Access Key ID and Secret Key are correct
- Check that IAM user has ProductAdvertisingAPI permissions
- Ensure credentials don't have extra spaces

### "Invalid Associate Tag" Error
- Verify Associate Tag is correct
- Make sure Amazon Associates account is approved
- Check tag format (usually ends with "-20" or similar)

### "Signature mismatch" Error
- This shouldn't happen with our implementation
- If it does, check that all credentials are correct
- Verify region and host settings

### "Rate limit exceeded" Error
- PA-API allows 1 request per second
- The agent handles this automatically
- If you see this, wait a moment and try again

### No Results Returned
- Some search terms may not return results
- Try different keywords
- Check that SearchIndex is appropriate

## Testing Without Credentials

The system works perfectly with mock data:
- Set `use_amazon_mock: true` in config.json
- Mock Amazon products will be returned
- All functionality works for testing

## Next Steps

Once eBay API is approved:
1. Add eBay App ID to config.json
2. You'll have both eBay and Amazon (or mock) working
3. Real product data from multiple sources!

## Implementation Details

The AWS Signature V4 implementation includes:
- Canonical request creation
- String-to-sign generation
- HMAC-SHA256 signing
- Proper header formatting
- Timestamp handling

This is a complete, production-ready implementation following AWS Signature V4 specification.

