# Dhanworks Bot API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [API Endpoints](#api-endpoints)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Code Examples](#code-examples)

---

## Overview

The Dhanworks Bot API provides programmatic access to financial analysis, market data, and bot automation features. The API follows RESTful principles and returns JSON-formatted responses.

**Current API Version:** v1
**Last Updated:** 2025-12-27

---

## Authentication

The API uses **Bearer Token Authentication**. All requests must include an `Authorization` header with a valid API token.

### Obtaining an API Token

1. Log in to your Dhanworks account
2. Navigate to **Settings** → **API Keys**
3. Click **Generate New Token**
4. Copy and store your token securely (it will only be displayed once)

### Authorization Header Format

```
Authorization: Bearer YOUR_API_TOKEN_HERE
```

### Token Security Best Practices

- Store tokens in environment variables, never in code
- Rotate tokens regularly
- Use separate tokens for different applications
- Revoke tokens immediately if compromised
- Use HTTPS for all requests

---

## Base URL

```
https://api.dhanworks.com/v1
```

All endpoints are relative to this base URL.

---

## API Endpoints

### 1. Market Data Endpoints

#### Get Market Overview
**Endpoint:** `GET /market/overview`

**Description:** Retrieve current market overview and indices information.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| market | string | No | Specific market (e.g., 'NSE', 'BSE', 'NIFTY50') |

**Response:**
```json
{
  "status": "success",
  "data": {
    "timestamp": "2025-12-27T07:20:53Z",
    "markets": [
      {
        "symbol": "NIFTY50",
        "current_price": 19845.50,
        "change": 125.40,
        "change_percent": 0.64,
        "high": 19900.00,
        "low": 19700.00,
        "volume": 1250000
      }
    ]
  }
}
```

---

#### Get Stock Quote
**Endpoint:** `GET /market/quote/{symbol}`

**Description:** Get detailed quote for a specific stock.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Stock symbol (e.g., 'RELIANCE', 'INFY') |
| interval | string | No | Data interval ('1m', '5m', '15m', '1h', '1d') |

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "current_price": 2850.50,
    "open": 2840.00,
    "high": 2865.00,
    "low": 2835.00,
    "close": 2850.50,
    "volume": 5234000,
    "market_cap": 3850000000000,
    "pe_ratio": 28.5,
    "dividend_yield": 1.2,
    "timestamp": "2025-12-27T07:20:53Z"
  }
}
```

---

#### Get Historical Data
**Endpoint:** `GET /market/history/{symbol}`

**Description:** Retrieve historical OHLC data for a stock.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Stock symbol |
| from_date | string | Yes | Start date (YYYY-MM-DD) |
| to_date | string | Yes | End date (YYYY-MM-DD) |
| interval | string | No | Data interval ('1d', '1w', '1mo') - default: '1d' |

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "INFY",
    "interval": "1d",
    "candles": [
      {
        "timestamp": "2025-12-26T00:00:00Z",
        "open": 1920.00,
        "high": 1935.50,
        "low": 1915.00,
        "close": 1930.25,
        "volume": 2450000
      },
      {
        "timestamp": "2025-12-25T00:00:00Z",
        "open": 1910.00,
        "high": 1925.00,
        "low": 1905.00,
        "close": 1920.00,
        "volume": 2150000
      }
    ]
  }
}
```

---

### 2. Portfolio Endpoints

#### Get Portfolio Summary
**Endpoint:** `GET /portfolio/summary`

**Description:** Get overview of user's portfolio.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_value": 500000,
    "invested_amount": 450000,
    "profit_loss": 50000,
    "profit_loss_percent": 11.11,
    "total_holdings": 15,
    "timestamp": "2025-12-27T07:20:53Z"
  }
}
```

---

#### Get Holdings
**Endpoint:** `GET /portfolio/holdings`

**Description:** List all stock holdings in the portfolio.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Number of results (default: 20, max: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_count": 15,
    "holdings": [
      {
        "symbol": "TCS",
        "quantity": 10,
        "buy_price": 3500.00,
        "current_price": 3850.00,
        "current_value": 38500.00,
        "profit_loss": 3500.00,
        "profit_loss_percent": 10.0,
        "purchase_date": "2025-06-15",
        "investment_amount": 35000.00
      }
    ]
  }
}
```

