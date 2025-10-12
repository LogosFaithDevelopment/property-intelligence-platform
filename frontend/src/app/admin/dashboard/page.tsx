/**
 * Admin Dashboard
 * Overview page with stats and recent activity
 */

'use client';

import { useAdminAuth } from '@/hooks/useAdminAuth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  FileText,
  Users,
  CheckCircle,
  Clock,
  TrendingUp,
  XCircle,
  Loader2,
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';

interface DashboardStats {
  total_submissions: number;
  pending_submissions: number;
  approved_submissions: number;
  rejected_submissions: number;
  processing_submissions: number;
  total_churches: number;
  total_properties: number;
  avg_score: number | null;
}

interface RecentSubmission {
  id: number;
  church_name: string;
  property_address: string;
  status: string;
  overall_score: number | null;
  submitted_at: string;
}

export default function AdminDashboard() {
  const { role, email } = useAdminAuth();
  const { getToken } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentSubmissions, setRecentSubmissions] = useState<
    RecentSubmission[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const token = await getToken();
        if (!token) return;

        // Fetch stats
        const statsRes = await fetch(
          'http://localhost:8000/api/v1/admin/stats/dashboard',
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }

        // Fetch recent submissions
        const recentRes = await fetch(
          'http://localhost:8000/api/v1/admin/stats/recent-submissions?limit=5',
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (recentRes.ok) {
          const recentData = await recentRes.json();
          setRecentSubmissions(recentData);
        }

        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, [getToken]);

  if (loading) {
    return (
      <div className='flex items-center justify-center min-h-[400px]'>
        <Loader2 className='h-8 w-8 animate-spin text-blue-600' />
      </div>
    );
  }

  return (
    <div className='max-w-7xl mx-auto'>
      {/* Header */}
      <div className='mb-8'>
        <h1 className='text-3xl font-bold mb-2 font-[family-name:var(--font-safe-light-accent)]'>
          Dashboard
        </h1>
        <p className='text-gray-600'>
          Welcome back! Here's an overview of property submissions.
        </p>
        {role && (
          <div className='mt-2'>
            <span className='inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800'>
              {role.charAt(0).toUpperCase() + role.slice(1)}
            </span>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Total Submissions
            </CardTitle>
            <FileText className='h-4 w-4 text-gray-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold'>
              {stats?.total_submissions || 0}
            </div>
            <p className='text-xs text-gray-500 mt-1'>All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Pending Review
            </CardTitle>
            <Clock className='h-4 w-4 text-yellow-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold text-yellow-600'>
              {stats?.pending_submissions || 0}
            </div>
            <p className='text-xs text-gray-500 mt-1'>Awaiting action</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Processing
            </CardTitle>
            <TrendingUp className='h-4 w-4 text-blue-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold text-blue-600'>
              {stats?.processing_submissions || 0}
            </div>
            <p className='text-xs text-gray-500 mt-1'>In progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Approved
            </CardTitle>
            <CheckCircle className='h-4 w-4 text-green-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold text-green-600'>
              {stats?.approved_submissions || 0}
            </div>
            <p className='text-xs text-gray-500 mt-1'>Ready to proceed</p>
          </CardContent>
        </Card>
      </div>

      {/* Additional Stats Row */}
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-8'>
        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Rejected
            </CardTitle>
            <XCircle className='h-4 w-4 text-red-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold text-red-600'>
              {stats?.rejected_submissions || 0}
            </div>
            <p className='text-xs text-gray-500 mt-1'>Not approved</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Churches
            </CardTitle>
            <Users className='h-4 w-4 text-purple-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold text-purple-600'>
              {stats?.total_churches || 0}
            </div>
            <p className='text-xs text-gray-500 mt-1'>Total registered</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className='flex flex-row items-center justify-between pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Average Score
            </CardTitle>
            <TrendingUp className='h-4 w-4 text-indigo-600' />
          </CardHeader>
          <CardContent>
            <div className='text-3xl font-bold text-indigo-600'>
              {stats?.avg_score?.toFixed(1) || 'N/A'}
            </div>
            <p className='text-xs text-gray-500 mt-1'>Out of 100</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader className='flex flex-row items-center justify-between'>
          <CardTitle>Recent Submissions</CardTitle>
          <Link href='/admin/submissions'>
            <Button variant='outline' size='sm'>
              View All
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {recentSubmissions.length === 0 ? (
            <div className='text-center py-12 text-gray-500'>
              <FileText className='h-12 w-12 mx-auto mb-4 text-gray-400' />
              <p className='mb-4'>No submissions yet</p>
              <Link href='/submit-property'>
                <Button variant='outline'>Submit First Property</Button>
              </Link>
            </div>
          ) : (
            <div className='space-y-3'>
              {recentSubmissions.map((submission) => (
                <Link
                  key={submission.id}
                  href={`/admin/submissions/${submission.id}`}
                  className='block mb-3'
                >
                  <div className='flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer'>
                    <div className='flex-1'>
                      <h3 className='font-semibold text-gray-900'>
                        {submission.church_name}
                      </h3>
                      <p className='text-sm text-gray-600'>
                        {submission.property_address}
                      </p>
                      <p className='text-xs text-gray-500 mt-1'>
                        {new Date(submission.submitted_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className='flex items-center gap-4'>
                      {submission.overall_score && (
                        <div className='text-right'>
                          <div className='text-2xl font-bold text-blue-600'>
                            {submission.overall_score.toFixed(1)}
                          </div>
                          <div className='text-xs text-gray-500'>Score</div>
                        </div>
                      )}
                      <div>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            submission.status === 'APPROVED'
                              ? 'bg-green-100 text-green-800'
                              : submission.status === 'REJECTED'
                              ? 'bg-red-100 text-red-800'
                              : submission.status === 'PROCESSING'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {submission.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className='mt-8 grid grid-cols-1 md:grid-cols-2 gap-6'>
        <Card>
          <CardHeader>
            <CardTitle className='text-lg'>View All Submissions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className='text-gray-600 mb-4'>
              Review and manage all property submissions in one place.
            </p>
            <Link href='/admin/submissions'>
              <Button>Go to Submissions</Button>
            </Link>
          </CardContent>
        </Card>

        {role === 'superadmin' && (
          <Card>
            <CardHeader>
              <CardTitle className='text-lg'>Manage Admin Users</CardTitle>
            </CardHeader>
            <CardContent>
              <p className='text-gray-600 mb-4'>
                Add, remove, or update admin user roles and permissions.
              </p>
              <Link href='/admin/users'>
                <Button variant='outline'>Manage Users</Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
