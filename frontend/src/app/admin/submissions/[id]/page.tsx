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
            <h1 className='text-3xl font-bold font-[family-name:var(--font-safe-light-accent)]'>
              {submission.church_name}
            </h1>
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

      {/* Quick Actions - AI Assessment & Download */}
      <div className='mb-6 grid grid-cols-2 gap-3'>
        <Link href={`/admin/submissions/${id}/assessment`}>
          <Button
            variant='default'
            className='w-full py-6 text-lg bg-blue-600 hover:bg-blue-700'
            disabled={!submission.overall_score}
          >
            <TrendingUp className='h-5 w-5 mr-2' />
            {submission.overall_score
              ? 'Full Development Analysis'
              : 'Analysis Pending...'}
          </Button>
        </Link>
        <Button
          onClick={async () => {
            try {
              toast.loading('Generating report...', { id: 'download-report' });

              const token = await getToken();
              const response = await fetch(
                `http://localhost:8000/api/v1/reports/assessment/${id}/download-v2`,
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
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
          className='w-full py-6 px-8 text-lg bg-gradient-to-r from-yellow-500 to-yellow-700 hover:from-yellow-600 hover:to-yellow-800'
          disabled={!submission.overall_score}
        >
          Download Summary Report
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
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Building2 className='h-5 w-5' />
            Entity Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-6'>
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
      {(submission.assessed_value || submission.existing_debt_amount) && (
        <Card className='mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <DollarSign className='h-5 w-5' />
              Ownership & Financial
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
              {submission.assessed_value && (
                <div>
                  <label className='text-sm font-medium text-gray-500'>
                    Owner Reported Current Value
                  </label>
                  <p className='mt-1 text-lg font-semibold'>
                    ${submission.assessed_value.toLocaleString()}
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

      {/* Notes Section */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
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
      <div className='flex gap-3 mb-6'>
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
