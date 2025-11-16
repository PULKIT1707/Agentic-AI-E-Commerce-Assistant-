# API Setup Guide

This guide explains how to get API keys for the Product Search Agent.

## eBay Finding API (Free - Recommended to Start)

### Step 1: Create eBay Developer Account
1. Go to [eBay Developers Program](https://developer.ebay.com/)
2. Click "Join" or "Sign In"
3. Sign up for a free account (use your eBay account or create new)

### Step 2: Create Application
1. After logging in, go to "My Account" → "Keys"
2. Click "Create an App Key"
3. Fill in the form:
   - **Application Title**: Your app name (e.g., "E-Commerce Assistant")
   - **Developer**: Your name
   - **Company**: Your company/school name
   - **Email**: Your email
   - **Use Case**: Select "Shopping" or "Research"
4. Accept terms and submit

### Step 3: Get Your App ID
1. After creating the app, you'll see your **Sandbox App ID** (for testing)
2. Copy this App ID
3. Add it to `config.json`:
```json
{
  "agents": {
    "product_search": {
      "api_keys": {
        "ebay": "YOUR_SANDBOX_APP_ID_HERE"
      }
    }
  }
}
```

### Step 4: Test
Run the test script:
```bash
python test_product_search.py
```

**Note**: Sandbox App ID works for testing. For production, you'll need to request Production credentials.

---

## Amazon Product Advertising API (PA-API 5.0) - Optional

Amazon PA-API requires AWS credentials and is more complex to set up.

### Step 1: Create Amazon Associates Account
1. Go to [Amazon Associates](https://affiliate-program.amazon.com/)
2. Sign up for an account
3. Get approved (may take 1-2 days)

### Step 2: Get Associate Tag
1. After approval, go to "Account Settings"
2. Find your **Associate Tag** (e.g., "yourstore-20")
3. Copy this tag

### Step 3: Create AWS Account and IAM User
1. Go to [AWS Console](https://aws.amazon.com/)
2. Create an AWS account (if you don't have one)
3. Go to IAM (Identity and Access Management)
4. Create a new user:
   - Username: `pa-api-user`
   - Access type: Programmatic access
5. Attach policy: `ProductAdvertisingAPI` (if available) or create custom policy
6. Save **Access Key ID** and **Secret Access Key**

### Step 4: Configure in config.json
```json
{
  "agents": {
    "product_search": {
      "api_keys": {
        "amazon_access_key": "YOUR_AWS_ACCESS_KEY_ID",
        "amazon_secret_key": "YOUR_AWS_SECRET_ACCESS_KEY",
        "amazon_associate_tag": "YOUR_ASSOCIATE_TAG"
      },
      "amazon_region": "us-east-1",
      "amazon_host": "webservices.amazon.com",
      "use_amazon_mock": false
    }
  }
}
```

### Step 5: Test
Run the test script to verify Amazon integration works.

**Note**: Amazon PA-API has rate limits (1 request/second on free tier). The implementation uses AWS Signature V4 which is complex.

---

## Quick Start (Recommended)

**For testing, start with eBay only:**

1. Get eBay Sandbox App ID (free, takes 5 minutes)
2. Add to `config.json`
3. Run tests - you'll get real eBay product data!

**For production or more data:**
- Add Amazon PA-API credentials
- Or use mock Amazon data (already working)

---

## Troubleshooting

### eBay API Issues
- **"Invalid App ID"**: Make sure you copied the Sandbox App ID correctly
- **"No results"**: Try different search terms, some may not return results
- **Rate limiting**: eBay allows 5,000 calls/day on free tier

### Amazon PA-API Issues
- **"Invalid credentials"**: Verify AWS Access Key and Secret Key
- **"Invalid Associate Tag"**: Make sure Associate Tag is correct
- **"Signature mismatch"**: AWS Signature V4 is complex - check implementation
- **Rate limiting**: 1 request/second limit on free tier

### General Issues
- Check `config.json` syntax (must be valid JSON)
- Verify API keys don't have extra spaces
- Check internet connection
- Review logs for detailed error messages

---

## Testing Without API Keys

The system works with mock Amazon data by default. You can test without any API keys:
- Mock Amazon products will be returned
- eBay search will be skipped (with warning)
- All other functionality works normally

