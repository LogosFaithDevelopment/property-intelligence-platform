/**
 * Admin Submission Detail Page - SIMPLIFIED
 * View detailed information about a single submission
 */

'use client';

import { use, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { getApiBaseUrl } from '@/lib/api-client';
import {
  Building2,
  MapPin,
  Mail,
  Phone,
  Globe,
  Calendar,
  Users,
  DollarSign,
  ArrowLeft,
  CheckCircle,
  XCircle,
  Loader2,
  MessageSquare,
  TrendingUp,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface SubmissionDetail {
  id: number;
  status: string;
  overall_score: number | null;
  created_at: string;
  updated_at: string;
  reviewer_notes: string | null;

  // Church data
  church_id: number;
  church_name: string;
  church_legal_name: string | null;
  church_denomination: string | null;
  church_founded_year: number | null;
  church_tax_exempt_status: string | null;
  church_tax_exempt_id: string | null;
  church_primary_email: string;
  church_primary_phone: string | null;
  church_website_url: string | null;
  church_street_address: string | null;
  church_city: string | null;
  church_state: string | null;
  church_zip_code: string | null;
  church_congregation_size: number | null;
  church_annual_budget: number | null;

  // NEW: Enhanced Church Fields
  church_denominational_affiliation: string | null;
  church_member_count: number | null;
  church_building_condition: string | null;
  church_site_condition_issues: string[] | null;
  church_exploration_reasons: string[] | null;
  church_ministries_using_property: string | null;

  // Property data
  property_id: number;
  property_street_address: string | null;
  property_city: string | null;
  property_state: string | null;
  property_zip_code: string | null;
  property_type: string | null;
  property_lot_size_sqft: number | null;
  property_lot_size_acres: number | null;
  property_current_usage: string | null;
  property_zoning_description: string | null;
  property_assessed_value: number | null;
  property_data_sources: string | null;
  property_building_sqft: number | null;
  property_year_built: number | null;
  property_market_value_estimate: number | null;

  // Assessment custom fields (user-provided)
  available_build_sqft: number | null;
  available_build_acres: number | null;

  // Ownership & Financial (existing debt from assessment form)
  existing_debt_amount: number | null;

  // Manual form fields (from current 2-section questionnaire)
  special_requirements: string | null;
  property_improvement_needs: string[] | null; // Array of improvement needs
  capital_financing_need: string | null;

  // NEW: Enhanced Assessment Fields
  has_property_debt: boolean | null;
  property_debt_amount: number | null;
  property_debt_terms: string | null;
  has_transfer_restrictions: boolean | null;
  transfer_restrictions_description: string | null;
  has_long_term_leases: boolean | null;
  long_term_leases_description: string | null;
  project_components_wanted: string[] | null;
  sunday_parking_needed: number | null;
  partnership_structure_preferences: string[] | null;
  decision_making_structure: string[] | null;
  timeline_preference_new: string | null;
  reinvestment_preference: string | null;

  // Assessment data (enriched)
  financial_projections: any | null;
  market_analysis: any | null;
  risk_factors: any | null;
}

export default function AdminSubmissionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { getToken } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  // State for dialogs
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [showCommentDialog, setShowCommentDialog] = useState(false);
  const [notes, setNotes] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [comment, setComment] = useState('');

  // Fetch submission details
  const { data: submission, isLoading } = useQuery<SubmissionDetail>({
    queryKey: ['admin-submission-detail', id],
    queryFn: async () => {
      const token = await getToken();
      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/admin/stats/submissions/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error('Failed to fetch submission details');
      }

      return response.json();
    },
  });

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/admin/submissions/${id}/approve`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ notes }),
        },
      );
      if (!response.ok) throw new Error('Failed to approve submission');
      return response.json();
    },
    onSuccess: () => {
      toast.success('Submission approved successfully!');
      setShowApproveDialog(false);
      setNotes('');
      queryClient.invalidateQueries({
        queryKey: ['admin-submission-detail', id],
      });
    },
    onError: () => {
      toast.error('Failed to approve submission');
    },
  });

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/admin/submissions/${id}/reject`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ reason: rejectReason, notes }),
        },
      );
      if (!response.ok) throw new Error('Failed to reject submission');
      return response.json();
    },
    onSuccess: () => {
      toast.success('Submission rejected');
      setShowRejectDialog(false);
      setRejectReason('');
      setNotes('');
      queryClient.invalidateQueries({
        queryKey: ['admin-submission-detail', id],
      });
    },
    onError: () => {
      toast.error('Failed to reject submission');
    },
  });

  // Comment mutation
  const commentMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const response = await fetch(
        `${getApiBaseUrl()}/api/v1/admin/submissions/${id}/comment`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ comment }),
        },
      );
      if (!response.ok) throw new Error('Failed to add comment');
      return response.json();
    },
    onSuccess: () => {
      toast.success('Comment added successfully!');
      setShowCommentDialog(false);
      setComment('');
      queryClient.invalidateQueries({
        queryKey: ['admin-submission-detail', id],
      });
    },
    onError: () => {
      toast.error('Failed to add comment');
    },
  });

  // Helper to parse enriched data from property_data_sources
  const getSmartyData = () => {
    if (!submission?.property_data_sources) return null;

    try {
      const dataSources = JSON.parse(submission.property_data_sources);
      const smartyData = dataSources?.smarty_data?.data;
      return smartyData || null;
    } catch (error) {
      console.error('Error parsing property data sources:', error);
      return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'DRAFT':
        return 'bg-gray-100 text-gray-800';
      case 'SUBMITTED':
        return 'bg-yellow-100 text-yellow-800';
      case 'PROCESSING':
        return 'bg-blue-100 text-blue-800';
      case 'COMPLETED':
        return 'bg-purple-100 text-purple-800';
      case 'REVIEWED':
        return 'bg-indigo-100 text-indigo-800';
      case 'APPROVED':
        return 'bg-green-100 text-green-800';
      case 'REJECTED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-96'>
        <div className='text-center'>
          <Loader2 className='h-12 w-12 animate-spin text-blue-600 mx-auto mb-4' />
          <p className='text-gray-600'>Loading submission details...</p>
        </div>
      </div>
    );
  }

  if (!submission) {
    return (
      <div className='text-center py-12'>
        <p className='text-red-600'>Submission not found</p>
      </div>
    );
  }

  return (
    <div className='max-w-5xl mx-auto w-full mt-2.5'>
      {/* Header */}
      <div className='mb-4 sm:mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
        <div className='flex items-center gap-4'>
          <Link href='/admin/submissions'>
            <Button variant='outline' size='icon'>
              <ArrowLeft className='h-4 w-4' />
            </Button>
          </Link>
          <div>
            <h1 className='text-xl sm:text-2xl lg:text-3xl font-bold font-[family-name:var(--font-safe-light-accent)]'>
              {submission.church_name}
            </h1>
            <p className='text-sm text-gray-600'>
              Submission ID: {submission.id}
            </p>
            {submission.property_street_address && (
              <p className='text-xs sm:text-sm text-gray-500'>
                {submission.property_street_address}
              </p>
            )}
          </div>
        </div>
        <div className='flex flex-col gap-2 items-start sm:items-end'>
          <Badge
            className={getStatusColor(submission.status)}
            variant='outline'
          >
            {submission.status}
          </Badge>
          {submission.overall_score && (
            <div className='text-left sm:text-right'>
              <div className='text-xl sm:text-2xl font-bold text-blue-600'>
                {submission.overall_score.toFixed(1)}
              </div>
              <div className='text-xs text-gray-500'>Overall Score</div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions - AI Assessment & Download */}
      <div className='mb-4 sm:mb-6 grid grid-cols-1 sm:grid-cols-2 gap-3'>
        <Link href={`/admin/submissions/${id}/assessment`}>
          <Button
            variant='default'
            className='w-full py-4 sm:py-6 text-base sm:text-lg bg-blue-600 hover:bg-blue-700'
            disabled={!submission.overall_score}
          >
            <TrendingUp className='h-4 w-5 sm:h-5 sm:w-5 mr-2 flex-shrink-0' />
            <span className='truncate'>
              {submission.overall_score
                ? 'Full Development Analysis'
                : 'Analysis Pending...'}
            </span>
          </Button>
        </Link>
        <Button
          onClick={async () => {
            try {
              toast.loading('Generating report...', { id: 'download-report' });

              const token = await getToken();
              const response = await fetch(
                `${getApiBaseUrl()}/api/v1/reports/assessment/${id}/download-v2`,
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                },
              );

              if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Logos_Assessment_${id}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                toast.success('Report downloaded successfully!', {
                  id: 'download-report',
                });
              } else {
                const errorText = await response.text();
                console.error('Download error:', errorText);
                toast.error('Failed to download report. Please try again.', {
                  id: 'download-report',
                });
              }
            } catch (error) {
              console.error('Unexpected error:', error);
              toast.error('Failed to download report. Please try again.', {
                id: 'download-report',
              });
            }
          }}
          className='w-full py-4 sm:py-6 px-4 sm:px-8 text-base sm:text-lg bg-gradient-to-r from-yellow-500 to-yellow-700 hover:from-yellow-600 hover:to-yellow-800'
          disabled={!submission.overall_score}
        >
          <span className='truncate'>Download Summary Report</span>
        </Button>
      </div>

      {/* Approve Dialog */}
      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Submission</DialogTitle>
            <DialogDescription>
              This will mark the submission as approved. You can add optional
              notes.
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder='Add notes (optional)...'
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={4}
          />
          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => setShowApproveDialog(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending}
              className='bg-green-600 hover:bg-green-700'
            >
              {approveMutation.isPending ? 'Approving...' : 'Approve'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Submission</DialogTitle>
            <DialogDescription>
              Please provide a reason for rejection. This will be recorded in
              the system.
            </DialogDescription>
          </DialogHeader>
          <div className='space-y-4'>
            <div>
              <label className='text-sm font-medium'>Rejection Reason *</label>
              <Textarea
                placeholder='Why is this submission being rejected?'
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                rows={3}
                className='mt-1'
              />
            </div>
            <div>
              <label className='text-sm font-medium'>
                Additional Notes (Optional)
              </label>
              <Textarea
                placeholder='Any additional context...'
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className='mt-1'
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => setShowRejectDialog(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => rejectMutation.mutate()}
              disabled={!rejectReason.trim() || rejectMutation.isPending}
              variant='destructive'
            >
              {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Comment Dialog */}
      <Dialog open={showCommentDialog} onOpenChange={setShowCommentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Comment</DialogTitle>
            <DialogDescription>
              Add an internal comment or note about this submission.
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder='Enter your comment...'
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={4}
          />
          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => setShowCommentDialog(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => commentMutation.mutate()}
              disabled={!comment.trim() || commentMutation.isPending}
            >
              {commentMutation.isPending ? 'Adding...' : 'Add Comment'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Entity Information */}
      <Card className='mb-4 sm:mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
            <Building2 className='h-5 w-5' />
            Entity Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6'>
            <div>
              <label className='text-sm font-medium text-gray-500'>
                Entity Name
              </label>
              <p className='mt-1 font-semibold text-lg'>
                {submission.church_name}
              </p>
            </div>
            <div>
              <label className='text-sm font-medium text-gray-500'>
                Entity Type
              </label>
              <p className='mt-1'>
                {submission.church_tax_exempt_status || 'N/A'}
              </p>
            </div>
            {submission.church_website_url && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Website
                </label>
                <p className='mt-1'>
                  <a
                    href={submission.church_website_url}
                    target='_blank'
                    rel='noopener noreferrer'
                    className='text-blue-600 hover:underline flex items-center gap-1'
                  >
                    <Globe className='h-4 w-4' />
                    {submission.church_website_url}
                  </a>
                </p>
              </div>
            )}
            <div>
              <label className='text-sm font-medium text-gray-500'>
                Submitted
              </label>
              <p className='mt-1 flex items-center gap-1'>
                <Calendar className='h-4 w-4 text-gray-500' />
                {new Date(submission.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Primary Contact */}
          <div className='pt-4 border-t'>
            <h3 className='text-sm font-semibold text-gray-700 mb-3'>
              Primary Contact
            </h3>
            <div className='space-y-2'>
              <div className='flex items-center gap-2'>
                <Mail className='h-4 w-4 text-gray-500' />
                <a
                  href={`mailto:${submission.church_primary_email}`}
                  className='text-blue-600 hover:underline'
                >
                  {submission.church_primary_email}
                </a>
              </div>
              {submission.church_primary_phone && (
                <div className='flex items-center gap-2'>
                  <Phone className='h-4 w-4 text-gray-500' />
                  <a
                    href={`tel:${submission.church_primary_phone}`}
                    className='text-blue-600 hover:underline'
                  >
                    {submission.church_primary_phone}
                  </a>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ownership & Financial */}
      {(submission.property_assessed_value ||
        submission.property_market_value_estimate ||
        submission.existing_debt_amount) && (
        <Card className='mb-4 sm:mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
              <DollarSign className='h-5 w-5' />
              Ownership & Financial
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              {submission.property_assessed_value && (
                <div>
                  <label className='text-sm font-medium text-gray-500'>
                    Property Assessed Value (City/County)
                  </label>
                  <p className='mt-1 text-lg font-semibold'>
                    ${submission.property_assessed_value.toLocaleString()}
                  </p>
                </div>
              )}
              {submission.property_market_value_estimate && (
                <div>
                  <label className='text-sm font-medium text-gray-500'>
                    Owner Reported Value
                  </label>
                  <p className='mt-1 text-lg font-semibold'>
                    $
                    {submission.property_market_value_estimate.toLocaleString()}
                  </p>
                </div>
              )}
              {submission.existing_debt_amount && (
                <div>
                  <label className='text-sm font-medium text-gray-500'>
                    Existing Debt Amount
                  </label>
                  <p className='mt-1 text-lg font-semibold'>
                    ${submission.existing_debt_amount.toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Property Needs & Financing */}
      {(submission.property_improvement_needs ||
        submission.capital_financing_need ||
        submission.special_requirements) && (
        <Card className='mb-4 sm:mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
              <DollarSign className='h-5 w-5' />
              Property Needs & Financing
            </CardTitle>
          </CardHeader>
          <CardContent>
            {submission.property_improvement_needs &&
              Array.isArray(submission.property_improvement_needs) &&
              submission.property_improvement_needs.length > 0 && (
                <div className='mb-4'>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Property Improvement Needs
                  </label>
                  <div className='flex flex-wrap gap-2'>
                    {submission.property_improvement_needs.map(
                      (need: string) => {
                        const labels: Record<string, string> = {
                          hvac: 'HVAC/AC System',
                          roof: 'Roof',
                          landscaping: 'Landscaping',
                          painting: 'Painting',
                          interior: 'Interior Improvements',
                          other: 'Other',
                        };
                        return (
                          <Badge key={need} variant='secondary'>
                            {labels[need] || need}
                          </Badge>
                        );
                      },
                    )}
                  </div>
                </div>
              )}
            {submission.capital_financing_need && (
              <div className='mb-4'>
                <label className='text-sm font-medium text-gray-500 block mb-2'>
                  Capital/Financing Need
                </label>
                <p className='text-sm text-gray-700 bg-gray-50 p-3 rounded-md'>
                  {submission.capital_financing_need}
                </p>
              </div>
            )}
            {submission.special_requirements && (
              <div>
                <label className='text-sm font-medium text-gray-500 block mb-2'>
                  Special Requirements / Considerations
                </label>
                <p className='text-sm text-gray-700 bg-gray-50 p-3 rounded-md'>
                  {submission.special_requirements}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Church Details & Vision */}
      {(submission.church_denominational_affiliation ||
        submission.church_member_count ||
        submission.church_building_condition ||
        (submission.church_site_condition_issues &&
          submission.church_site_condition_issues.length > 0) ||
        (submission.church_exploration_reasons &&
          submission.church_exploration_reasons.length > 0) ||
        submission.church_ministries_using_property) && (
        <Card className='mb-4 sm:mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
              <Building2 className='h-5 w-5' />
              Church Details & Vision
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            {submission.church_denominational_affiliation && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Denominational Affiliation
                </label>
                <p className='mt-1 text-sm'>
                  <Badge variant='outline'>
                    {submission.church_denominational_affiliation
                      .split('_')
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(' ')}
                  </Badge>
                </p>
              </div>
            )}
            {submission.church_member_count && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Member Count
                </label>
                <p className='mt-1 font-semibold'>
                  {submission.church_member_count.toLocaleString()} members
                </p>
              </div>
            )}
            {submission.church_building_condition && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Building Condition
                </label>
                <p className='mt-1'>
                  <Badge variant='secondary'>
                    {submission.church_building_condition
                      .split('_')
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(' ')}
                  </Badge>
                </p>
              </div>
            )}
            {submission.church_site_condition_issues &&
              submission.church_site_condition_issues.length > 0 && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Site Condition Issues
                  </label>
                  <div className='flex flex-wrap gap-2'>
                    {submission.church_site_condition_issues.map(
                      (issue: string) => (
                        <Badge key={issue} variant='secondary'>
                          {issue
                            .split('_')
                            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                            .join(' ')}
                        </Badge>
                      ),
                    )}
                  </div>
                </div>
              )}
            {submission.church_exploration_reasons &&
              submission.church_exploration_reasons.length > 0 && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Reasons for Exploring
                  </label>
                  <div className='flex flex-wrap gap-2'>
                    {submission.church_exploration_reasons.map(
                      (reason: string) => (
                        <Badge key={reason} variant='outline'>
                          {reason
                            .split('_')
                            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                            .join(' ')}
                        </Badge>
                      ),
                    )}
                  </div>
                </div>
              )}
            {submission.church_ministries_using_property && (
              <div>
                <label className='text-sm font-medium text-gray-500 block mb-2'>
                  Current Ministries Using Property
                </label>
                <p className='text-sm text-gray-700 bg-gray-50 p-3 rounded-md'>
                  {submission.church_ministries_using_property}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Property Debt & Restrictions */}
      {(submission.has_property_debt ||
        submission.has_transfer_restrictions ||
        submission.has_long_term_leases) && (
        <Card className='mb-4 sm:mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
              <DollarSign className='h-5 w-5' />
              Property Debt & Restrictions
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            {submission.has_property_debt && (
              <div>
                <label className='text-sm font-medium text-gray-500 block mb-2'>
                  Property Debt
                </label>
                {submission.property_debt_amount && (
                  <p className='font-semibold text-lg mb-2'>
                    ${submission.property_debt_amount.toLocaleString()}
                  </p>
                )}
                {submission.property_debt_terms && (
                  <p className='text-sm text-gray-700 bg-gray-50 p-3 rounded-md'>
                    {submission.property_debt_terms}
                  </p>
                )}
              </div>
            )}
            {submission.has_transfer_restrictions &&
              submission.transfer_restrictions_description && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Transfer Restrictions
                  </label>
                  <p className='text-sm text-gray-700 bg-gray-50 p-3 rounded-md'>
                    {submission.transfer_restrictions_description}
                  </p>
                </div>
              )}
            {submission.has_long_term_leases &&
              submission.long_term_leases_description && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Long-term Leases
                  </label>
                  <p className='text-sm text-gray-700 bg-gray-50 p-3 rounded-md'>
                    {submission.long_term_leases_description}
                  </p>
                </div>
              )}
          </CardContent>
        </Card>
      )}

      {/* Project Vision & Preferences */}
      {((submission.project_components_wanted &&
        submission.project_components_wanted.length > 0) ||
        submission.sunday_parking_needed ||
        (submission.partnership_structure_preferences &&
          submission.partnership_structure_preferences.length > 0) ||
        (submission.decision_making_structure &&
          submission.decision_making_structure.length > 0) ||
        submission.timeline_preference_new ||
        submission.reinvestment_preference) && (
        <Card className='mb-4 sm:mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
              <TrendingUp className='h-5 w-5' />
              Project Vision & Partnership Preferences
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-4'>
            {submission.project_components_wanted &&
              submission.project_components_wanted.length > 0 && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Desired Project Components
                  </label>
                  <div className='flex flex-wrap gap-2'>
                    {submission.project_components_wanted.map(
                      (component: string) => (
                        <Badge key={component} variant='secondary'>
                          {component
                            .split('_')
                            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                            .join(' ')}
                        </Badge>
                      ),
                    )}
                  </div>
                </div>
              )}
            {submission.sunday_parking_needed && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Sunday Parking Spaces Needed
                </label>
                <p className='mt-1 font-semibold'>
                  {submission.sunday_parking_needed} spaces
                </p>
              </div>
            )}
            {submission.partnership_structure_preferences &&
              submission.partnership_structure_preferences.length > 0 && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Partnership Structure Preferences
                  </label>
                  <div className='flex flex-wrap gap-2'>
                    {submission.partnership_structure_preferences.map(
                      (pref: string) => (
                        <Badge key={pref} variant='outline'>
                          {pref
                            .split('_')
                            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                            .join(' ')}
                        </Badge>
                      ),
                    )}
                  </div>
                </div>
              )}
            {submission.decision_making_structure &&
              submission.decision_making_structure.length > 0 && (
                <div>
                  <label className='text-sm font-medium text-gray-500 block mb-2'>
                    Decision Makers
                  </label>
                  <div className='flex flex-wrap gap-2'>
                    {submission.decision_making_structure.map(
                      (decision: string) => (
                        <Badge key={decision} variant='secondary'>
                          {decision.charAt(0).toUpperCase() + decision.slice(1)}
                        </Badge>
                      ),
                    )}
                  </div>
                </div>
              )}
            {submission.timeline_preference_new && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Timeline Preference
                </label>
                <p className='mt-1'>
                  <Badge>
                    {submission.timeline_preference_new
                      .replace('_', '-')
                      .split('-')
                      .map((w, i) => (i === 0 ? w : w + ' months'))
                      .join(' ')}
                  </Badge>
                </p>
              </div>
            )}
            {submission.reinvestment_preference && (
              <div>
                <label className='text-sm font-medium text-gray-500'>
                  Reinvestment Preference
                </label>
                <p className='mt-1'>
                  <Badge variant='outline'>
                    {submission.reinvestment_preference
                      .split('_')
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(' ')}
                  </Badge>
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Notes Section */}
      <Card className='mb-4 sm:mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2 text-lg sm:text-xl'>
            <MessageSquare className='h-5 w-5' />
            Notes
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Existing Notes Display */}
          {submission.reviewer_notes && (
            <div className='mb-6'>
              <div className='space-y-3'>
                {/* Parse and display notes with user colors */}
                {submission.reviewer_notes.split('\n\n').map((note, index) => {
                  // Extract username and timestamp from note format
                  // Format: "💬 Username (2024-01-01 12:00 UTC): Message"
                  const userMatch = note.match(/^[💬✅❌🔄]\s*(.+?)\s*\(/);
                  const timestampMatch = note.match(/\((.+?)\)/);
                  const userName = userMatch ? userMatch[1] : 'Admin User';
                  const timestamp = timestampMatch ? timestampMatch[1] : '';

                  // Hash the username to get consistent color
                  const hashCode = (str: string) => {
                    let hash = 0;
                    for (let i = 0; i < str.length; i++) {
                      const char = str.charCodeAt(i);
                      hash = (hash << 5) - hash + char;
                      hash = hash & hash; // Convert to 32bit integer
                    }
                    return Math.abs(hash);
                  };

                  // Color options for different users
                  const colorPairs = [
                    {
                      bg: 'bg-blue-50',
                      border: 'border-blue-200',
                      text: 'text-blue-700',
                    },
                    {
                      bg: 'bg-green-50',
                      border: 'border-green-200',
                      text: 'text-green-700',
                    },
                    {
                      bg: 'bg-purple-50',
                      border: 'border-purple-200',
                      text: 'text-purple-700',
                    },
                    {
                      bg: 'bg-amber-50',
                      border: 'border-amber-200',
                      text: 'text-amber-700',
                    },
                    {
                      bg: 'bg-pink-50',
                      border: 'border-pink-200',
                      text: 'text-pink-700',
                    },
                    {
                      bg: 'bg-indigo-50',
                      border: 'border-indigo-200',
                      text: 'text-indigo-700',
                    },
                    {
                      bg: 'bg-cyan-50',
                      border: 'border-cyan-200',
                      text: 'text-cyan-700',
                    },
                    {
                      bg: 'bg-rose-50',
                      border: 'border-rose-200',
                      text: 'text-rose-700',
                    },
                  ];

                  const userHash = hashCode(userName);
                  const colorScheme = colorPairs[userHash % colorPairs.length];

                  return (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${colorScheme.bg} ${colorScheme.border}`}
                    >
                      <div className='flex items-center gap-2 mb-2'>
                        <span
                          className={`text-sm font-semibold ${colorScheme.text}`}
                        >
                          {userName}
                        </span>
                        {timestamp && (
                          <span className='text-xs text-gray-500'>
                            {timestamp}
                          </span>
                        )}
                      </div>
                      <p className='text-sm text-gray-800 whitespace-pre-wrap'>
                        {note}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Add New Note */}
          <div className='space-y-3'>
            <label className='text-sm font-medium text-gray-700'>
              Add New Note
            </label>
            <Textarea
              placeholder='Enter your notes here...'
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className='min-h-[120px]'
            />
            <Button
              onClick={() => {
                if (comment.trim()) {
                  setShowCommentDialog(true);
                }
              }}
              disabled={!comment.trim()}
              className='w-full'
            >
              Save Note
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className='flex flex-col sm:flex-row gap-3 mb-6'>
        <Button
          onClick={() => setShowApproveDialog(true)}
          disabled={submission.status === 'approved'}
          className='flex-1 bg-green-600 hover:bg-green-700 text-white'
        >
          <CheckCircle className='mr-2 h-4 w-4' />
          {submission.status === 'approved'
            ? 'Approved'
            : 'Approve Application'}
        </Button>
        <Button
          onClick={() => setShowRejectDialog(true)}
          disabled={submission.status === 'rejected'}
          variant='destructive'
          className='flex-1'
        >
          <XCircle className='mr-2 h-4 w-4' />
          {submission.status === 'rejected' ? 'Rejected' : 'Reject Application'}
        </Button>
      </div>
    </div>
  );
}
