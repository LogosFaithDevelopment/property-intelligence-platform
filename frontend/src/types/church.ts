/**
 * Church Submission Form Types
 * Based on FRONTEND_BUILD_PLAN.md and backend models
 */

// Entity Type Options (maps to tax_exempt_status in backend)
export const ENTITY_TYPE_OPTIONS = [
  'For Profit Company',
  'Faith Based Organization',
  'Other',
] as const;

export type EntityType = (typeof ENTITY_TYPE_OPTIONS)[number];

// Timeline Preference Options
export const TIMELINE_OPTIONS = [
  '6-12 months',
  '12-18 months',
  '18-24 months',
  'Flexible',
] as const;

export type TimelinePreference = (typeof TIMELINE_OPTIONS)[number];

// Affordability Target Options
export const AFFORDABILITY_OPTIONS = [
  '30% AMI (Extremely Low Income)',
  '50% AMI (Very Low Income)',
  '60% AMI (Low Income)',
  '80% AMI (Moderate Income)',
  'Mix of income levels',
] as const;

export type AffordabilityTarget = (typeof AFFORDABILITY_OPTIONS)[number];

// Congregation Size Options
export const CONGREGATION_SIZE_OPTIONS = [
  '<100',
  '100-300',
  '300-500',
  '500+',
] as const;

export type CongregationSize = (typeof CONGREGATION_SIZE_OPTIONS)[number];

// Leadership Support Options
export const LEADERSHIP_SUPPORT_OPTIONS = [
  'Unanimous',
  'Strong Majority',
  'Majority',
  'Mixed',
] as const;

export type LeadershipSupport = (typeof LEADERSHIP_SUPPORT_OPTIONS)[number];

// Development Involvement Level Options
export const INVOLVEMENT_LEVEL_OPTIONS = [
  'Passive partner (Logos handles everything)',
  'Active partner (church involved in decisions)',
  'Community oversight (church reviews progress)',
] as const;

export type InvolvementLevel = (typeof INVOLVEMENT_LEVEL_OPTIONS)[number];

// Revenue Sharing Preference Options
export const REVENUE_SHARING_OPTIONS = [
  '50/50 split',
  'Flexible - open to discussion',
  'Church receives fixed annual payment',
  'Church receives % of net income',
] as const;

export type RevenueSharingPreference = (typeof REVENUE_SHARING_OPTIONS)[number];

// ========== PHASE 2 & 3: LOGOS DEAL FRAMEWORK OPTIONS ==========

// Decision Making Authority Options (Phase 3)
export const DECISION_AUTHORITY_OPTIONS = [
  'pastor',
  'board',
  'congregation',
  'denomination',
] as const;

export type DecisionAuthority = (typeof DECISION_AUTHORITY_OPTIONS)[number];

// Decision Timeline Options (Phase 3)
export const DECISION_TIMELINE_OPTIONS = [
  'immediate',
  '1-3_months',
  '3-6_months',
  '6-12_months',
  'unsure',
] as const;

export type DecisionTimeline = (typeof DECISION_TIMELINE_OPTIONS)[number];

/**
 * Complete Church Submission Form Data
 * This matches the backend API payload structure
 */
export interface ChurchSubmissionFormData {
  // ========== SECTION 1: CHURCH INFORMATION ==========
  // Church Details
  church_name: string;
  legal_name?: string;
  denomination?: string;
  founded_year?: number;

  // Entity & Tax Information (NEW FIELDS)
  entity_type: EntityType; // Maps to tax_exempt_status in backend
  ein_number?: string; // Maps to tax_exempt_id in backend (format: XX-XXXXXXX)
  website?: string; // Maps to website_url in backend

  // Contact Information
  street_address: string;
  city: string;
  state: string;
  zip_code: string;
  congregation_size: CongregationSize;
  annual_budget?: number;
  primary_contact_name: string;
  primary_contact_email: string;
  primary_contact_phone: string;

  // ========== SECTION 2: PROPERTY DETAILS ==========
  // Property Location
  property_address: string;
  property_city: string;
  property_state: string;
  property_zip_code: string;
  latitude?: number;
  longitude?: number;

  // Multi-Address Support (NEW FIELDS)
  demolish_all_structures?: boolean; // Plan to demolish all existing structures
  additional_addresses?: Array<{
    address: string;
    city: string;
    state: string;
    zip_code: string;
  }>; // Additional addresses for multi-parcel properties

