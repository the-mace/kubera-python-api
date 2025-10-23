"""Test fixtures based on real API responses with sanitized data."""

# Portfolio list response (GET /api/v3/data/portfolio)
PORTFOLIOS_LIST_RESPONSE = [
    {
        "id": "portfolio_001",
        "name": "Test Portfolio 1",
        "currency": "USD"
    },
    {
        "id": "portfolio_002",
        "name": "Test Portfolio 2",
        "currency": "EUR"
    },
    {
        "id": "portfolio_003",
        "name": "Test Portfolio 3",
        "currency": "GBP"
    }
]

# Detailed portfolio response (GET /api/v3/data/portfolio/{id})
# This structure is based on actual API responses
PORTFOLIO_DETAIL_RESPONSE = {
    "asset": [
        # Bank account example
        {
            "id": "asset_001",
            "name": "Test Bank - Checking - 1234",
            "sectionId": "section_001",
            "sectionName": "Cash Accounts",
            "sheetId": "sheet_001",
            "sheetName": "Banks",
            "category": "asset",
            "value": {
                "amount": 5000.00,
                "currency": "USD"
            },
            "ticker": "USD",
            "tickerId": 150,
            "tickerSector": "Other",
            "quantity": 5000.00,
            "investable": "investable_cash",
            "ownership": 1,
            "subType": "cash",
            "holdingsCount": 0,
            "connection": {
                "aggregator": "plaid",
                "providerName": "Test Bank",
                "lastUpdated": None,
                "id": "connection_001",
                "accountId": "account_001"
            },
            "liquidity": "high",
            "sector": "other",
            "geography": {
                "country": "usa",
                "region": "other"
            },
            "assetClass": "cash",
            "type": "bank",
            "purchaseDate": "2024-01-15",
            "holdingPeriodInDays": 100,
            "isManual": False
        },
        # Stock example with parent account
        {
            "id": "asset_002_isin-us0378331005",
            "name": "Apple Inc",
            "sectionId": "section_002",
            "sectionName": "Taxable",
            "sheetId": "sheet_002",
            "sheetName": "Investments",
            "category": "asset",
            "value": {
                "amount": 15000.00,
                "currency": "USD"
            },
            "ticker": "AAPL",
            "tickerId": 12345,
            "tickerSubType": "cs",
            "tickerSector": "Technology",
            "exchange": "NASDAQ",
            "quantity": 100,
            "investable": "investable_easy_convert",
            "ownership": 1,
            "isin": "US0378331005",
            "subType": "stock",
            "holdingsCount": 0,
            "rate": {
                "price": 150.00,
                "currency": "USD"
            },
            "connection": {
                "aggregator": "yodlee",
                "providerName": "Test Brokerage",
                "lastUpdated": "2024-10-23T18:58:00.000Z",
                "id": "connection_002",
                "accountId": "account_002"
            },
            "parent": {
                "id": "asset_002",
                "name": "Brokerage Account - 5678"
            },
            "liquidity": "high",
            "sector": "technology",
            "geography": {
                "country": "usa",
                "region": "north america"
            },
            "assetClass": "stock",
            "type": "investment",
            "purchaseDate": "2024-04-10",
            "holdingPeriodInDays": 196,
            "isManual": True
        },
        # Mutual fund example with cost basis and tax info
        {
            "id": "asset_003_isin-us0231351067",
            "name": "Test High Yield Fund",
            "sectionId": "section_002",
            "sectionName": "Taxable",
            "sheetId": "sheet_002",
            "sheetName": "Investments",
            "category": "asset",
            "value": {
                "amount": 50000.00,
                "currency": "USD"
            },
            "ticker": "TESTHYX",
            "tickerId": 387965,
            "tickerSubType": "oef",
            "tickerSector": "Other",
            "exchange": "Nasdaq",
            "quantity": 5000.0,
            "irr": 1.1359633637348585,
            "investable": "investable_easy_convert",
            "ownership": 1,
            "isin": "US0231351067",
            "subType": "mutual fund",
            "holdingsCount": 0,
            "rate": {
                "price": 10.00,
                "currency": "USD"
            },
            "cost": {
                "amount": 48000.00,
                "currency": "USD"
            },
            "costBasisForTax": {
                "amount": 48000.00,
                "currency": "USD"
            },
            "taxRate": 30,
            "taxStatus": "taxable",
            "taxOnUnrealizedGain": {
                "amount": 600.00,
                "currency": "USD"
            },
            "connection": {
                "aggregator": "yodlee",
                "providerName": "Test Brokerage",
                "lastUpdated": "2024-10-23T19:07:22.000Z",
                "id": "connection_002",
                "accountId": "account_003"
            },
            "parent": {
                "id": "asset_003",
                "name": "Investment Account - 9012"
            },
            "liquidity": "high",
            "sector": "other",
            "geography": {
                "country": "usa",
                "region": "north america"
            },
            "assetClass": "fund",
            "type": "investment",
            "purchaseDate": "2024-06-18",
            "holdingPeriodInDays": 127,
            "isManual": True
        }
    ],
    "debt": [
        # Mortgage example
        {
            "id": "debt_001",
            "name": "Primary Residence Mortgage",
            "sectionId": "section_003",
            "sectionName": "Real Estate",
            "sheetId": "sheet_003",
            "sheetName": "Debts",
            "category": "debt",
            "value": {
                "amount": 250000.00,
                "currency": "USD"
            },
            "investable": "non_investable",
            "ownership": 1,
            "subType": "mortgage",
            "connection": {
                "aggregator": "mx",
                "providerName": "Test Mortgage Co",
                "lastUpdated": None,
                "id": "connection_003",
                "accountId": "account_004"
            },
            "type": "debt",
            "isManual": False
        }
    ],
    "insurance": [
        # Life insurance example
        {
            "id": "insurance_001",
            "name": "Term Life Insurance Policy",
            "sectionId": "section_004",
            "sectionName": "Protection",
            "sheetId": "sheet_004",
            "sheetName": "Insurance",
            "category": "insurance",
            "value": {
                "amount": 500000.00,
                "currency": "USD"
            },
            "subType": "life",
            "type": "insurance",
            "isManual": True
        }
    ],
    "netWorth": {
        "amount": 320000.00,
        "currency": "USD"
    },
    "totalAssets": {
        "amount": 570000.00,
        "currency": "USD"
    },
    "totalDebts": {
        "amount": 250000.00,
        "currency": "USD"
    }
}

# Update item response (POST /api/v3/data/item/{id})
UPDATE_ITEM_RESPONSE = {
    "id": "asset_001",
    "name": "Updated Item Name",
    "value": {
        "amount": 5500.00,
        "currency": "USD"
    },
    "description": "Updated description",
    "cost": {
        "amount": 5000.00,
        "currency": "USD"
    }
}

# Error response examples
ERROR_RESPONSE_401 = {
    "errorCode": 401,
    "message": "Invalid credentials"
}

ERROR_RESPONSE_403 = {
    "errorCode": 403,
    "message": "Insufficient permissions"
}

ERROR_RESPONSE_429 = {
    "errorCode": 429,
    "message": "Rate limit exceeded"
}

ERROR_RESPONSE_400 = {
    "errorCode": 400,
    "message": "Invalid request data"
}

# Wrapped API response format (actual API wraps data in {"data": ..., "errorCode": 0})
def wrap_api_response(data):
    """Wrap data in the standard Kubera API response format."""
    return {
        "data": data,
        "errorCode": 0
    }
