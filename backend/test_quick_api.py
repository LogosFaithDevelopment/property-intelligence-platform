"""
Quick API Test - Tests core endpoints without waiting for background tasks
"""

import asyncio
from datetime import datetime

import httpx

BASE_URL = "http://localhost:8000/api/v1"
TEST_TIMESTAMP = str(int(datetime.now().timestamp()))
TEST_EMAIL = f"quick_test_{TEST_TIMESTAMP}@example.com"
TEST_TAX_ID = f"{TEST_TIMESTAMP[:2]}-{TEST_TIMESTAMP[2:9]}"


async def quick_test():
    """Quick test of core API functionality"""
    
    print("=" * 70)
    print("QUICK API TEST - No Background Tasks")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        
        # TEST 1: Create Church
        print("📋 TEST 1: Create Church")
        church_data = {
            "name": "Quick Test Church",
            "primary_contact_name": "Test Pastor",
            "primary_email": TEST_EMAIL,
            "primary_phone": "310-555-9999",
            "street_address": "789 Test Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "tax_exempt_id": TEST_TAX_ID,
            "is_501c3_verified": True,
            "congregation_size": 200
        }
        
        try:
            response = await client.post(f"{BASE_URL}/churches/", json=church_data)
            if response.status_code == 201:
                church = response.json()
                church_id = church["id"]
                print(f"✅ SUCCESS: Church ID {church_id}")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(response.text)
                return
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return
        
        print()
        
        # TEST 2: Create Property
        print("🏢 TEST 2: Create Property")
        property_data = {
            "church_id": church_id,
            "name": "Test Property",
            "street_address": "1640 Maple Ave",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "lot_size_sqft": 25000,
            "property_type": "parking_lot",
            "ownership_status": "owned_outright"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/properties/", json=property_data)
            if response.status_code == 201:
                property_obj = response.json()
                property_id = property_obj["id"]
                print(f"✅ SUCCESS: Property ID {property_id}")
                print(f"   Address: {property_obj['full_address']}")
                print(f"   Lot Size: {property_obj['lot_size_sqft']} sqft")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(response.text)
                return
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return
        
        print()
        
        # TEST 3: Get Property Details
        print("📊 TEST 3: Get Property Details")
        try:
            response = await client.get(f"{BASE_URL}/properties/{property_id}")
            if response.status_code == 200:
                property_obj = response.json()
                print(f"✅ SUCCESS: Retrieved property")
                print(f"   Coordinates: {property_obj.get('latitude')}, {property_obj.get('longitude')}")
                print(f"   (Note: Will be None until enrichment runs)")
            else:
                print(f"❌ FAILED: {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
        
        # TEST 4: Manually trigger enrichment (won't wait)
        print("🔄 TEST 4: Trigger Property Enrichment")
        try:
            response = await client.post(f"{BASE_URL}/properties/{property_id}/enrich")
            if response.status_code in [200, 202]:
                print(f"✅ SUCCESS: Enrichment triggered (runs in background)")
            else:
                print(f"⚠️  Status: {response.status_code}")
                print(f"   Note: Enrichment endpoint may not exist yet")
        except Exception as e:
            print(f"⚠️  Note: {e}")
        
        print()
        
        # TEST 5: Create Assessment (without waiting for completion)
        print("📝 TEST 5: Create Assessment")
        assessment_data = {
            "church_id": church_id,
            "property_id": property_id,
            "congregation_approval": True,
            "leadership_support": "strong",  # String, not integer
            "timeline_readiness": "6_TO_12_MONTHS",
            "preferred_unit_count": 50,
            "affordability_target": "60_80_AMI",
            "revenue_sharing_preference": "GROUND_LEASE",
            "development_involvement_level": "COLLABORATIVE",
            "priority": "HIGH"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/assessments/", json=assessment_data)
            if response.status_code == 201:
                assessment = response.json()
                assessment_id = assessment["id"]
                print(f"✅ SUCCESS: Assessment ID {assessment_id}")
                print(f"   Status: {assessment.get('status')}")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(response.text)
                return
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return
        
        print()
        
        # TEST 6: List All Churches
        print("📋 TEST 6: List All Churches")
        try:
            response = await client.get(f"{BASE_URL}/churches/?page=1&size=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {data.get('total', 0)} total churches")
                print(f"   Current page has {len(data.get('items', []))} churches")
            else:
                print(f"❌ FAILED: {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
        
        # TEST 7: List All Properties
        print("🏢 TEST 7: List All Properties")
        try:
            response = await client.get(f"{BASE_URL}/properties/?page=1&size=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {data.get('total', 0)} total properties")
                print(f"   Current page has {len(data.get('items', []))} properties")
            else:
                print(f"❌ FAILED: {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
        
        # TEST 8: List All Assessments
        print("📊 TEST 8: List All Assessments")
        try:
            response = await client.get(f"{BASE_URL}/assessments/?page=1&size=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found {data.get('total', 0)} total assessments")
                print(f"   Current page has {len(data.get('items', []))} assessments")
            else:
                print(f"❌ FAILED: {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
        print("=" * 70)
        print("✅ QUICK TEST COMPLETE")
        print("=" * 70)
        print()
        print("NOTES:")
        print("- Property enrichment runs in background (not tested here)")
        print("- AI assessment processing runs in background (not tested here)")
        print("- To test background tasks, implement proper task queue (Arq/Celery)")
        print()


if __name__ == "__main__":
    asyncio.run(quick_test())