---

#### Add Holding
**Endpoint:** `POST /portfolio/holdings`

**Description:** Add a new stock holding to portfolio.

**Request Body:**
```json
{
  "symbol": "WIPRO",
  "quantity": 50,
  "buy_price": 400.50,
  "purchase_date": "2025-12-27"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Holding added successfully",
  "data": {
    "holding_id": "hold_xyz123",
    "symbol": "WIPRO",
    "quantity": 50,
    "investment_amount": 20025.00
  }
}
```

---

#### Update Holding
**Endpoint:** `PUT /portfolio/holdings/{holding_id}`

**Description:** Update an existing holding.

**Request Body:**
```json
{
  "quantity": 75,
  "buy_price": 400.50
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Holding updated successfully",
  "data": {
    "holding_id": "hold_xyz123",
    "symbol": "WIPRO",
    "quantity": 75,
    "investment_amount": 30037.50
  }
}
```

---

#### Delete Holding
**Endpoint:** `DELETE /portfolio/holdings/{holding_id}`

**Description:** Remove a holding from portfolio.

**Response:**
```json
{
  "status": "success",
  "message": "Holding deleted successfully"
}
```

---

### 3. Analysis Endpoints

#### Get Technical Analysis
**Endpoint:** `GET /analysis/technical/{symbol}`

**Description:** Get technical indicators and analysis for a stock.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | Yes | Stock symbol |
| period | integer | No | Analysis period in days (default: 20) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "SBIN",
    "analysis_date": "2025-12-27T07:20:53Z",
    "indicators": {
      "rsi": {
        "value": 65.5,
        "signal": "overbought",
        "period": 14
      },
      "macd": {
        "value": 2.35,
        "signal_line": 1.80,
        "histogram": 0.55,
        "trend": "bullish"
      },
      "moving_averages": {
        "sma_20": 520.30,
        "sma_50": 515.40,
        "ema_12": 522.50,
        "ema_26": 519.30
      },
      "bollinger_bands": {
        "upper": 535.50,
        "middle": 520.30,
        "lower": 505.10,
        "position": "upper"
      }
    },
    "trend": "bullish",
    "support": 510.00,
    "resistance": 540.00
  }
}
```

---

#### Get Fundamental Analysis
**Endpoint:** `GET /analysis/fundamental/{symbol}`

**Description:** Get fundamental analysis and financial metrics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "MARUTI",
    "financial_metrics": {
      "pe_ratio": 24.5,
      "pb_ratio": 3.2,
      "dividend_yield": 1.8,
      "eps": 185.50,
      "roe": 16.5,
      "debt_to_equity": 0.45,
      "current_ratio": 1.25
    },
    "quarterly_results": {
      "revenue": 28500000000,
      "net_profit": 1850000000,
      "revenue_growth": 8.5,
      "profit_growth": 12.3
    },
    "rating": "BUY",
    "target_price": 11500.00
  }
}
```

---

### 4. Watchlist Endpoints

#### Create Watchlist
**Endpoint:** `POST /watchlist`

**Description:** Create a new watchlist.

**Request Body:**
```json
{
  "name": "Tech Stocks",
  "description": "Technology sector stocks to monitor"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "watchlist_id": "wl_abc123",
    "name": "Tech Stocks",
    "created_at": "2025-12-27T07:20:53Z"
  }
}
```

---

#### Get Watchlists
**Endpoint:** `GET /watchlist`

