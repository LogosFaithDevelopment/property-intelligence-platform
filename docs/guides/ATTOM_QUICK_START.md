# 🚀 ATTOM API Quick Start

## 🔑 Setup

```bash
# API Key already configured in .env
ATTOM_API_KEY=4192abd990678013d974cbca764cc376
```

## 📝 Basic Usage

```python
from app.api_providers.attom_provider import ATTOMProvider
import os

# Initialize
provider = ATTOMProvider(api_key=os.getenv("ATTOM_API_KEY"))

# Get property details
result = await provider.get_property_detail("123 Main St", "Denver CO")
if result["success"]:
    data = result["data"]
    print(f"Property: {data['address']['street']}")
    print(f"Value: ${data['assessment']['market_value']:,}")
    print(f"Size: {data['building']['sqft']} sqft")
    print(f"Beds/Baths: {data['building']['bedrooms']}/{data['building']['bathrooms']}")

# Get valuation
avm = await provider.get_avm("123 Main St", "Denver CO")
if avm["success"]:
    print(f"Estimated Value: ${avm['data']['amount']:,}")
    print(f"Range: ${avm['data']['low']:,} - ${avm['data']['high']:,}")

# Get comparables
comps = await provider.get_sales_comparables("123 Main St", radius=0.5)
if comps["success"]:
    print(f"Found {comps['data']['count']} comparable sales")
    print(f"Median Price: ${comps['data']['median_price']:,}")
```

## ✅ Working Endpoints

| Endpoint                  | Status     | Use Case            |
| ------------------------- | ---------- | ------------------- |
| `get_property_detail()`   | ✅ Working | Full property info  |
| `get_avm()`               | ✅ Working | Property valuation  |
| `get_sales_comparables()` | ✅ Working | Recent sales nearby |
| `get_all_states()`        | ✅ Working | State list          |

## 📊 Response Structure

```python
{
    "success": True,
    "data": {
        "address": {...},
        "lot": {...},
        "building": {...},
        "assessment": {...}
    },
    "raw": {...}  # Full API response
}
```

## 🧪 Test It

```bash
# Run test suite
cd /Users/adamsilver/Desktop/property-intelligence-platform
docker-compose exec backend python test_attom_api.py
```

## 📚 Full Documentation

- **API Reference:** `/backend/ATTOM_API_REFERENCE.md`
- **Integration Summary:** `/backend/ATTOM_INTEGRATION_SUMMARY.md`
- **Complete Guide:** `/ATTOM_COMPLETE.md`

## 🎯 Next Step: Integrate!

Add to `services/property_enrichment.py`:

```python
# Enrich with ATTOM data
attom_detail = await attom_provider.get_property_detail(address)
attom_valuation = await attom_provider.get_avm(address)

# Store in database
property.attom_data = attom_detail['data']
property.estimated_value = attom_valuation['data']['amount']
```

---

**Status:** ✅ Ready for Production Use  
**API Key:** Active & Working  
**Property API:** Fully Functional
