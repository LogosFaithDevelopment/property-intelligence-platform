#!/usr/bin/env python3
"""
Test Phase 2 & 3 Implementation
Tests debt-to-value ratio, sanctuary replacement, and partnership quality scoring
"""

import json
from datetime import datetime

import requests

# API Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "logos-secret-key-2025"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_phase2_3_scoring():
    """Test Phase 2 & 3 fields with various scenarios"""
    
    print("=" * 80)
    print("🧪 TESTING PHASE 2 & 3 IMPLEMENTATION")
    print("=" * 80)
    
    # Test Scenario 1: IDEAL PARTNER (all positive)
    print("\n" + "="*80)
    print("TEST 1: IDEAL PARTNER (All Positive Factors)")
    print("="*80)
    
    ideal_submission = {
        "church_name": "Phase2-3 Test Church - Ideal Partner",
        "contact_name": "Test Pastor",
        "contact_email": "test@example.com",
        "contact_phone": "555-0100",
        "property_address": "123 Test St, Los Angeles, CA 90001",
        "property_apn": "TEST-001-IDEAL",
        "lot_size_sqft": 15000,
        "existing_units": 0,
        "assessed_value": 1000000,
        
        # Phase 2 Fields - IDEAL (no debt, no sanctuary)
        "existing_debt_amount": 0,
        "expects_sanctuary_replacement": False,
        "sanctuary_replacement_cost_estimate": None,
        
        # Phase 3 Fields - IDEAL (all aligned)
        "decision_making_authority": "pastor",
        "decision_timeline": "1-3_months",
        "accepts_60_40_ownership": True,
        "willing_to_pay_deposit": True,
        
        # Other fields
        "project_notes": "Test submission for Phase 2/3 - Ideal scenario",
        "zoning_code": "R3"
    }
    
    response = requests.post(f"{BASE_URL}/api/submissions", json=ideal_submission, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        submission_id = data.get("id")
        print(f"✅ Submission created: ID {submission_id}")
        print(f"Expected Impact: +60 points (partnership)")
        print(f"  • No debt penalty: 0")
        print(f"  • No sanctuary penalty: 0")
        print(f"  • Pastor authority: +20")
        print(f"  • Fast timeline: +10")
        print(f"  • Accepts 60/40: +20")
        print(f"  • Willing deposit: +10")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test Scenario 2: DEAL BREAKER (high debt, sanctuary)
    print("\n" + "="*80)
    print("TEST 2: DEAL BREAKER (High Debt + Sanctuary)")
    print("="*80)
    
    deal_breaker = {
        "church_name": "Phase2-3 Test Church - Deal Breaker",
        "contact_name": "Test Pastor",
        "contact_email": "test2@example.com",
        "contact_phone": "555-0200",
        "property_address": "456 Test Ave, Los Angeles, CA 90002",
        "property_apn": "TEST-002-BREAKER",
        "lot_size_sqft": 15000,
        "existing_units": 0,
        "assessed_value": 1000000,
        
        # Phase 2 Fields - PROBLEMS (25% debt, wants sanctuary)
        "existing_debt_amount": 250000,  # 25% of 1M = deal breaker
        "expects_sanctuary_replacement": True,
        "sanctuary_replacement_cost_estimate": 500000,
        
        # Phase 3 Fields - PROBLEMS (misaligned)
        "decision_making_authority": "denomination",
        "decision_timeline": "6-12_months",
        "accepts_60_40_ownership": False,
        "willing_to_pay_deposit": False,
        
        "project_notes": "Test submission for Phase 2/3 - Deal breaker scenario",
        "zoning_code": "R3"
    }
    
    response = requests.post(f"{BASE_URL}/api/submissions", json=deal_breaker, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        submission_id = data.get("id")
        print(f"✅ Submission created: ID {submission_id}")
        print(f"Expected Impact: -60 points")
        print(f"  • 25% debt penalty: -20 (DEAL BREAKER)")
        print(f"  • Sanctuary penalty: -10")
        print(f"  • Denomination authority: -10")
        print(f"  • Slow timeline: -5")
        print(f"  • Rejects 60/40: -15 (RED FLAG)")
        print(f"  • No deposit: -5")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test Scenario 3: MIXED PROFILE
    print("\n" + "="*80)
    print("TEST 3: MIXED PROFILE (Some Good, Some Concerns)")
    print("="*80)
    
    mixed_submission = {
        "church_name": "Phase2-3 Test Church - Mixed",
        "contact_name": "Test Pastor",
        "contact_email": "test3@example.com",
        "contact_phone": "555-0300",
        "property_address": "789 Test Blvd, Los Angeles, CA 90003",
        "property_apn": "TEST-003-MIXED",
        "lot_size_sqft": 15000,
        "existing_units": 0,
        "assessed_value": 1000000,
        
        # Phase 2 Fields - MIXED (moderate debt, no sanctuary)
        "existing_debt_amount": 120000,  # 12% = moderate concern
        "expects_sanctuary_replacement": False,
        "sanctuary_replacement_cost_estimate": None,
        
        # Phase 3 Fields - MIXED
        "decision_making_authority": "board",
        "decision_timeline": "3-6_months",
        "accepts_60_40_ownership": True,
        "willing_to_pay_deposit": False,
        
        "project_notes": "Test submission for Phase 2/3 - Mixed scenario",
        "zoning_code": "R3"
    }
    
    response = requests.post(f"{BASE_URL}/api/submissions", json=mixed_submission, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        submission_id = data.get("id")
        print(f"✅ Submission created: ID {submission_id}")
        print(f"Expected Impact: +30 points")
        print(f"  • 12% debt penalty: -10 (moderate)")
        print(f"  • No sanctuary penalty: 0")
        print(f"  • Board authority: +20")
        print(f"  • Moderate timeline: +5")
        print(f"  • Accepts 60/40: +20 (GOOD!)")
        print(f"  • No deposit: -5")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test Scenario 4: EDGE CASE (congregation vote)
    print("\n" + "="*80)
    print("TEST 4: EDGE CASE (Congregation Vote)")
    print("="*80)
    
    congregation_submission = {
        "church_name": "Phase2-3 Test Church - Congregation",
        "contact_name": "Test Pastor",
        "contact_email": "test4@example.com",
        "contact_phone": "555-0400",
        "property_address": "321 Test Way, Los Angeles, CA 90004",
        "property_apn": "TEST-004-CONGREGATION",
        "lot_size_sqft": 15000,
        "existing_units": 0,
        "assessed_value": 1000000,
        
        # Phase 2 Fields - GOOD (no debt, no sanctuary)
        "existing_debt_amount": 0,
        "expects_sanctuary_replacement": False,
        
        # Phase 3 Fields - CONGREGATION (slower but acceptable)
        "decision_making_authority": "congregation",
        "decision_timeline": "3-6_months",
        "accepts_60_40_ownership": True,
        "willing_to_pay_deposit": True,
        
        "project_notes": "Test submission for Phase 2/3 - Congregation vote",
        "zoning_code": "R3"
    }
    
    response = requests.post(f"{BASE_URL}/api/submissions", json=congregation_submission, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        submission_id = data.get("id")
        print(f"✅ Submission created: ID {submission_id}")
        print(f"Expected Impact: +40 points")
        print(f"  • No debt penalty: 0")
        print(f"  • No sanctuary penalty: 0")
        print(f"  • Congregation authority: +5 (slower)")
        print(f"  • Moderate timeline: +5")
        print(f"  • Accepts 60/40: +20")
        print(f"  • Willing deposit: +10")
    else:
        print(f"❌ Error: {response.text}")
    
    print("\n" + "="*80)
    print("✅ TEST SUBMISSIONS CREATED")
    print("="*80)
    print("\n📋 Next Steps:")
    print("1. Check the backend logs for scoring details")
    print("2. Run assessments on these submissions")
    print("3. Verify the scores match expected impacts")
    print("4. Check that phase2_deal_breakers and phase3_partnership_quality appear in output")
    print("\nCommand to check logs:")
    print("docker-compose logs backend | grep -E '(🚨|✓|⚠|△)'")

if __name__ == "__main__":
    test_phase2_3_scoring()
