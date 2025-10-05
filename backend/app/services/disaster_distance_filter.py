"""
Disaster Distance Filter Service

Filters natural disaster events by geographic relevance to property location.
Prevents false positives like urban LA properties being penalized for rural wildfires.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DisasterDistanceFilter:
    """
    Filters disaster events by distance to property location
    
    Uses county-level filtering as primary method, with distance-based
    thresholds to determine risk relevance.
    """
    
    # Distance thresholds (in miles) by disaster type
    DISASTER_RELEVANCE_RADIUS = {
        'flood': {
            'direct': 10,      # Direct risk: within 10 miles
            'regional': 25,    # Regional risk: 10-25 miles
            'informational': 50  # Background data only
        },
        'fire': {
            'direct': 5,       # STRICTER: Fires need to be very close (changed from 15)
            'regional': 20,    # Regional fire risk (changed from 35)
            'informational': 75  # State background data
        },
        'tornado': {
            'direct': 25,      # Tornadoes are localized
            'regional': 50,    # Regional tornado patterns
            'informational': 100
        },
        'hurricane': {
            'direct': 50,      # Hurricanes affect large areas
            'regional': 100,   # Regional hurricane risk
            'informational': 200
        },
        'earthquake': {
            'direct': 50,      # Earthquakes affect regions
            'regional': 100,   # Seismic zone risk
            'informational': 200
        }
    }
    
    # California county coordinates (major counties)
    # Format: county_name -> (latitude, longitude)
    CALIFORNIA_COUNTY_COORDS = {
        'los angeles': (34.0522, -118.2437),
        'san diego': (32.7157, -117.1611),
        'orange': (33.7175, -117.8311),
        'riverside': (33.9533, -117.3962),
        'san bernardino': (34.1083, -117.2898),
        'santa clara': (37.3541, -121.9552),
        'alameda': (37.6017, -121.7195),
        'sacramento': (38.5816, -121.4944),
        'contra costa': (37.9298, -121.9018),
        'fresno': (36.7378, -119.7871),
        'kern': (35.3733, -118.4194),
        'san francisco': (37.7749, -122.4194),
        'ventura': (34.3705, -119.1391),
        'san mateo': (37.5630, -122.3255),
        'san joaquin': (37.9577, -121.2908),
        'stanislaus': (37.6391, -120.9971),
        'sonoma': (38.2912, -122.4580),
        'tulare': (36.2077, -118.8597),
        'santa barbara': (34.4208, -119.6982),
        'monterey': (36.6177, -121.8947),
        'placer': (39.0916, -120.8039),
        'merced': (37.3022, -120.4830),
        'santa cruz': (37.0455, -121.9590),
        'marin': (38.0834, -122.7633),
        'solano': (38.2494, -121.9018),
        'butte': (39.6277, -121.5986),
        'yolo': (38.6794, -121.8419),
        'el dorado': (38.7296, -120.5396),
        'imperial': (33.0114, -115.3631),
        'shasta': (40.7911, -122.2380),
        'madera': (37.0542, -119.7699),
        'kings': (36.0844, -119.8194),
        'napa': (38.5025, -122.2654),
        'humboldt': (40.7450, -123.8695),
        'nevada': (39.2305, -120.9994),
        'sutter': (39.0296, -121.6919),
        'mendocino': (39.3106, -123.3561),
        'yuba': (39.2727, -121.3577),
        'lake': (39.0933, -122.7583),
        'san luis obispo': (35.2827, -120.6596),
        'tehama': (40.1297, -122.2380),
        'san benito': (36.5761, -120.9874),
        'tuolumne': (37.9577, -119.9385),
        'calaveras': (38.2199, -120.5402),
        'siskiyou': (41.5985, -122.4695),
        'amador': (38.3496, -120.6499),
        'lassen': (40.6622, -120.7347),
        'glenn': (39.5985, -122.3919),
        'del norte': (41.7437, -124.0830),
        'colusa': (39.1797, -122.2411),
        'plumas': (40.0099, -120.8347),
        'mariposa': (37.4852, -119.9660),
        'inyo': (36.8316, -117.6789),
        'trinity': (40.6652, -123.1108),
        'mono': (38.0750, -118.9650),
        'modoc': (41.4452, -120.7708),
        'alpine': (38.5974, -119.8186),
        'sierra': (39.5777, -120.5213)
    }
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        
        Returns distance in miles
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in miles
        r = 3959
        
        return c * r
    
    @classmethod
    def filter_disasters_by_distance(
        cls,
        disasters: List[Dict[str, Any]],
        disaster_type: str,
        property_lat: float,
        property_lon: float,
        property_county: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Filter disasters by geographic proximity to property
        
        Args:
            disasters: List of FEMA disaster declarations
            disaster_type: 'flood', 'fire', 'tornado', 'hurricane', or 'earthquake'
            property_lat: Property latitude
            property_lon: Property longitude
            property_county: Property county name (optional, for county-level filtering)
        
        Returns:
            Dictionary with categorized disasters by distance
        """
        
        if not disasters:
            return {
                'direct_risk': [],
                'regional_risk': [],
                'informational': [],
                'total_count': 0,
                'direct_count': 0,
                'regional_count': 0,
                'filtering_method': 'none'
            }
        
        thresholds = cls.DISASTER_RELEVANCE_RADIUS.get(disaster_type, {
            'direct': 25,
            'regional': 50,
            'informational': 100
        })
        
        direct_risk = []
        regional_risk = []
        informational = []
        
        # First try county-level filtering with distance calculations
        if property_county:
            property_county_lower = property_county.lower().strip()
            
            for disaster in disasters:
                designated_area = disaster.get('designatedArea', '').lower()
                
                # Extract clean county name from designated area
                disaster_county = designated_area.split('(')[0].strip() if '(' in designated_area else designated_area
                
                # Try to get county coordinates and calculate distance
                disaster_coords = cls.CALIFORNIA_COUNTY_COORDS.get(disaster_county)
                
                if disaster_coords:
                    # Calculate distance from property to disaster county center
                    distance = cls.haversine_distance(
                        property_lat, property_lon,
                        disaster_coords[0], disaster_coords[1]
                    )
                    
                    # Classify based on actual distance, not just county match
                    if distance <= thresholds['direct']:
                        direct_risk.append(disaster)
                    elif distance <= thresholds['regional']:
                        regional_risk.append(disaster)
                    else:
                        informational.append(disaster)
                else:
                    # Unknown county coordinates
                    # If it's the same county, assume direct risk (conservative)
                    if property_county_lower in designated_area:
                        direct_risk.append(disaster)
                    else:
                        # Different county, unknown distance -> regional
                        regional_risk.append(disaster)
            
            filtering_method = 'county_level'
        
        else:
            # Fallback: treat all same-state disasters as regional
            regional_risk = disasters
            filtering_method = 'state_level'
        
        return {
            'direct_risk': direct_risk,
            'regional_risk': regional_risk,
            'informational': informational,
            'total_count': len(disasters),
            'direct_count': len(direct_risk),
            'regional_count': len(regional_risk),
            'informational_count': len(informational),
            'filtering_method': filtering_method,
            'thresholds_miles': thresholds
        }
    
    @classmethod
    def get_risk_context_message(
        cls,
        disaster_type: str,
        filtered_data: Dict[str, Any],
        property_location: str
    ) -> str:
        """
        Generate human-readable context message about disaster risk filtering
        
        Args:
            disaster_type: Type of disaster
            filtered_data: Output from filter_disasters_by_distance()
            property_location: Property location description
        
        Returns:
            Context message explaining risk assessment
        """
        
        direct_count = filtered_data['direct_count']
        regional_count = filtered_data['regional_count']
        total_count = filtered_data['total_count']
        method = filtered_data['filtering_method']
        
        disaster_label = disaster_type.title()
        
        if method == 'county_level':
            if direct_count > 0:
                return (
                    f"{disaster_label} Risk: {direct_count} event(s) occurred in or near {property_location} "
                    f"({direct_count}/{total_count} events within direct risk radius). "
                    f"This location has DIRECT {disaster_type} risk exposure."
                )
            elif regional_count > 0:
                return (
                    f"{disaster_label} Risk: {regional_count} event(s) occurred in surrounding region "
                    f"({regional_count}/{total_count} events within regional risk radius). "
                    f"{property_location} has REGIONAL but not direct {disaster_type} risk."
                )
            else:
                return (
                    f"{disaster_label} Risk: {total_count} statewide event(s), but NONE near {property_location}. "
                    f"This is an URBAN/PROTECTED location with minimal {disaster_type} risk. "
                    f"State background data provided for reference only."
                )
        
        else:  # state_level fallback
            return (
                f"{disaster_label} Risk: {total_count} statewide event(s). "
                f"Geographic filtering not available - treating as regional background risk."
            )
