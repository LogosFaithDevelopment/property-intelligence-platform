import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@clerk/nextjs';
import apiClient from '@/lib/api-client';
import type {
  ChurchSubmissionFormData,
  ChurchSubmissionApiPayload,
} from '@/types/church';

// Utility: Recursively replace empty strings and NaN with undefined
function cleanFormData<T extends Record<string, any>>(data: T): T {
  const cleaned: Record<string, any> = {};
  for (const key in data) {
    const value = data[key];
    if (typeof value === 'string' && value.trim() === '') {
      cleaned[key] = undefined;
    } else if (typeof value === 'number' && isNaN(value)) {
      cleaned[key] = undefined;
    } else if (value && typeof value === 'object' && !Array.isArray(value)) {
      cleaned[key] = cleanFormData(value);
    } else {
      cleaned[key] = value;
    }
  }
  return cleaned as T;
}

/**
 * Convert congregation size range string to approximate number
 */
function congregationSizeToNumber(
  sizeRange: string | number | undefined,
): number | undefined {
  if (!sizeRange) return undefined;
  if (typeof sizeRange === 'number') return sizeRange;

  // Map dropdown options to approximate numbers
  const mapping: Record<string, number> = {
    '<100': 75,
    '100-300': 200,
    '300-500': 400,
    '500+': 750,
  };

  return mapping[sizeRange] || undefined;
}

/**
 * Transform form data to backend API payload
 * The backend /api/v1/submissions/ endpoint expects nested church/property/assessment structure
 */
function transformFormDataToApiPayload(
  formData: ChurchSubmissionFormData,
): any {
  // Clean the form data first
  const cleaned = cleanFormData(formData);

  // Return nested structure for submissions endpoint
  return {
    church: {
      // Church Basic Information
      name: cleaned.church_name,
      legal_name: cleaned.legal_name,
      denomination: cleaned.denomination,
      founded_year: cleaned.founded_year,

      // Tax-exempt information
      tax_exempt_status: cleaned.entity_type, // entity_type → tax_exempt_status
      tax_exempt_id: cleaned.ein_number, // ein_number → tax_exempt_id

      // Contact Information
      primary_email: cleaned.primary_contact_email,
      primary_phone: cleaned.primary_contact_phone,
      website_url: cleaned.website, // website → website_url

      // Address Information
      street_address: cleaned.street_address,
      city: cleaned.city,
      state: cleaned.state,
      zip_code: cleaned.zip_code,

      // Organization Details
      congregation_size: congregationSizeToNumber(cleaned.congregation_size), // Convert range to number
      annual_budget: cleaned.annual_budget,

      // FORM ENHANCEMENT: New Church Fields
      denominational_affiliation: cleaned.denominational_affiliation,
      member_count: cleaned.member_count,
      building_condition: cleaned.building_condition,
      site_condition_issues: cleaned.site_condition_issues,
      exploration_reasons: cleaned.exploration_reasons,
      ministries_using_property: cleaned.ministries_using_property,

      // Partnership Preferences
      partnership_goals: cleaned.special_requirements,
      timeline_preference: cleaned.timeline_preference,
    },
    property: {
      // Property Address
      street_address: cleaned.property_address,
      city: cleaned.property_city,
      state: cleaned.property_state,
      zip_code: cleaned.property_zip_code,

      // Multi-Address Support
      demolish_all_structures: cleaned.demolish_all_structures,
      additional_addresses: cleaned.additional_addresses,

      // Geospatial Data
      latitude: cleaned.latitude,
      longitude: cleaned.longitude,

      // Property Details
      lot_size_sqft: cleaned.lot_size_sqft,
      current_usage: cleaned.current_usage,
      zoning_description: cleaned.zoning_description,
      market_value_estimate: cleaned.assessed_value, // Map form's 'assessed_value' to API's 'market_value_estimate'
    },
    assessment: {
      // Ownership
      owns_property_free_clear: cleaned.owns_property_free_clear,
      willing_to_ground_lease: cleaned.willing_to_ground_lease,
      existing_debt_amount: cleaned.existing_debt_amount,

      // Congregation Approval
      congregation_voted: cleaned.congregation_voted,
      vote_percentage: cleaned.vote_percentage,
      leadership_support: cleaned.leadership_support,
      denomination_approval_needed: cleaned.denomination_approval_needed,

      // Parking
      current_parking_spaces: cleaned.current_parking_spaces,
      parking_spaces_needed_after: cleaned.parking_spaces_needed_after,
      special_requirements: cleaned.special_requirements,

      // Timeline & Preferences
      timeline_readiness: cleaned.timeline_preference, // Map timeline_preference to timeline_readiness
      preferred_unit_count: cleaned.preferred_unit_count,
      affordability_target: cleaned.affordability_target,
      revenue_sharing_preference: cleaned.revenue_sharing_preference,
      development_involvement_level: cleaned.development_involvement_level,

      // Available Build Space (NEW FIELDS)
      available_build_sqft: cleaned.available_build_sqft,
      build_area_notes: cleaned.build_area_notes,

      // FORM ENHANCEMENT: Debt & Restrictions
      has_property_debt: cleaned.has_property_debt,
      property_debt_amount: cleaned.property_debt_amount,
      property_debt_terms: cleaned.property_debt_terms,
      has_transfer_restrictions: cleaned.has_transfer_restrictions,
      transfer_restrictions_description:
        cleaned.transfer_restrictions_description,
      has_long_term_leases: cleaned.has_long_term_leases,
      long_term_leases_description: cleaned.long_term_leases_description,

      // FORM ENHANCEMENT: Project Vision
      project_components_wanted: cleaned.project_components_wanted,
      sunday_parking_needed: cleaned.sunday_parking_needed,

      // FORM ENHANCEMENT: Partnership & Timeline
      partnership_structure_preferences:
        cleaned.partnership_structure_preferences,
      decision_making_structure: cleaned.decision_making_structure,
      timeline_preference_new: cleaned.timeline_preference_new,
      reinvestment_preference: cleaned.reinvestment_preference,
      priority_ranking: cleaned.priority_ranking,

      // Property Improvement & Financing Needs
      property_improvement_needs: cleaned.property_improvement_needs,
      capital_financing_need: cleaned.capital_financing_need,
    },
  };
}