**Description:** Retrieve all user watchlists.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "watchlist_id": "wl_abc123",
      "name": "Tech Stocks",
      "symbol_count": 5,
      "created_at": "2025-12-27T07:20:53Z"
    }
  ]
}
```

---

#### Add Stock to Watchlist
**Endpoint:** `POST /watchlist/{watchlist_id}/symbols`

**Description:** Add a stock to a watchlist.

**Request Body:**
```json
{
  "symbol": "HCLTECH"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Stock added to watchlist",
  "data": {
    "watchlist_id": "wl_abc123",
    "symbol": "HCLTECH"
  }
}
```

---

#### Remove Stock from Watchlist
**Endpoint:** `DELETE /watchlist/{watchlist_id}/symbols/{symbol}`

**Description:** Remove a stock from watchlist.

**Response:**
```json
{
  "status": "success",
  "message": "Stock removed from watchlist"
}
```

---

### 5. Alert Endpoints

#### Create Price Alert
**Endpoint:** `POST /alerts`

**Description:** Create a price alert for a stock.

**Request Body:**
```json
{
  "symbol": "BAJAJFINSV",
  "alert_type": "price",
  "condition": "above",
  "target_price": 1800.00,
  "notification_method": "email"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "alert_id": "alrt_def456",
    "symbol": "BAJAJFINSV",
    "target_price": 1800.00,
    "status": "active",
    "created_at": "2025-12-27T07:20:53Z"
  }
}
```

---

#### Get Active Alerts
**Endpoint:** `GET /alerts`

**Description:** List all active alerts.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status ('active', 'triggered', 'inactive') |

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "alert_id": "alrt_def456",
      "symbol": "BAJAJFINSV",
      "alert_type": "price",
      "condition": "above",
      "target_price": 1800.00,
      "current_price": 1750.50,
      "status": "active",
      "notification_method": "email"
    }
  ]
}
```

---

#### Delete Alert
**Endpoint:** `DELETE /alerts/{alert_id}`

**Description:** Remove an alert.

**Response:**
```json
{
  "status": "success",
  "message": "Alert deleted successfully"
}
```

---

### 6. Bot Automation Endpoints

#### Create Trading Bot
**Endpoint:** `POST /bots`

**Description:** Create an automated trading bot.

**Request Body:**
```json
{
  "name": "Morning Trend Trader",
  "symbol": "HDFC",
  "strategy": "moving_average_crossover",
  "parameters": {
    "fast_period": 12,
    "slow_period": 26,
    "quantity": 10
  },
  "enabled": true,
  "start_time": "09:30",
  "end_time": "15:30"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "bot_id": "bot_ghi789",
    "name": "Morning Trend Trader",
    "symbol": "HDFC",
    "strategy": "moving_average_crossover",
    "status": "active",
    "created_at": "2025-12-27T07:20:53Z"
  }
}
```

---

#### Get Bot Status
**Endpoint:** `GET /bots/{bot_id}`

**Description:** Get status and performance of a specific bot.

**Response:**
```json
{
  "status": "success",
  "data": {
    "bot_id": "bot_ghi789",
    "name": "Morning Trend Trader",
    "symbol": "HDFC",
    "status": "active",
    "total_trades": 45,
    "winning_trades": 32,
    "losing_trades": 13,
    "win_rate": 71.1,
    "total_profit": 25450.00,
    "roi": 5.09,
    "running_since": "2025-12-01T09:30:00Z"
  }
}
```

---

#### Update Bot
**Endpoint:** `PUT /bots/{bot_id}`

**Description:** Modify an existing bot configuration.

**Request Body:**
```json
{
  "name": "Updated Bot Name",
  "parameters": {
    "fast_period": 10,
    "slow_period": 30,
    "quantity": 15
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Bot updated successfully",
  "data": {
    "bot_id": "bot_ghi789",
    "name": "Updated Bot Name"
  }
}
```

---

#### Stop Bot
**Endpoint:** `POST /bots/{bot_id}/stop`

**Description:** Stop a running bot.

**Response:**
```json
{
  "status": "success",
  "message": "Bot stopped successfully",
  "data": {
    "bot_id": "bot_ghi789",
    "status": "stopped"
  }
}
```

---

#### Delete Bot
**Endpoint:** `DELETE /bots/{bot_id}`

**Description:** Delete a bot permanently.

**Response:**
```json
{
  "status": "success",
  "message": "Bot deleted successfully"
}
```

---

## Request/Response Examples

### Common Response Codes

| Code | Description |
|------|-------------|
| 200 | Successful request |
| 201 | Resource created successfully |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

---

## Error Handling

All error responses follow this format:

