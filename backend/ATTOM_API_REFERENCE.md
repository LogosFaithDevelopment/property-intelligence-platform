# ATTOM API Integration Reference

## Official Documentation

- **Base URL**: `https://api.gateway.attomdata.com/propertyapi/v1.0.0`
- **Authentication**: API Key in header as `apikey`
- **Format**: JSON or XML (specify in `Accept` header)

## Authentication Headers

```http
Accept: application/json
apikey: YOUR_API_KEY
```

## Available Resources

### 1. Property API (`/property`)

Detailed property characteristics including lot, building, assessment, utilities, and more.

**Packages:**

- `/detail` - Comprehensive property details
- `/snapshot` - Quick property overview
- `/expandedprofile` - Full property profile with all data

**Parameters:**

- `address1` - Street address (e.g., "4529 Winona ct")
- `address2` - City and state (e.g., "Denver CO")
- `postalcode` - ZIP code
- `latitude` / `longitude` - Geo coordinates

**Example:**

```
GET https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail?address1=4529+Winona+ct&address2=Denver+CO
```

### 2. Assessment API (`/assessment`)

Property tax assessment values and history.

**Packages:**

- `/detail` - Detailed assessment data
- `/snapshot` - Quick assessment overview

### 3. AVM API (`/attomavm`)

Automated Valuation Model - estimated property values.

**Packages:**

- `/detail` - Detailed valuation with confidence scores
- `/snapshot` - Quick value estimate

**Example:**

```
GET https://api.gateway.attomdata.com/propertyapi/v1.0.0/attomavm/detail?address1=4529+Winona+ct&address2=Denver+CO
```

### 4. Sales API (`/sale`)

Recent sales transaction information.

**Packages:**

- `/detail` - Detailed sale information
- `/snapshot` - Quick sale overview

### 5. Sales History API (`/saleshistory`)

Historical sales data (up to 10 years).

**Packages:**

- `/detail` - Detailed sales history
- `/snapshot` - Quick history overview

### 6. All Events API (`/allevents`)

All recorded events on a property.

### 7. Sales Trend API (`/salestrend`)

Market trends and statistics within ZIP codes.

**Example:**

```
GET https://api.gateway.attomdata.com/propertyapi/v1.0.0/salestrend/snapshot?postalcode=80212
```

### 8. School API (`/school`)

School district and school information.

**Packages:**

- `/detail` - Detailed school data
- `/snapshot` - Quick school overview

## Search Filters

### Property Characteristics

- `minbeds` / `maxbeds` - Bedroom count
- `minbaths` / `maxbaths` - Bathroom count
- `minsqft` / `maxsqft` - Square footage
- `minyearbuilt` / `maxyearbuilt` - Year built
- `minlotsize` / `maxlotsize` - Lot size

### Geographic Filters

- `radius` - Search radius in miles
- `orderby` - Sort results (distance, price, etc.)
- `pagesize` - Results per page (default 10, max 100)
- `page` - Page number

### Date Filters

- `startdate` / `enddate` - Date range for sales
- Format: `YYYY-MM-DD`

## Response Status Codes

- **200** - Success
- **400** - Bad Request (invalid parameters)
- **401** - Unauthorized (invalid API key)
- **404** - Property not found
- **429** - Rate limit exceeded
- **500** - Internal server error

## Response Format

### Property Detail Response

```json
{
  "status": {
    "version": "1.0.0",
    "code": 0,
    "msg": "SuccessWithResult",
    "total": 1,
    "page": 1,
    "pagesize": 10
  },
  "property": [
    {
      "identifier": {
        "obPropId": 123456789,
        "apn": "1234567890"
      },
      "address": {
        "country": "US",
        "countrySubd": "CO",
        "line1": "4529 WINONA CT",
        "line2": "DENVER, CO 80212",
        "locality": "DENVER",
        "postal1": "80212",
        "postal2": "1234",
        "oneLine": "4529 WINONA CT, DENVER, CO 80212"
      },
      "lot": {
        "lotSize1": 6500,
        "lotSize2": 0.15
      },
      "building": {
        "size": {
          "universalSize": 2000,
          "livingSize": 2000
        },
        "rooms": {
          "beds": 3,
          "baths": 2
        },
        "yearBuilt": 1950
      },
      "assessment": {
        "assessed": {
          "assdTtlValue": 350000,
          "assdYear": 2024
        },
        "market": {
          "mktTtlValue": 450000
        },
        "tax": {
          "taxAmt": 4500,
          "taxYear": 2024
        }
      }
    }
  ]
}
```

## Rate Limits

- **Standard Tier**: 60 requests/minute
- **Premium Tier**: 1000 requests/minute
- Rate limit info in response headers

## Best Practices

1. **Use address1 and address2 parameters** for best results

   - address1: Street address only
   - address2: City and state

2. **Handle rate limits** - Implement exponential backoff

3. **Cache responses** - Property data changes infrequently

4. **Check status codes** - Always verify `status.code` in response

5. **Pagination** - Use `pagesize` and `page` for large result sets

## Integration in Property Intelligence Platform

### Current Implementation

The ATTOM provider (`app/api_providers/attom_provider.py`) implements:

1. **Property Detail** - Full property characteristics
2. **AVM** - Property valuation estimates
3. **Sales Comparables** - Recent nearby sales
4. **Area Snapshot** - Market trends by ZIP code

### Usage Example

```python
from app.api_providers.attom_provider import ATTOMProvider

provider = ATTOMProvider(api_key=your_api_key)

# Get property details
result = await provider.get_property_detail(
    address1="4529 Winona ct",
    address2="Denver CO"
)

# Get valuation
avm = await provider.get_avm(
    address1="4529 Winona ct",
    address2="Denver CO"
)

# Get market trends
trends = await provider.get_area_snapshot("80212")
```

