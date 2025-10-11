/**
 * Admin Users Management Page
 * Manage admin user roles and permissions (Superadmin only)
 */

'use client';

import { useAdminAuth } from '@/hooks/useAdminAuth';
import { useAuth } from '@clerk/nextjs';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, Users, Crown, Eye, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface AdminUser {
  id: number;
  clerk_user_id: string;
  email: string;
  full_name: string;
  role: 'superadmin' | 'admin' | 'viewer';
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export default function AdminUsersPage() {
  const { role } = useAdminAuth();
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  // Fetch all admin users
  const { data: adminUsers, isLoading } = useQuery<AdminUser[]>({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const token = await getToken();
      const { data } = await apiClient.get('/api/v1/admin/auth/users', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return data;
    },
    enabled: role === 'superadmin', // Only fetch if superadmin
  });

  // Toggle admin user active status
  const toggleActiveMutation = useMutation({
    mutationFn: async ({ id, isActive }: { id: number; isActive: boolean }) => {
      const token = await getToken();
      await apiClient.patch(
        `/api/v1/admin/auth/users/${id}`,
        { is_active: !isActive },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      toast.success('Admin user updated successfully');
    },
    onError: () => {
      toast.error('Failed to update admin user');
    },
  });

  // Redirect if not superadmin
  if (role !== 'superadmin') {
    return (
      <div className='max-w-4xl mx-auto'>
        <Card>
          <CardContent className='text-center py-12'>
            <Shield className='h-12 w-12 mx-auto mb-4 text-gray-400' />
            <h2 className='text-xl font-semibold mb-2'>
              Superadmin Access Required
            </h2>
            <p className='text-gray-600'>
              You don't have permission to view this page.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-96'>
        <div className='text-center'>
          <Loader2 className='h-12 w-12 animate-spin text-blue-600 mx-auto mb-4' />
          <p className='text-gray-600'>Loading admin users...</p>
        </div>
      </div>
    );
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'superadmin':
        return <Crown className='h-4 w-4' />;
      case 'admin':
        return <Shield className='h-4 w-4' />;
      case 'viewer':
        return <Eye className='h-4 w-4' />;
      default:
        return <Users className='h-4 w-4' />;
    }
  };

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case 'superadmin':
        return 'bg-purple-100 text-purple-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className='max-w-5xl mx-auto'>
      {/* Header */}
      <div className='mb-8'>
        <h1 className='text-3xl font-bold mb-2'>Admin Users</h1>
        <p className='text-gray-600'>Manage admin user roles and permissions</p>
      </div>

      {/* Info Card */}
      <Card className='mb-6 border-blue-200 bg-blue-50'>
        <CardContent className='pt-6'>
          <div className='flex items-start gap-3'>
            <Shield className='h-5 w-5 text-blue-600 mt-0.5' />
            <div>
              <h3 className='font-semibold text-blue-900 mb-1'>
                Role Hierarchy
              </h3>
              <ul className='text-sm text-blue-800 space-y-1'>
                <li>
                  <strong>Superadmin:</strong> Full system access, can manage
                  admin users
                </li>
                <li>
                  <strong>Admin:</strong> Can review and manage submissions
                </li>
                <li>
                  <strong>Viewer:</strong> Read-only access to submissions
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-6'>
        <Card>
          <CardHeader className='pb-3'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Total Admins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold'>{adminUsers?.length || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-3'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Active Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-green-600'>
              {adminUsers?.filter((u) => u.is_active).length || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-3'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              Superadmins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-purple-600'>
              {adminUsers?.filter((u) => u.role === 'superadmin').length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Admin Users List */}
      <Card>
        <CardHeader>
          <CardTitle>Admin Users</CardTitle>
        </CardHeader>
        <CardContent>
          {!adminUsers || adminUsers.length === 0 ? (
            <p className='text-gray-500 text-center py-8'>
              No admin users found
            </p>
          ) : (
            <div className='space-y-3'>
              {adminUsers.map((user) => (
                <div
                  key={user.id}
                  className='flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50'
                >
                  <div className='flex items-center gap-4 flex-1'>
                    <div className='w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center'>
                      {getRoleIcon(user.role)}
                    </div>
                    <div className='flex-1'>
                      <div className='flex items-center gap-2 mb-1'>
                        <h4 className='font-semibold'>
                          {user.full_name || user.email}
                        </h4>
                        <Badge
                          className={getRoleBadgeClass(user.role)}
                          variant='outline'
                        >
                          {user.role}
                        </Badge>
                        {!user.is_active && (
                          <Badge
                            variant='outline'
                            className='bg-red-100 text-red-800'
                          >
                            Inactive
                          </Badge>
                        )}
                      </div>
                      <p className='text-sm text-gray-600'>{user.email}</p>
                      <p className='text-xs text-gray-500 mt-1'>
                        Last login:{' '}
                        {user.last_login
                          ? new Date(user.last_login).toLocaleDateString()
                          : 'Never'}
                      </p>
                    </div>
                  </div>

                  <div>
                    {user.role !== 'superadmin' && (
                      <Button
                        variant='outline'
                        size='sm'
                        onClick={() =>
                          toggleActiveMutation.mutate({
                            id: user.id,
                            isActive: user.is_active,
                          })
                        }
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* CLI Instructions */}
      <Card className='mt-6'>
        <CardHeader>
          <CardTitle className='text-sm'>Add New Admin User</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-sm text-gray-600 mb-3'>
            To add a new admin user, use the CLI tool:
          </p>
          <pre className='bg-gray-100 p-3 rounded text-xs overflow-x-auto'>
            python backend/assign_admin_role.py &lt;clerk_user_id&gt;
            &lt;email&gt; &lt;role&gt; [full_name]
          </pre>
          <p className='text-xs text-gray-500 mt-2'>
            Roles: superadmin, admin, viewer
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