  // Property Characteristics
  lot_size_sqft?: number;
  lot_size_acres?: number; // Calculated from lot_size_sqft
  current_usage?: string;
  zoning_description?: string;

  // Available Build Space (NEW FIELDS)
  available_build_sqft?: number; // Maps to available_build_sqft in assessment
  build_area_notes?: string; // Maps to build_area_notes in assessment

  // ========== SECTION 3: OWNERSHIP & FINANCIAL ==========
  owns_property_free_clear: boolean; // CRITICAL - must be true
  willing_to_ground_lease: boolean;
  has_mortgage?: boolean;
  mortgage_balance?: number;
  assessed_value?: number;

  // ========== SECTION 4: CONGREGATION APPROVAL ==========
  congregation_voted: boolean;
  vote_percentage?: number; // Required if congregation_voted is true
  leadership_support: LeadershipSupport;
  denomination_approval_needed: boolean;

  // ========== SECTION 5: PARKING & DEVELOPMENT ==========
  current_parking_spaces?: number;
  parking_spaces_needed_after: number;
  special_requirements?: string;

  // ========== SECTION 6: TIMELINE & PREFERENCES ==========
  timeline_preference: TimelinePreference;
  preferred_unit_count?: number;
  affordability_target?: AffordabilityTarget;
  revenue_sharing_preference?: RevenueSharingPreference;
  development_involvement_level?: InvolvementLevel;
}

/**
 * Backend API Payload Structure
 * This is what gets sent to POST /api/v1/submissions
 */
export interface ChurchSubmissionApiPayload {
  // Church data
  church: {
    name: string;
    legal_name?: string;
    denomination?: string;
    founded_year?: number;
    tax_exempt_status: string; // entity_type maps here
    tax_exempt_id?: string; // ein_number maps here
    website_url?: string; // website maps here
    street_address: string;
    city: string;
    state: string;
    zip_code: string;
    congregation_size: string;
    annual_budget?: number;
    primary_contact_name: string;
    primary_contact_email: string;
    primary_contact_phone: string;
  };

  // Property data
  property: {
    address: string;
    city: string;
    state: string;
    zip_code: string;
    latitude?: number;
    longitude?: number;
    lot_size_sqft?: number;
    current_usage?: string;
    zoning_description?: string;
  };

  // Assessment preferences
  assessment: {
    owns_property_free_clear: boolean;
    willing_to_ground_lease: boolean;
    congregation_voted: boolean;
    vote_percentage?: number;
    leadership_support: string;
    denomination_approval_needed: boolean;
    current_parking_spaces?: number;
    parking_spaces_needed_after: number;
    special_requirements?: string;
    timeline_preference: string;
    preferred_unit_count?: number;
    affordability_target?: string;
    revenue_sharing_preference?: string;
    development_involvement_level?: string;
    available_build_sqft?: number; // NEW FIELD
    build_area_notes?: string; // NEW FIELD
  };
}

/**
 * Form Step Information
 */
export interface FormStep {
  id: number;
  title: string;
  description: string;
  fields: string[];
}

export const FORM_STEPS: FormStep[] = [
  {
    id: 1,
    title: 'Church Information',
    description: 'Tell us about your church',
    fields: ['church_name', 'entity_type', 'ein_number', 'website'],
  },
  {
    id: 2,
    title: 'Property Details',
    description: 'Information about your property',
    fields: ['property_address', 'available_build_sqft', 'build_area_notes'],
  },
  {
    id: 3,
    title: 'Ownership & Financial',
    description: 'Property ownership details',
    fields: ['owns_property_free_clear', 'willing_to_ground_lease'],
  },
  {
    id: 4,
    title: 'Congregation Approval',
    description: 'Congregation voting and support',
    fields: ['congregation_voted', 'vote_percentage', 'leadership_support'],
  },
  {
    id: 5,
    title: 'Parking & Development',
    description: 'Development requirements',
    fields: ['parking_spaces_needed_after', 'special_requirements'],
  },
  {
    id: 6,
    title: 'Timeline & Preferences',
    description: 'Your preferences and timeline',
    fields: ['timeline_preference', 'affordability_target'],
  },
];
