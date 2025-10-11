"""
Test distance calculations for LA County fires

Shows which fires are truly within 15 miles of downtown LA
vs which are in distant parts of the county
"""

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in miles"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 3959  # Earth radius in miles
    return c * r

# Downtown LA property location
downtown_la = (34.0402871, -118.2647559)

# LA County center (from our lookup table)
la_county_center = (34.0522, -118.2437)

# Known fire locations (approximate)
fire_locations = {
    "LA County Center (generic)": (34.0522, -118.2437),  # Used for all LA County fires currently
    "Palisades Fire (Malibu)": (34.0522, -118.5260),     # ~20 miles west
    "Eaton Fire (Altadena)": (34.1897, -118.1248),       # ~15 miles northeast  
    "Griffith Park": (34.1367, -118.2941),               # ~7 miles north
    "Downtown LA": downtown_la
}

print("=" * 80)
print("DISTANCE FROM DOWNTOWN LA TO FIRE LOCATIONS")
print("=" * 80)

for location, coords in fire_locations.items():
    distance = haversine_distance(
        downtown_la[0], downtown_la[1],
        coords[0], coords[1]
    )
    print(f"\n{location}:")
    print(f"  Coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
    print(f"  Distance: {distance:.1f} miles")
    
    if distance <= 15:
        print(f"  ✅ DIRECT RISK (within 15 mile threshold)")
    elif distance <= 35:
        print(f"  ⚠️  REGIONAL RISK (15-35 miles)")
    else:
        print(f"  ℹ️  INFORMATIONAL (beyond 35 miles)")

print("\n" + "=" * 80)
print("CURRENT PROBLEM:")
print("=" * 80)
print("FEMA data only provides COUNTY names, not exact fire coordinates.")
print("Current system uses LA County CENTER (34.05°N, -118.24°W) for ALL LA fires.")
print("\nDistance from downtown LA to LA County center: ~1.5 miles")
print("This means ALL LA County fires show as 'nearby' even if they're 20+ miles away!")
print("\nSOLUTION:")
print("Updated filter to calculate distance to county CENTER, not just match county name.")
print("Now Palisades Fire (Malibu) will show ~20 miles, not 1.5 miles.")
