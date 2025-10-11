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

      {/* Property Information - ENHANCED */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <MapPin className='h-5 w-5' />
            Property Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Address Header */}
          <div className='mb-6'>
            {submission.property_street_address && (
              <h4 className='font-semibold text-xl mb-1'>
                {submission.property_street_address}
              </h4>
            )}
            {(submission.property_city ||
              submission.property_state ||
              submission.property_zip_code) && (
              <p className='text-gray-600'>
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

          {/* Combined Lot Size Banner (if multi-address) */}
          {getSmartyData()?.property?.combined_lot_size_sqft && (
            <div className='mb-6 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <label className='text-xs font-bold text-blue-700 uppercase tracking-wide flex items-center gap-1'>
                    <Building2 className='h-4 w-4' />
                    Total Development Site
                  </label>
                  <p className='text-3xl font-bold text-blue-900 mt-2'>
                    {getSmartyData()?.property?.combined_lot_size_sqft.toLocaleString()}{' '}
                    <span className='text-lg font-normal text-blue-700'>
                      sq ft
                    </span>
                  </p>
                  <p className='text-sm text-blue-700 mt-1 font-medium'>
                    {1 +
                      (getSmartyData()?.property?.additional_addresses
                        ?.length || 0)}{' '}
                    {getSmartyData()?.property?.additional_addresses?.length
                      ? 'parcels combined'
                      : 'parcel'}
                  </p>
                </div>
                {getSmartyData()?.property?.demolish_all_structures && (
                  <Badge className='bg-amber-500 hover:bg-amber-600 text-white px-3 py-1'>
                    🏗️ Full Demolition Planned
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Additional Addresses */}
          {getSmartyData()?.property?.additional_addresses &&
            getSmartyData()?.property?.additional_addresses.length > 0 && (
              <div className='mb-6 p-4 bg-gray-50 border-l-4 border-gray-400 rounded'>
                <label className='text-sm font-bold text-gray-700 uppercase block mb-3'>
                  📍 Additional Parcels
                </label>
                <div className='space-y-2'>
                  {getSmartyData()?.property?.additional_addresses.map(
                    (addr: any, idx: number) => (
                      <div
                        key={idx}
                        className='flex items-center gap-2 text-sm bg-white p-2 rounded'
                      >
                        <MapPin className='h-4 w-4 text-gray-500 flex-shrink-0' />
                        <span className='font-medium'>
                          {addr.address}, {addr.city}, {addr.state}{' '}
                          {addr.zip_code}
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

          {/* Property Details Grid - Only Show If Data Exists */}
          {(() => {
            const smartyData = getSmartyData();
            const lotInfo = smartyData?.lot;
            const buildingInfo = smartyData?.building;
            const valuationInfo = smartyData?.valuation;

            // Determine what data to show (prefer enriched Smarty data)
            const lotSizeSqft =
              lotInfo?.size_sqft || submission.property_lot_size_sqft;
            const lotSizeAcres =
              lotInfo?.size_acres || submission.property_lot_size_acres;
            const buildingSqft =
              buildingInfo?.size_sqft || submission.property_building_sqft;
            const yearBuilt =
              buildingInfo?.year_built || submission.property_year_built;
            const zoning = submission.property_zoning_description;
            const currentUse = submission.property_current_usage;
            const assessedValue =
              valuationInfo?.assessed_value ||
              submission.property_assessed_value;
            const propertyType = submission.property_type;

            // Count how many fields have data
            const hasData = !!(
              lotSizeSqft ||
              buildingSqft ||
              yearBuilt ||
              zoning ||
              currentUse ||
              assessedValue
            );

            if (!hasData) {
              return (
                <div className='p-4 bg-yellow-50 border border-yellow-200 rounded-lg'>
                  <p className='text-sm text-yellow-800'>
                    ⚠️ Detailed property data is being processed. Check back
                    soon or view the AI Assessment for development analysis.
                  </p>
                </div>
              );
            }

            return (
              <div className='grid grid-cols-2 md:grid-cols-3 gap-4'>
                {lotSizeSqft && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Lot Size
                    </label>
                    <p className='text-lg font-bold text-gray-900'>
                      {lotSizeSqft.toLocaleString()} sq ft
                    </p>
                    {lotSizeAcres > 0 && (
                      <p className='text-xs text-gray-600'>
                        ({lotSizeAcres.toFixed(2)} acres)
                      </p>
                    )}
                  </div>
                )}

                {buildingSqft && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Building Size
                    </label>
                    <p className='text-lg font-bold text-gray-900'>
                      {buildingSqft.toLocaleString()} sq ft
                    </p>
                  </div>
                )}

                {yearBuilt && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Year Built
                    </label>
                    <p className='text-lg font-bold text-gray-900'>
                      {yearBuilt}
                    </p>
                  </div>
                )}

                {currentUse && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Current Use
                    </label>
                    <p className='text-sm font-medium text-gray-900'>
                      {currentUse}
                    </p>
                  </div>
                )}

                {zoning && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Zoning
                    </label>
                    <p className='text-sm font-medium text-gray-900'>
                      {zoning}
                    </p>
                  </div>
                )}

                {assessedValue && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Assessed Value
                    </label>
                    <p className='text-lg font-bold text-gray-900'>
                      ${assessedValue.toLocaleString()}
                    </p>
                  </div>
                )}

                {propertyType && propertyType !== 'other' && (
                  <div className='p-3 bg-white border border-gray-200 rounded-lg'>
                    <label className='text-xs font-medium text-gray-500 uppercase block mb-1'>
                      Property Type
                    </label>
                    <p className='text-sm font-medium text-gray-900 capitalize'>
                      {propertyType}
                    </p>
                  </div>
                )}
              </div>
            );
          })()}
        </CardContent>
      </Card>

      {/* Available Build Space & LOGOS Qualification */}
      {(() => {
        const smartyData = getSmartyData();
        const availableBuildSpace = smartyData?.available_build_space;
        const lotInfo = smartyData?.lot;
        const buildingInfo = smartyData?.building;
        const valuationInfo = smartyData?.valuation;
        const financialInfo = smartyData?.financial;

        if (!smartyData) return null;

        return (
          <Card className='mb-6 border-2 border-blue-200 bg-blue-50/30'>
            <CardHeader>
              <div className='flex items-center justify-between'>
                <CardTitle className='flex items-center gap-2'>
                  <Building2 className='h-5 w-5 text-blue-600' />
                  Available Build Space Analysis
                </CardTitle>
                {availableBuildSpace?.qualifies_for_logos && (
                  <Badge className='bg-green-600 text-white text-sm px-3 py-1'>
                    ✓ QUALIFIES FOR LOGOS
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className='space-y-6'>
              {/* Key Metrics */}
              <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                {/* Lot Size */}
                <div className='bg-white p-4 rounded-lg border'>
                  <label className='text-xs font-medium text-gray-500 uppercase'>
                    Lot Size
                  </label>
                  <p className='text-2xl font-bold text-gray-900 mt-1'>
                    {lotInfo?.size_sqft?.toLocaleString() || 'N/A'} sq ft
                  </p>
                  {lotInfo?.size_acres > 0 && (
                    <p className='text-sm text-gray-600'>
                      ({lotInfo.size_acres.toFixed(2)} acres)
                    </p>
                  )}
                  {lotInfo?.lot_numbers && (
                    <p className='text-xs text-gray-500 mt-1'>
                      Lots: {lotInfo.lot_numbers}
                    </p>
                  )}
                  {lotInfo?.parcel_number && (
                    <p className='text-xs text-gray-500'>
                      Parcel: {lotInfo.parcel_number}
                    </p>
                  )}
                </div>

                {/* Building Size */}
                <div className='bg-white p-4 rounded-lg border'>
                  <label className='text-xs font-medium text-gray-500 uppercase'>
                    Building Size
                  </label>
                  <p className='text-2xl font-bold text-gray-900 mt-1'>
                    {buildingInfo?.size_sqft?.toLocaleString() || 'N/A'} sq ft
                  </p>
                  {buildingInfo?.year_built && (
                    <p className='text-sm text-gray-600'>
                      Built: {buildingInfo.year_built}
                    </p>
                  )}
                  {buildingInfo?.stories && (
                    <p className='text-xs text-gray-500 mt-1'>
                      {buildingInfo.stories}{' '}
                      {buildingInfo.stories === 1 ? 'story' : 'stories'}
                    </p>
                  )}
                </div>

                {/* Available Build Space - THE MONEY NUMBER */}
                <div
                  className={`p-4 rounded-lg border-2 ${
                    availableBuildSpace?.qualifies_for_logos
                      ? 'bg-green-50 border-green-300'
                      : 'bg-yellow-50 border-yellow-300'
                  }`}
                >
                  <label className='text-xs font-medium uppercase flex items-center gap-1'>
                    <TrendingUp className='h-3 w-3' />
                    Available Build Space
                  </label>
                  <p
                    className={`text-2xl font-bold mt-1 ${
                      availableBuildSpace?.qualifies_for_logos
                        ? 'text-green-700'
                        : 'text-yellow-700'
                    }`}
                  >
                    {availableBuildSpace?.sqft?.toLocaleString() || 'N/A'} sq ft
                  </p>
                  <p className='text-xs mt-1 text-gray-600'>
                    {availableBuildSpace?.calculation || 'Lot - Building'}
                  </p>
                  <p
                    className={`text-xs mt-2 font-medium ${
                      availableBuildSpace?.qualifies_for_logos
                        ? 'text-green-700'
                        : 'text-yellow-700'
                    }`}
                  >
                    {availableBuildSpace?.qualifies_for_logos
                      ? '✓ Meets 10,000 sq ft minimum'
                      : `Below 10,000 sq ft requirement`}
                  </p>
                </div>
              </div>

              {/* Valuation Information */}
              {valuationInfo &&
                (valuationInfo.assessed_total > 0 ||
                  valuationInfo.estimated_market_min > 0) && (
                  <div className='bg-white p-4 rounded-lg border'>
                    <h4 className='font-semibold mb-3 flex items-center gap-2'>
                      <DollarSign className='h-4 w-4 text-green-600' />
                      Property Valuation
                    </h4>
                    <div className='grid grid-cols-2 md:grid-cols-4 gap-4 text-sm'>
                      {valuationInfo.assessed_total > 0 && (
                        <div>
                          <label className='text-gray-500'>
                            Assessed Value
                          </label>
                          <p className='font-medium'>
                            ${valuationInfo.assessed_total.toLocaleString()}
                          </p>
                          {valuationInfo.assessed_year && (
                            <p className='text-xs text-gray-500'>
                              ({valuationInfo.assessed_year})
                            </p>
                          )}
                        </div>
                      )}
                      {valuationInfo.assessed_land > 0 && (
                        <div>
                          <label className='text-gray-500'>Land Value</label>
                          <p className='font-medium'>
                            ${valuationInfo.assessed_land.toLocaleString()}
                          </p>
                        </div>
                      )}
                      {valuationInfo.assessed_improvement > 0 && (
                        <div>
                          <label className='text-gray-500'>
                            Improvement Value
                          </label>
                          <p className='font-medium'>
                            $
                            {valuationInfo.assessed_improvement.toLocaleString()}
                          </p>
                        </div>
                      )}
                      {valuationInfo.estimated_market_min > 0 && (
                        <div>
                          <label className='text-gray-500'>
                            Est. Market Value
                          </label>
                          <p className='font-medium'>
                            $
                            {valuationInfo.estimated_market_min.toLocaleString()}{' '}
                            - $
                            {valuationInfo.estimated_market_max.toLocaleString()}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

              {/* Financial History */}
              {financialInfo?.has_mortgages &&
                financialInfo.mortgages?.length > 0 && (
                  <div className='bg-white p-4 rounded-lg border'>
                    <h4 className='font-semibold mb-3'>Financial History</h4>
                    <p className='text-sm text-gray-600 mb-2'>
                      {financialInfo.mortgage_count} mortgage(s) on record -
                      Total: $
                      {financialInfo.total_mortgage_amount?.toLocaleString() ||
                        '0'}
                    </p>
                    <div className='space-y-2 text-sm'>
                      {financialInfo.mortgages
                        .slice(0, 3)
                        .map((mortgage: any, idx: number) => (
                          <div
                            key={idx}
                            className='flex justify-between items-center p-2 bg-gray-50 rounded'
                          >
                            <div>
                              <span className='font-medium'>
                                {mortgage.lender || 'Unknown Lender'}
                              </span>
                              {mortgage.recording_date && (
                                <span className='text-gray-500 ml-2'>
                                  (
                                  {new Date(
                                    mortgage.recording_date
                                  ).toLocaleDateString()}
                                  )
                                </span>
                              )}
                            </div>
                            {mortgage.amount && (
                              <span className='font-medium'>
                                ${mortgage.amount.toLocaleString()}
                              </span>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              {financialInfo && !financialInfo.has_mortgages && (
                <div className='bg-green-50 p-3 rounded-lg border border-green-200'>
                  <p className='text-sm text-green-800 font-medium'>
                    ✓ Property owned free and clear (no mortgages on record)
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })()}

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