```json
{
  "status": "error",
  "error_code": "INVALID_SYMBOL",
  "message": "The stock symbol 'INVALID' does not exist",
  "timestamp": "2025-12-27T07:20:53Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| INVALID_TOKEN | 401 | Authentication token is invalid or expired |
| INVALID_SYMBOL | 404 | Stock symbol not found |
| VALIDATION_ERROR | 400 | Request body validation failed |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INSUFFICIENT_BALANCE | 400 | Insufficient funds for operation |
| INTERNAL_ERROR | 500 | Server error occurred |

---

## Rate Limiting

The API implements rate limiting to prevent abuse.

**Default Limits:**
- Free Tier: 100 requests per hour
- Premium Tier: 1,000 requests per hour
- Enterprise Tier: Unlimited

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1703661653
```

When rate limit is exceeded, the API returns a 429 response with:
```json
{
  "status": "error",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Please retry after 3600 seconds",
  "retry_after": 3600
}
```

---

## Code Examples

### Python

#### Installation
```bash
pip install requests python-dotenv
```

#### Market Data
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('DHANWORKS_API_TOKEN')
BASE_URL = 'https://api.dhanworks.com/v1'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Get Market Overview
def get_market_overview():
    url = f'{BASE_URL}/market/overview'
    response = requests.get(url, headers=headers)
    return response.json()

# Get Stock Quote
def get_stock_quote(symbol):
    url = f'{BASE_URL}/market/quote/{symbol}'
    response = requests.get(url, headers=headers)
    return response.json()

