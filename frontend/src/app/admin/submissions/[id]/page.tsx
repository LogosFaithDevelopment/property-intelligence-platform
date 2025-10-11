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

  // Section 3: Ownership & Financial
  owns_property_free_clear: boolean | null;
  has_mortgage: boolean | null;
  mortgage_balance: number | null;
  willing_to_ground_lease: boolean | null;
  assessed_value: number | null;
  existing_debt_amount: number | null;
  expects_sanctuary_replacement: boolean | null;
  sanctuary_replacement_cost_estimate: number | null;

  // Section 4: Congregation Approval
  congregation_voted: boolean | null;
  vote_percentage: number | null;
  leadership_support: string | null;
  decision_authority: string | null;
  decision_timeline: string | null;
  denomination_approval_needed: boolean | null;

  // Section 5: Parking & Development
  current_parking_spaces: number | null;
  parking_spaces_needed_after: number | null;
  special_requirements: string | null;

  // Section 6: Timeline & Preferences
  timeline_preference: string | null;
  preferred_unit_count: number | null;
  affordability_target: string | null;
  revenue_sharing_preference: string | null;
  development_involvement_level: string | null;

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
        `http://localhost:8000/api/v1/admin/stats/submissions/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
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
        `http://localhost:8000/api/v1/admin/submissions/${id}/approve`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ notes }),
        }
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
        `http://localhost:8000/api/v1/admin/submissions/${id}/reject`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ reason: rejectReason, notes }),
        }
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
        `http://localhost:8000/api/v1/admin/submissions/${id}/comment`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ comment }),
        }
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
    <div className='max-w-5xl mx-auto'>
      {/* Header */}
      <div className='mb-6 flex items-center justify-between'>
        <div className='flex items-center gap-4'>
          <Link href='/admin/submissions'>
            <Button variant='outline' size='icon'>
              <ArrowLeft className='h-4 w-4' />
            </Button>
          </Link>
          <div>
            <h1 className='text-3xl font-bold'>{submission.church_name}</h1>
            <p className='text-gray-600'>Submission ID: {submission.id}</p>
            {submission.property_street_address && (
              <p className='text-sm text-gray-500'>
                {submission.property_street_address}
              </p>
            )}
          </div>
        </div>
        <div className='flex flex-col gap-2 items-end'>
          <Badge
            className={getStatusColor(submission.status)}
            variant='outline'
          >
            {submission.status}
          </Badge>
          {submission.overall_score && (
            <div className='text-right'>
              <div className='text-2xl font-bold text-blue-600'>
                {submission.overall_score.toFixed(1)}
              </div>
              <div className='text-xs text-gray-500'>Overall Score</div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions - AI Assessment Visualization */}
      <div className='mb-6'>
        <Link href={`/admin/submissions/${id}/assessment`}>
          <Button
            variant='default'
            className='w-full py-6 text-lg bg-blue-600 hover:bg-blue-700'
            disabled={!submission.overall_score}
          >
            <TrendingUp className='h-5 w-5 mr-2' />
            {submission.overall_score
              ? 'View Full AI Assessment Data & Visualizations'
              : 'AI Assessment Pending (Processing...)'}
          </Button>
        </Link>
      </div>

      {/* Action Buttons */}
      <div className='mb-6 flex gap-3'>
        <Button
          onClick={() => setShowApproveDialog(true)}
          className='flex-1 bg-green-600 hover:bg-green-700'
          disabled={approveMutation.isPending}
        >
          <CheckCircle className='h-4 w-4 mr-2' />
          {approveMutation.isPending ? 'Approving...' : 'Approve Submission'}
        </Button>
        <Button
          onClick={() => setShowRejectDialog(true)}
          variant='destructive'
          className='flex-1'
          disabled={rejectMutation.isPending}
        >
          <XCircle className='h-4 w-4 mr-2' />
          {rejectMutation.isPending ? 'Rejecting...' : 'Reject Submission'}
        </Button>
        <Button
          onClick={() => setShowCommentDialog(true)}
          variant='outline'
          disabled={commentMutation.isPending}
        >
          <MessageSquare className='h-4 w-4 mr-2' />
          Add Comment
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

      {/* Church Information */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Building2 className='h-5 w-5' />
            Church Information
          </CardTitle>
        </CardHeader>
        <CardContent className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Legal Name
            </label>
            <p className='mt-1'>{submission.church_legal_name || 'N/A'}</p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Denomination
            </label>
            <p className='mt-1'>{submission.church_denomination || 'N/A'}</p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Founded Year
            </label>
            <p className='mt-1'>{submission.church_founded_year || 'N/A'}</p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Tax Exempt Status
            </label>
            <p className='mt-1'>
              {submission.church_tax_exempt_status || 'N/A'}
            </p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>EIN</label>
            <p className='mt-1'>{submission.church_tax_exempt_id || 'N/A'}</p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Congregation Size
            </label>
            <p className='mt-1 flex items-center gap-1'>
              <Users className='h-4 w-4 text-gray-500' />
              {submission.church_congregation_size?.toLocaleString() || 'N/A'}
            </p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Annual Budget
            </label>
            <p className='mt-1 flex items-center gap-1'>
              <DollarSign className='h-4 w-4 text-gray-500' />
              {submission.church_annual_budget
                ? `$${submission.church_annual_budget.toLocaleString()}`
                : 'N/A'}
            </p>
          </div>
          <div>
            <label className='text-sm font-medium text-gray-500'>
              Submitted
            </label>
            <p className='mt-1 flex items-center gap-1'>
              <Calendar className='h-4 w-4 text-gray-500' />
              {new Date(submission.created_at).toLocaleDateString()}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Contact Information */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
        </CardHeader>
        <CardContent className='space-y-3'>
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
          {submission.church_website_url && (
            <div className='flex items-center gap-2'>
              <Globe className='h-4 w-4 text-gray-500' />
              <a
                href={submission.church_website_url}
                target='_blank'
                rel='noopener noreferrer'
                className='text-blue-600 hover:underline'
              >
                {submission.church_website_url}
              </a>
            </div>
          )}
          {(submission.church_street_address || submission.church_city) && (
            <div className='flex items-start gap-2'>
              <MapPin className='h-4 w-4 text-gray-500 mt-1' />
              <div>
                {submission.church_street_address && (
                  <p>{submission.church_street_address}</p>
                )}
                {(submission.church_city ||
                  submission.church_state ||
                  submission.church_zip_code) && (
                  <p>
                    {[
                      submission.church_city,
                      submission.church_state,
                      submission.church_zip_code,
                    ]
                      .filter(Boolean)
                      .join(', ')}
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Property Overview - Consolidated Card */}
      {(() => {
        const smartyData = getSmartyData();
        const lotInfo = smartyData?.lot;
        const buildingInfo = smartyData?.building;
        const combinedLotSize = smartyData?.property?.combined_lot_size_sqft;
        const additionalAddresses =
          smartyData?.property?.additional_addresses || [];

        return (
          <Card className='mb-6'>
            <CardHeader>
              <CardTitle className='flex items-center gap-2'>
                <Building2 className='h-5 w-5' />
                Property Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Address */}
              <div className='mb-6 pb-4 border-b'>
                {submission.property_street_address && (
                  <h3 className='text-xl font-bold text-gray-900 mb-1'>
                    {submission.property_street_address}
                  </h3>
                )}
                {(submission.property_city ||
                  submission.property_state ||
                  submission.property_zip_code) && (
                  <p className='text-gray-600 text-lg'>
                    {[
                      submission.property_city,
                      submission.property_state,
                      submission.property_zip_code,
                    ]
                      .filter(Boolean)
                      .join(', ')}
                  </p>
                )}
              </div>

              {/* Multi-Parcel Banner */}
              {combinedLotSize && additionalAddresses.length > 0 && (
                <div className='mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg'>
                  <div className='flex items-center justify-between'>
                    <div>
                      <label className='text-xs font-bold text-blue-700 uppercase tracking-wide flex items-center gap-1 mb-1'>
                        <Building2 className='h-4 w-4' />
                        Multi-Parcel Development Site
                      </label>
                      <p className='text-2xl font-bold text-blue-900'>
                        {combinedLotSize.toLocaleString()}{' '}
                        <span className='text-base font-normal text-blue-700'>
                          sq ft total
                        </span>
                      </p>
                      <p className='text-sm text-blue-700 mt-1'>
                        {1 + additionalAddresses.length} parcels combined
                      </p>
                    </div>
                  </div>
                  {/* Additional Addresses List */}
                  <div className='mt-4 pt-4 border-t border-blue-200'>
                    <label className='text-xs font-bold text-blue-700 uppercase block mb-2'>
                      📍 Included Parcels
                    </label>
                    <div className='space-y-1'>
                      <div className='text-sm text-blue-900'>
                        • {submission.property_street_address}
                      </div>
                      {additionalAddresses.map((addr: any, idx: number) => (
                        <div key={idx} className='text-sm text-blue-900'>
                          • {addr.address}, {addr.city}, {addr.state}{' '}
                          {addr.zip_code}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Key Metrics Grid */}
              <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
                {/* Lot Size */}
                <div className='p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200'>
                  <label className='text-xs font-medium text-blue-700 uppercase block mb-1'>
                    Lot Size
                  </label>
                  <p className='text-2xl font-bold text-blue-900'>
                    {(
                      combinedLotSize ||
                      lotInfo?.size_sqft ||
                      submission.property_lot_size_sqft
                    )?.toLocaleString() || 'N/A'}
                  </p>
                  <p className='text-xs text-blue-600 mt-1'>sq ft</p>
                  {(lotInfo?.size_acres ||
                    submission.property_lot_size_acres) && (
                    <p className='text-xs text-blue-600 mt-1'>
                      (
                      {(
                        lotInfo?.size_acres ||
                        submission.property_lot_size_acres
                      )?.toFixed(2)}{' '}
                      acres)
                    </p>
                  )}
                  {lotInfo?.lot_numbers && (
                    <p className='text-xs text-gray-600 mt-2'>
                      Lots: {lotInfo.lot_numbers}
                    </p>
                  )}
                  {lotInfo?.parcel_number && (
                    <p className='text-xs text-gray-600'>
                      Parcel: {lotInfo.parcel_number}
                    </p>
                  )}
                </div>

                {/* Building Size */}
                <div className='p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200'>
                  <label className='text-xs font-medium text-gray-700 uppercase block mb-1'>
                    Building Size
                  </label>
                  <p className='text-2xl font-bold text-gray-900'>
                    {(
                      buildingInfo?.size_sqft ||
                      submission.property_building_sqft
                    )?.toLocaleString() || 'N/A'}
                  </p>
                  <p className='text-xs text-gray-600 mt-1'>sq ft</p>
                </div>

                {/* Year Built */}
                <div className='p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200'>
                  <label className='text-xs font-medium text-purple-700 uppercase block mb-1'>
                    Year Built
                  </label>
                  <p className='text-2xl font-bold text-purple-900'>
                    {buildingInfo?.year_built ||
                      submission.property_year_built ||
                      'N/A'}
                  </p>
                </div>

                {/* Current Use */}
                <div className='p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200'>
                  <label className='text-xs font-medium text-green-700 uppercase block mb-1'>
                    Current Use
                  </label>
                  <p className='text-sm font-semibold text-green-900'>
                    {submission.property_current_usage || 'N/A'}
                  </p>
                </div>

                {/* Zoning */}
                <div className='p-4 bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg border border-amber-200'>
                  <label className='text-xs font-medium text-amber-700 uppercase block mb-1'>
                    Zoning
                  </label>
                  <p className='text-xl font-bold text-amber-900'>
                    {submission.property_zoning_description || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Mortgage Status */}
              {(() => {
                const financialInfo = smartyData?.financial;
                if (financialInfo && !financialInfo.has_mortgages) {
                  return (
                    <div className='mt-6 bg-green-50 p-4 rounded-lg border border-green-200'>
                      <p className='text-sm text-green-800 font-medium flex items-center gap-2'>
                        <CheckCircle className='h-4 w-4' />
                        Property owned free and clear (no mortgages on record)
                      </p>
                    </div>
                  );
                }
                return null;
              })()}
            </CardContent>
          </Card>
        );
      })()}

      {/* Ownership & Financial Details */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <DollarSign className='h-5 w-5' />
            Ownership & Financial Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            {/* Ownership Status */}
            <div className='p-4 bg-gray-50 rounded-lg border'>
              <h4 className='font-semibold text-sm text-gray-700 mb-3'>
                Property Ownership
              </h4>
              <div className='space-y-2 text-sm'>
                <div className='flex justify-between items-center'>
                  <span className='text-gray-600'>Owned Free & Clear:</span>
                  <span className='font-medium'>
                    {submission.owns_property_free_clear === true ? (
                      <Badge className='bg-green-600'>✓ Yes</Badge>
                    ) : submission.owns_property_free_clear === false ? (
                      <Badge variant='destructive'>✗ No</Badge>
                    ) : (
                      'Not specified'
                    )}
                  </span>
                </div>
                {submission.has_mortgage !== null && (
                  <div className='flex justify-between items-center'>
                    <span className='text-gray-600'>Has Mortgage:</span>
                    <span className='font-medium'>
                      {submission.has_mortgage ? 'Yes' : 'No'}
                    </span>
                  </div>
                )}
                {submission.mortgage_balance && (
                  <div className='flex justify-between items-center'>
                    <span className='text-gray-600'>Mortgage Balance:</span>
                    <span className='font-medium'>
                      ${submission.mortgage_balance.toLocaleString()}
                    </span>
                  </div>
                )}
                <div className='flex justify-between items-center'>
                  <span className='text-gray-600'>
                    Willing to Ground Lease:
                  </span>
                  <span className='font-medium'>
                    {submission.willing_to_ground_lease === true ? (
                      <Badge className='bg-blue-600'>✓ Yes</Badge>
                    ) : submission.willing_to_ground_lease === false ? (
                      <Badge variant='outline'>✗ No</Badge>
                    ) : (
                      'Not specified'
                    )}
                  </span>
                </div>
              </div>
            </div>

            {/* Financial Details */}
            <div className='p-4 bg-gray-50 rounded-lg border'>
              <h4 className='font-semibold text-sm text-gray-700 mb-3'>
                Financial Information
              </h4>
              <div className='space-y-2 text-sm'>
                {submission.existing_debt_amount && (
                  <div className='flex justify-between items-center'>
                    <span className='text-gray-600'>Existing Debt:</span>
                    <span className='font-medium'>
                      ${submission.existing_debt_amount.toLocaleString()}
                    </span>
                  </div>
                )}
                {submission.expects_sanctuary_replacement !== null && (
                  <div className='flex justify-between items-center'>
                    <span className='text-gray-600'>
                      Expects Sanctuary Replacement:
                    </span>
                    <span className='font-medium'>
                      {submission.expects_sanctuary_replacement ? (
                        <Badge variant='outline'>Yes</Badge>
                      ) : (
                        'No'
                      )}
                    </span>
                  </div>
                )}
                {submission.sanctuary_replacement_cost_estimate && (
                  <div className='flex justify-between items-center'>
                    <span className='text-gray-600'>Estimated Cost:</span>
                    <span className='font-medium'>
                      $
                      {submission.sanctuary_replacement_cost_estimate.toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Congregation Approval */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Users className='h-5 w-5' />
            Congregation Approval & Support
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
            {/* Voting Status */}
            <div className='p-4 bg-gray-50 rounded-lg border'>
              <h4 className='font-semibold text-sm text-gray-700 mb-3'>
                Congregation Vote
              </h4>
              <div className='space-y-3'>
                <div className='flex justify-between items-center'>
                  <span className='text-gray-600 text-sm'>
                    Congregation Voted:
                  </span>
                  <span className='font-medium'>
                    {submission.congregation_voted === true ? (
                      <Badge className='bg-green-600'>✓ Yes</Badge>
                    ) : submission.congregation_voted === false ? (
                      <Badge variant='outline'>Not Yet</Badge>
                    ) : (
                      'Not specified'
                    )}
                  </span>
                </div>
                {submission.congregation_voted &&
                  submission.vote_percentage !== null && (
                    <div className='mt-4'>
                      <div className='flex justify-between items-center mb-2'>
                        <span className='text-gray-600 text-sm'>
                          Approval Percentage:
                        </span>
                        <span className='text-2xl font-bold text-blue-600'>
                          {submission.vote_percentage}%
                        </span>
                      </div>
                      <div className='w-full bg-gray-200 rounded-full h-3'>
                        <div
                          className={`h-3 rounded-full ${
                            submission.vote_percentage >= 66
                              ? 'bg-green-500'
                              : submission.vote_percentage > 50
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${submission.vote_percentage}%` }}
                        />
                      </div>
                      <p className='text-xs text-gray-500 mt-1'>
                        {submission.vote_percentage >= 66
                          ? '✓ Strong support (66%+)'
                          : submission.vote_percentage > 50
                          ? 'Meets minimum (>50%)'
                          : '⚠️ Below minimum requirement'}
                      </p>
                    </div>
                  )}
              </div>
            </div>

            {/* Leadership & Decision Making */}
            <div className='p-4 bg-gray-50 rounded-lg border'>
              <h4 className='font-semibold text-sm text-gray-700 mb-3'>
                Leadership & Decision Making
              </h4>
              <div className='space-y-2 text-sm'>
                {submission.leadership_support && (
                  <div className='flex justify-between items-start'>
                    <span className='text-gray-600'>Leadership Support:</span>
                    <span className='font-medium text-right'>
                      {submission.leadership_support}
                    </span>
                  </div>
                )}
                {submission.decision_authority && (
                  <div className='flex justify-between items-start'>
                    <span className='text-gray-600'>Decision Authority:</span>
                    <span className='font-medium text-right'>
                      {submission.decision_authority}
                    </span>
                  </div>
                )}
                {submission.decision_timeline && (
                  <div className='flex justify-between items-start'>
                    <span className='text-gray-600'>Decision Timeline:</span>
                    <span className='font-medium text-right'>
                      {submission.decision_timeline}
                    </span>
                  </div>
                )}
                {submission.denomination_approval_needed !== null && (
                  <div className='flex justify-between items-center'>
                    <span className='text-gray-600'>
                      Denomination Approval Needed:
                    </span>
                    <span className='font-medium'>
                      {submission.denomination_approval_needed ? 'Yes' : 'No'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Development Preferences */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Building2 className='h-5 w-5' />
            Development Preferences & Requirements
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
            {/* Parking */}
            <div className='p-4 bg-blue-50 rounded-lg border border-blue-200'>
              <h4 className='font-semibold text-sm text-blue-900 mb-3 flex items-center gap-2'>
                🅿️ Parking Requirements
              </h4>
              <div className='space-y-2 text-sm'>
                {submission.current_parking_spaces !== null && (
                  <div className='flex justify-between items-center'>
                    <span className='text-blue-700'>Current Spaces:</span>
                    <span className='font-bold text-blue-900'>
                      {submission.current_parking_spaces}
                    </span>
                  </div>
                )}
                {submission.parking_spaces_needed_after !== null && (
                  <div className='flex justify-between items-center'>
                    <span className='text-blue-700'>Needed After:</span>
                    <span className='font-bold text-blue-900'>
                      {submission.parking_spaces_needed_after}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Timeline & Units */}
            <div className='p-4 bg-green-50 rounded-lg border border-green-200'>
              <h4 className='font-semibold text-sm text-green-900 mb-3 flex items-center gap-2'>
                📅 Timeline & Units
              </h4>
              <div className='space-y-2 text-sm'>
                {submission.timeline_preference && (
                  <div className='flex justify-between items-start'>
                    <span className='text-green-700'>Timeline:</span>
                    <span className='font-bold text-green-900 text-right'>
                      {submission.timeline_preference}
                    </span>
                  </div>
                )}
                {submission.preferred_unit_count !== null && (
                  <div className='flex justify-between items-center'>
                    <span className='text-green-700'>Preferred Units:</span>
                    <span className='font-bold text-green-900'>
                      {submission.preferred_unit_count}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Financial Preferences */}
            <div className='p-4 bg-purple-50 rounded-lg border border-purple-200'>
              <h4 className='font-semibold text-sm text-purple-900 mb-3 flex items-center gap-2'>
                💰 Financial Structure
              </h4>
              <div className='space-y-2 text-sm'>
                {submission.revenue_sharing_preference && (
                  <div>
                    <span className='text-purple-700 block mb-1'>
                      Revenue Sharing:
                    </span>
                    <span className='font-bold text-purple-900'>
                      {submission.revenue_sharing_preference}
                    </span>
                  </div>
                )}
                {submission.affordability_target && (
                  <div>
                    <span className='text-purple-700 block mb-1'>
                      Target Income:
                    </span>
                    <span className='font-bold text-purple-900 text-xs'>
                      {submission.affordability_target}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Special Requirements */}
          {submission.special_requirements && (
            <div className='mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200'>
              <h4 className='font-semibold text-sm text-amber-900 mb-2 flex items-center gap-2'>
                ⭐ Special Requirements & Considerations
              </h4>
              <p className='text-sm text-amber-900 whitespace-pre-wrap'>
                {submission.special_requirements}
              </p>
            </div>
          )}

          {/* Development Involvement */}
          {submission.development_involvement_level && (
            <div className='mt-4 p-3 bg-gray-100 rounded border'>
              <div className='flex items-center justify-between'>
                <span className='text-sm text-gray-600'>
                  Development Involvement Level:
                </span>
                <span className='font-medium text-gray-900'>
                  {submission.development_involvement_level}
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Admin Notes */}

      {/* Admin Notes */}
      {submission.reviewer_notes && (
        <Card>
          <CardHeader>
            <CardTitle>Admin Notes & History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className='whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded border'>
              {submission.reviewer_notes}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
