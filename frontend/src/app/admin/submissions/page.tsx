/**
 * Admin Submissions List Page
 * View all property submissions with filtering
 */

'use client';

import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Building2,
  Search,
  Filter,
  MapPin,
  Calendar,
  Eye,
  Loader2,
  TrendingUp,
} from 'lucide-react';
import Link from 'next/link';

interface Submission {
  id: number;
  church_name: string;
  property_address: string;
  status: string;
  overall_score: number | null;
  submitted_at: string;
  updated_at: string;
}

interface SubmissionListResponse {
  total: number;
  submissions: Submission[];
}

export default function AdminSubmissionsPage() {
  const { getToken } = useAuth();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Fetch all submissions
  const { data, isLoading, error } = useQuery<SubmissionListResponse>({
    queryKey: ['admin-submissions-list', statusFilter],
    queryFn: async () => {
      const token = await getToken();
      const params = new URLSearchParams();
      if (statusFilter && statusFilter !== 'all') {
        params.append('status', statusFilter);
      }

      const response = await fetch(
        `http://localhost:8000/api/v1/admin/stats/submissions?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch submissions');
      }

      return response.json();
    },
    staleTime: 30000, // 30 seconds
  });

  const submissions = data?.submissions || [];
  const total = data?.total || 0;

  // Client-side search filter
  const filteredSubmissions = submissions.filter((submission) => {
    if (!search) return true;
    const searchLower = search.toLowerCase();
    return (
      submission.church_name.toLowerCase().includes(searchLower) ||
      submission.property_address.toLowerCase().includes(searchLower)
    );
  });

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
          <p className='text-gray-600'>Loading submissions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='text-center py-12'>
        <p className='text-red-600'>Error loading submissions</p>
        <p className='text-sm text-gray-500 mt-2'>{String(error)}</p>
      </div>
    );
  }

  return (
    <div className='max-w-7xl mx-auto'>
      {/* Header */}
      <div className='mb-8'>
        <h1 className='text-3xl font-bold mb-2'>Property Submissions</h1>
        <p className='text-gray-600'>
          Review and manage all church property submissions
        </p>
      </div>

      {/* Filters */}
      <Card className='mb-6'>
        <CardContent className='pt-6'>
          <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
            {/* Search */}
            <div className='relative md:col-span-2'>
              <Search className='absolute left-3 top-3 h-4 w-4 text-gray-400' />
              <Input
                placeholder='Search by church name or email...'
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className='pl-10'
              />
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder='All Statuses' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>All Statuses</SelectItem>
                <SelectItem value='DRAFT'>Draft</SelectItem>
                <SelectItem value='SUBMITTED'>Submitted</SelectItem>
                <SelectItem value='PROCESSING'>Processing</SelectItem>
                <SelectItem value='COMPLETED'>Completed</SelectItem>
                <SelectItem value='REVIEWED'>Reviewed</SelectItem>
                <SelectItem value='APPROVED'>Approved</SelectItem>
                <SelectItem value='REJECTED'>Rejected</SelectItem>
              </SelectContent>
            </Select>

            {/* Results Count */}
            <div className='flex items-center text-sm text-gray-600'>
              Showing {filteredSubmissions.length} of {total} total
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submissions List */}
      {submissions.length === 0 ? (
        <Card>
          <CardContent className='text-center py-12'>
            <Building2 className='h-12 w-12 mx-auto mb-4 text-gray-400' />
            <p className='text-gray-600 mb-4'>No submissions found</p>
            <p className='text-sm text-gray-500'>
              Try adjusting your filters or search criteria
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className='space-y-4'>
          {filteredSubmissions.map((submission) => (
            <Link
              key={submission.id}
              href={`/admin/submissions/${submission.id}`}
            >
              <Card className='hover:shadow-md transition-shadow cursor-pointer'>
                <CardContent className='p-6'>
                  <div className='flex items-start justify-between'>
                    <div className='flex-1'>
                      {/* Church Name & Status */}
                      <div className='flex items-center gap-3 mb-3'>
                        <h3 className='text-lg font-semibold'>
                          {submission.church_name}
                        </h3>
                        <Badge className={getStatusColor(submission.status)}>
                          {submission.status}
                        </Badge>
                      </div>

                      {/* Property Address */}
                      <div className='flex items-center gap-2 text-sm text-gray-600 mb-2'>
                        <MapPin className='h-4 w-4' />
                        <span>{submission.property_address}</span>
                      </div>

                      {/* Date & Score */}
                      <div className='flex items-center gap-4 text-sm text-gray-500'>
                        <span className='flex items-center gap-1'>
                          <Calendar className='h-4 w-4' />
                          {new Date(
                            submission.submitted_at
                          ).toLocaleDateString()}
                        </span>
                        {submission.overall_score && (
                          <span className='flex items-center gap-1'>
                            <TrendingUp className='h-4 w-4' />
                            Score: {submission.overall_score.toFixed(1)}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Score Badge (if available) */}
                    {submission.overall_score && (
                      <div className='ml-4 text-right'>
                        <div className='text-3xl font-bold text-blue-600'>
                          {submission.overall_score.toFixed(1)}
                        </div>
                        <div className='text-xs text-gray-500'>Score</div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