# Get Historical Data
def get_historical_data(symbol, from_date, to_date):
    url = f'{BASE_URL}/market/history/{symbol}'
    params = {
        'from_date': from_date,
        'to_date': to_date,
        'interval': '1d'
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Usage
if __name__ == '__main__':
    print('Market Overview:')
    overview = get_market_overview()
    print(overview)
    
    print('\nTCS Quote:')
    quote = get_stock_quote('TCS')
    print(quote)
    
    print('\nINFY Historical Data:')
    history = get_historical_data('INFY', '2025-12-01', '2025-12-27')
    print(history)
```

#### Portfolio Management
```python
# Get Portfolio Summary
def get_portfolio_summary():
    url = f'{BASE_URL}/portfolio/summary'
    response = requests.get(url, headers=headers)
    return response.json()

# Get Holdings
def get_holdings(limit=20, offset=0):
    url = f'{BASE_URL}/portfolio/holdings'
    params = {'limit': limit, 'offset': offset}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Add Holding
def add_holding(symbol, quantity, buy_price, purchase_date):
    url = f'{BASE_URL}/portfolio/holdings'
    payload = {
        'symbol': symbol,
        'quantity': quantity,
        'buy_price': buy_price,
        'purchase_date': purchase_date
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Update Holding
def update_holding(holding_id, quantity, buy_price):
    url = f'{BASE_URL}/portfolio/holdings/{holding_id}'
    payload = {'quantity': quantity, 'buy_price': buy_price}
    response = requests.put(url, headers=headers, json=payload)
    return response.json()

# Delete Holding
def delete_holding(holding_id):
    url = f'{BASE_URL}/portfolio/holdings/{holding_id}'
    response = requests.delete(url, headers=headers)
    return response.json()

# Usage
holdings = get_holdings()
print(holdings)

new_holding = add_holding('WIPRO', 50, 400.50, '2025-12-27')
print(new_holding)
```

#### Bot Automation
```python
# Create Bot
def create_bot(name, symbol, strategy, parameters):
    url = f'{BASE_URL}/bots'
    payload = {
        'name': name,
        'symbol': symbol,
        'strategy': strategy,
        'parameters': parameters,
        'enabled': True,
        'start_time': '09:30',
        'end_time': '15:30'
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Get Bot Status
def get_bot_status(bot_id):
    url = f'{BASE_URL}/bots/{bot_id}'
    response = requests.get(url, headers=headers)
    return response.json()

# Stop Bot
def stop_bot(bot_id):
    url = f'{BASE_URL}/bots/{bot_id}/stop'
    response = requests.post(url, headers=headers)
    return response.json()

# Usage
bot_config = {
    'fast_period': 12,
    'slow_period': 26,
    'quantity': 10
}
new_bot = create_bot('MA Crossover', 'HDFC', 'moving_average_crossover', bot_config)
print(new_bot)

status = get_bot_status(new_bot['data']['bot_id'])
print(status)
```

---

### JavaScript/Node.js

#### Installation
```bash
npm install axios dotenv
```

#### Market Data
```javascript
require('dotenv').config();
const axios = require('axios');

const API_TOKEN = process.env.DHANWORKS_API_TOKEN;
const BASE_URL = 'https://api.dhanworks.com/v1';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Get Market Overview
async function getMarketOverview() {
  try {
    const response = await apiClient.get('/market/overview');
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Get Stock Quote
async function getStockQuote(symbol) {
  try {
    const response = await apiClient.get(`/market/quote/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Get Historical Data
async function getHistoricalData(symbol, fromDate, toDate) {
  try {
    const response = await apiClient.get(`/market/history/${symbol}`, {
      params: {
        from_date: fromDate,
        to_date: toDate,
        interval: '1d'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Usage
(async () => {
  console.log('Market Overview:');
  const overview = await getMarketOverview();
  console.log(overview);
  
  console.log('\nTCS Quote:');
  const quote = await getStockQuote('TCS');
  console.log(quote);
  
  console.log('\nINFY Historical Data:');
  const history = await getHistoricalData('INFY', '2025-12-01', '2025-12-27');
  console.log(history);
})();
```

#### Portfolio Management
```javascript
// Get Portfolio Summary
async function getPortfolioSummary() {
  try {
    const response = await apiClient.get('/portfolio/summary');
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Get Holdings
async function getHoldings(limit = 20, offset = 0) {
  try {
    const response = await apiClient.get('/portfolio/holdings', {
      params: { limit, offset }
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Add Holding
async function addHolding(symbol, quantity, buyPrice, purchaseDate) {
  try {
    const response = await apiClient.post('/portfolio/holdings', {
      symbol,
      quantity,
      buy_price: buyPrice,
      purchase_date: purchaseDate
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Update Holding
async function updateHolding(holdingId, quantity, buyPrice) {
  try {
    const response = await apiClient.put(`/portfolio/holdings/${holdingId}`, {
      quantity,
      buy_price: buyPrice
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Delete Holding
async function deleteHolding(holdingId) {
  try {
    const response = await apiClient.delete(`/portfolio/holdings/${holdingId}`);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Usage
(async () => {
  const holdings = await getHoldings();
  console.log(holdings);
  
  const newHolding = await addHolding('WIPRO', 50, 400.50, '2025-12-27');
  console.log(newHolding);
})();
```

#### Bot Automation
```javascript
// Create Bot
async function createBot(name, symbol, strategy, parameters) {
  try {
    const response = await apiClient.post('/bots', {
      name,
      symbol,
      strategy,
      parameters,
      enabled: true,
      start_time: '09:30',
      end_time: '15:30'
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Get Bot Status
async function getBotStatus(botId) {
  try {
    const response = await apiClient.get(`/bots/${botId}`);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Stop Bot
async function stopBot(botId) {
  try {
    const response = await apiClient.post(`/bots/${botId}/stop`);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Usage
(async () => {
  const botConfig = {
    fast_period: 12,
    slow_period: 26,
    quantity: 10
  };
  
  const newBot = await createBot('MA Crossover', 'HDFC', 'moving_average_crossover', botConfig);
  console.log(newBot);
  
  const status = await getBotStatus(newBot.data.bot_id);
  console.log(status);
})();
```

---

### cURL

#### Basic Authentication
```bash
export API_TOKEN="your_api_token_here"
```

#### Market Data Examples

**Get Market Overview:**
```bash
curl -X GET "https://api.dhanworks.com/v1/market/overview" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Get Stock Quote:**
```bash
curl -X GET "https://api.dhanworks.com/v1/market/quote/TCS" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Get Historical Data:**
```bash
curl -X GET "https://api.dhanworks.com/v1/market/history/INFY?from_date=2025-12-01&to_date=2025-12-27&interval=1d" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

#### Portfolio Management Examples

**Get Portfolio Summary:**
```bash
curl -X GET "https://api.dhanworks.com/v1/portfolio/summary" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Get Holdings:**
```bash
curl -X GET "https://api.dhanworks.com/v1/portfolio/holdings?limit=20&offset=0" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Add Holding:**
```bash
curl -X POST "https://api.dhanworks.com/v1/portfolio/holdings" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "WIPRO",
    "quantity": 50,
    "buy_price": 400.50,
    "purchase_date": "2025-12-27"
  }'
```

**Update Holding:**
```bash
curl -X PUT "https://api.dhanworks.com/v1/portfolio/holdings/hold_xyz123" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 75,
    "buy_price": 400.50
  }'
```

**Delete Holding:**
```bash
curl -X DELETE "https://api.dhanworks.com/v1/portfolio/holdings/hold_xyz123" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

#### Analysis Examples

**Get Technical Analysis:**
```bash
curl -X GET "https://api.dhanworks.com/v1/analysis/technical/SBIN?period=20" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Get Fundamental Analysis:**
```bash
curl -X GET "https://api.dhanworks.com/v1/analysis/fundamental/MARUTI" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

#### Watchlist Examples

**Create Watchlist:**
```bash
curl -X POST "https://api.dhanworks.com/v1/watchlist" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Stocks",
    "description": "Technology sector stocks to monitor"
  }'
```

**Get Watchlists:**
```bash
curl -X GET "https://api.dhanworks.com/v1/watchlist" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Add Stock to Watchlist:**
```bash
curl -X POST "https://api.dhanworks.com/v1/watchlist/wl_abc123/symbols" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "HCLTECH"
  }'
```

**Remove Stock from Watchlist:**
```bash
curl -X DELETE "https://api.dhanworks.com/v1/watchlist/wl_abc123/symbols/HCLTECH" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

#### Alert Examples

**Create Price Alert:**
```bash
curl -X POST "https://api.dhanworks.com/v1/alerts" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BAJAJFINSV",
    "alert_type": "price",
    "condition": "above",
    "target_price": 1800.00,
    "notification_method": "email"
  }'
```

**Get Active Alerts:**
```bash
curl -X GET "https://api.dhanworks.com/v1/alerts?status=active" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Delete Alert:**
```bash
curl -X DELETE "https://api.dhanworks.com/v1/alerts/alrt_def456" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

#### Bot Automation Examples

**Create Bot:**
```bash
curl -X POST "https://api.dhanworks.com/v1/bots" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning Trend Trader",
    "symbol": "HDFC",
    "strategy": "moving_average_crossover",
    "parameters": {
      "fast_period": 12,
      "slow_period": 26,
      "quantity": 10
    },
    "enabled": true,
    "start_time": "09:30",
    "end_time": "15:30"
  }'
```

**Get Bot Status:**
```bash
curl -X GET "https://api.dhanworks.com/v1/bots/bot_ghi789" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Update Bot:**
```bash
curl -X PUT "https://api.dhanworks.com/v1/bots/bot_ghi789" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Bot Name",
    "parameters": {
      "fast_period": 10,
      "slow_period": 30,
      "quantity": 15
    }
  }'
```

**Stop Bot:**
```bash
curl -X POST "https://api.dhanworks.com/v1/bots/bot_ghi789/stop" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

**Delete Bot:**
```bash
curl -X DELETE "https://api.dhanworks.com/v1/bots/bot_ghi789" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Support and Resources

- **Documentation:** https://docs.dhanworks.com
- **Community Forum:** https://community.dhanworks.com
- **Email Support:** support@dhanworks.com
- **Status Page:** https://status.dhanworks.com
- **GitHub Repository:** https://github.com/dhanworks/api-client

---

## Changelog

### Version 1.0.0 (2025-12-27)
- Initial API release
- Market data endpoints
- Portfolio management
- Technical and fundamental analysis
- Watchlist management
- Price alerts
- Bot automation

---

## License

This API documentation is licensed under the Creative Commons Attribution 4.0 International License.

---

**Last Updated:** 2025-12-27 07:20:53 UTC
**API Version:** v1.0.0