## Testing

Run the test script to verify API integration:

```bash
cd backend
python test_attom_api.py
```

## API Key

Your ATTOM API key is stored in `.env`:

```
ATTOM_API_KEY=4192abd990678013d974cbca764cc376
```

---

## Area API

### Overview

The Area API provides geographic boundaries and relationships between different area types. It uses a separate base URL from the Property API.

**Base URL**: `https://api.gateway.attomdata.com/areaapi/v4.0.0`

### Geographic Area Types

| Code   | Type                    | Description                                                 |
| ------ | ----------------------- | ----------------------------------------------------------- |
| **ST** | State                   | All 50 states, DC, and US territories                       |
| **CO** | County                  | County subdivisions                                         |
| **CS** | County Subdivision      | Smaller geographic units (townships, towns)                 |
| **PL** | Place                   | Incorporated places and census designated places            |
| **ZI** | Zip Code (ZCTA)         | ZIP Code Tabulation Areas                                   |
| **N1** | Macro Neighborhood      | Large neighborhoods, regions, or master planned communities |
| **N2** | Neighborhood            | Common city-level neighborhoods                             |
| **N3** | Sub-Neighborhood        | Smaller named areas within N2 (business districts, etc.)    |
| **N4** | Residential Subdivision | Subdivisions, condos, townhomes, apartments                 |
| **DB** | School District         | School district boundaries                                  |
| **SB** | School Attendance       | School attendance area boundaries                           |
| **CB** | CBSA                    | Core Based Statistical Areas (metros)                       |

### Available Endpoints

#### 1. Area Hierarchy Lookup

Find all geographic areas that contain a specific point.

**Endpoint:** `GET /hierarchy/lookup`

**Parameters:**

- `WKTString` - Well-Known Text format point: `POINT(longitude latitude)`
- `geoType` - Type of geography: `All`, `ZI`, `N1`, `N2`, `N3`, `N4`, `DB`, `SB`, `ST`, `CO`, `PL`, `CB`

**Example:**

```
GET https://api.gateway.attomdata.com/areaapi/v4.0.0/hierarchy/lookup?WKTString=POINT(-105.0521%2039.7837)&geoType=All
```

**Use Cases:**

- Determine what neighborhood, zip code, or city a point falls within
- Find all geographic contexts for a property location
- Identify school districts and attendance zones

#### 2. Area Boundary Detail

Get the geometric boundary (polygon) for a specific area.

**Endpoint:** `GET /boundary/detail`

**Parameters:**

- `geoIdV4` - Geocode identifier (e.g., `25c781485c834372b7e7b7ef0fc0c2fa`)
- `AreaId` - Known Geo ID (e.g., `ZI80212`)
- `format` - Output format: `geojson` or `wkt`

**Example:**

```
GET https://api.gateway.attomdata.com/areaapi/v4.0.0/boundary/detail?AreaId=ZI80212&format=geojson
```

**Use Cases:**

- Display ZIP code boundaries on a map
- Show neighborhood or school district boundaries
- Calculate area coverage and overlaps

#### 3. County Lookup

Get all counties within a state.

**Endpoint:** `GET /county/lookup`

**Parameters:**

- `StateId` - State ID (e.g., `ST06` for California, `ST36` for New York)

**Example:**

```
GET https://api.gateway.attomdata.com/areaapi/v4.0.0/county/lookup?StateId=ST06
```

#### 4. State Lookup

Get all US states and their IDs.

**Endpoint:** `GET /state/lookup`

**Example:**

```
GET https://api.gateway.attomdata.com/areaapi/v4.0.0/state/lookup
```

#### 5. CBSA Lookup

Get all Core Based Statistical Areas (metros) within a state.

**Endpoint:** `GET /cbsa/lookup`

**Parameters:**

- `StateId` - State ID (e.g., `ST36`)

### Area API Response Codes

| Code     | Description                              |
| -------- | ---------------------------------------- |
| **0**    | Success - Request processed successfully |
| **-1**   | Database Connection Failed               |
| **-2**   | SQL Command Failed                       |
| **100**  | Invalid or missing input parameters      |
| **4100** | Invalid WKT (Well-Known Text)            |

### Python Usage Examples

```python
from app.api_providers.attom_provider import ATTOMProvider

provider = ATTOMProvider(api_key="your_key")

# Get all areas a point falls within
hierarchy = await provider.get_area_hierarchy(
    latitude=39.7837,
    longitude=-105.0521,
    geo_type="All"
)

# Get ZIP code boundary
boundary = await provider.get_area_boundary(
    area_id="ZI80212",
    format="geojson"
)

# Get all counties in California
counties = await provider.get_counties_in_state("ST06")

# Get all states
states = await provider.get_all_states()
```

### Integration Use Cases

1. **Property Context Enhancement**

   - Determine exact neighborhood for listings
   - Identify school districts automatically
   - Show ZIP code boundaries on property maps

2. **Market Analysis**

   - Aggregate data by neighborhood or ZIP
   - Compare properties within same geographic area
   - Identify micro-market boundaries

3. **Search & Discovery**

   - Allow users to search by neighborhood name
   - Filter properties by school district
   - Show all areas within a radius

4. **Compliance & Reporting**
   - Accurate school district assignments
   - Legal boundary definitions
   - Tax jurisdiction identification

---

## Support

- **Documentation**: https://api.developer.attomdata.com/docs
- **Support**: Check your ATTOM account dashboard for support options