/**
 * Submit church property for review
 * POST /api/v1/churches
 */
export const useSubmitProperty = () => {
  const queryClient = useQueryClient();
  const { getToken } = useAuth();

  return useMutation({
    mutationFn: async (formData: ChurchSubmissionFormData) => {
      const payload = transformFormDataToApiPayload(formData);

      // Get Clerk auth token if user is authenticated
      const token = await getToken();
      const headers: Record<string, string> = {};

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log('🔐 Sending authenticated request with Clerk token');
      } else {
        console.log('📝 Sending unauthenticated request (public submission)');
      }

      const { data } = await apiClient.post('/api/v1/submissions/', payload, {
        headers,
      });
      return data;
    },
    onSuccess: () => {
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      queryClient.invalidateQueries({ queryKey: ['submission-status'] });
    },
    onError: (error: Error) => {
      console.error('Submission failed:', error);
      throw error;
    },
  });
};

/**
 * Check church submission status
 * GET /api/v1/submissions/my-status
 */
export const useSubmissionStatus = () => {
  return useQuery({
    queryKey: ['submission-status'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/submissions/my-status');
      return data;
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Admin-only: Fetch all submissions
 * GET /api/v1/admin/submissions
 */
interface SubmissionFilters {
  status?: 'new' | 'reviewing' | 'approved' | 'rejected';
  score_min?: number;
  score_max?: number;
  city?: string;
  state?: string;
}

export const useSubmissions = (filters?: SubmissionFilters) => {
  return useQuery({
    queryKey: ['submissions', filters],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/admin/submissions', {
        params: filters,
      });
      return data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Admin-only: Fetch single submission with full assessment
 * GET /api/v1/admin/submissions/:id
 */
export const useSubmission = (id: string | null) => {
  return useQuery({
    queryKey: ['submissions', id],
    queryFn: async () => {
      if (!id) throw new Error('Submission ID is required');
      const { data } = await apiClient.get(`/api/v1/admin/submissions/${id}`);
      return data;
    },
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Admin-only: Approve or reject submission
 * PUT /api/v1/admin/submissions/:id/status
 */
export const useUpdateSubmissionStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      status,
      notes,
    }: {
      id: string;
      status: 'approved' | 'rejected';
      notes?: string;
    }) => {
      const { data } = await apiClient.put(
        `/api/v1/admin/submissions/${id}/status`,
        {
          status,
          notes,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
    },
  });
};

/**
 * Admin-only: Generate investment report (V3)
 * GET /api/v1/reports/assessment/:id/download-v2
 */
export const useGenerateReport = () => {
  return useMutation({
    mutationFn: async (assessmentId: string) => {
      const { data } = await apiClient.get(
        `/api/v1/reports/assessment/${assessmentId}/download-v2`,
        {
          responseType: 'blob',
        },
      );
      return data;
    },
  });
};
