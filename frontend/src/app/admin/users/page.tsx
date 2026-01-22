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
import {
  Shield,
  Users,
  Crown,
  Eye,
  Loader2,
  Plus,
  X,
  Trash2,
} from 'lucide-react';
import { toast } from 'sonner';
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

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

  // Dialog state
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<AdminUser | null>(null);
  const [formData, setFormData] = useState({
    clerk_user_id: '',
    email: '',
    role: 'admin' as 'superadmin' | 'admin' | 'viewer',
    full_name: '',
  });

  // Fetch current user info
  const { data: currentUser } = useQuery<AdminUser>({
    queryKey: ['current-admin-user'],
    queryFn: async () => {
      const token = await getToken();
      const { data } = await apiClient.get('/api/v1/admin/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return data;
    },
    enabled: role === 'superadmin',
  });

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
        },
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

  // Create admin user mutation
  const createAdminMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = await getToken();
      await apiClient.post(
        '/api/v1/admin/auth/users',
        {
          clerk_user_id: data.clerk_user_id,
          email: data.email,
          role: data.role,
          full_name: data.full_name || null,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      toast.success('Admin user created successfully');
      setIsCreateDialogOpen(false);
      setFormData({
        clerk_user_id: '',
        email: '',
        role: 'admin',
        full_name: '',
      });
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Failed to create admin user',
      );
    },
  });

  // Delete admin user mutation
  const deleteAdminMutation = useMutation({
    mutationFn: async (id: number) => {
      const token = await getToken();
      await apiClient.delete(`/api/v1/admin/auth/users/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      toast.success('Admin user deleted successfully');
      setDeleteConfirmOpen(false);
      setUserToDelete(null);
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || 'Failed to delete admin user',
      );
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    if (!formData.clerk_user_id || !formData.email) {
      toast.error('Clerk User ID and Email are required');
      return;
    }

    createAdminMutation.mutate(formData);
  };

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
      <div className='mb-8 flex justify-between items-start'>
        <div>
          <h1 className='text-3xl font-bold mb-2'>Admin Users</h1>
          <p className='text-gray-600'>
            Manage admin user roles and permissions
          </p>
        </div>
        <Button
          onClick={() => setIsCreateDialogOpen(true)}
          className='flex items-center gap-2'
        >
          <Plus className='h-4 w-4' />
          Add Admin User
        </Button>
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

                  <div className='flex gap-2'>
                    {currentUser && user.id !== currentUser.id && (
                      <>
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
                        <Button
                          variant='outline'
                          size='sm'
                          className='text-red-600 hover:text-red-700 hover:bg-red-50'
                          onClick={() => {
                            setUserToDelete(user);
                            setDeleteConfirmOpen(true);
                          }}
                        >
                          <Trash2 className='h-4 w-4' />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent className='sm:max-w-[425px]'>
          <DialogHeader>
            <DialogTitle>Delete Admin User</DialogTitle>
            <DialogDescription>
              Are you sure you want to permanently delete this admin user? This
              action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          {userToDelete && (
            <div className='py-4'>
              <div className='bg-gray-50 p-4 rounded-lg'>
                <p className='text-sm font-medium'>{userToDelete.full_name}</p>
                <p className='text-sm text-gray-600'>{userToDelete.email}</p>
                <Badge
                  className={`mt-2 ${getRoleBadgeClass(userToDelete.role)}`}
                >
                  {getRoleIcon(userToDelete.role)}
                  <span className='ml-1 capitalize'>{userToDelete.role}</span>
                </Badge>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant='outline'
              onClick={() => {
                setDeleteConfirmOpen(false);
                setUserToDelete(null);
              }}
              disabled={deleteAdminMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant='destructive'
              onClick={() =>
                userToDelete && deleteAdminMutation.mutate(userToDelete.id)
              }
              disabled={deleteAdminMutation.isPending}
            >
              {deleteAdminMutation.isPending ? (
                <>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Deleting...
                </>
              ) : (
                'Delete User'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Admin User Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className='sm:max-w-[500px]'>
          <DialogHeader>
            <DialogTitle>Add Admin User</DialogTitle>
            <DialogDescription>
              Create a new admin user. Get the Clerk User ID from your Clerk
              dashboard.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateSubmit}>
            <div className='grid gap-4 py-4'>
              <div className='grid gap-2'>
                <Label htmlFor='clerk_user_id'>
                  Clerk User ID <span className='text-red-500'>*</span>
                </Label>
                <Input
                  id='clerk_user_id'
                  placeholder='user_2abc123xyz...'
                  value={formData.clerk_user_id}
                  onChange={(e) =>
                    setFormData({ ...formData, clerk_user_id: e.target.value })
                  }
                  required
                />
                <p className='text-xs text-gray-500'>
                  Find this in your Clerk dashboard under Users
                </p>
              </div>

              <div className='grid gap-2'>
                <Label htmlFor='email'>
                  Email <span className='text-red-500'>*</span>
                </Label>
                <Input
                  id='email'
                  type='email'
                  placeholder='admin@example.com'
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  required
                />
              </div>

              <div className='grid gap-2'>
                <Label htmlFor='role'>
                  Role <span className='text-red-500'>*</span>
                </Label>
                <Select
                  value={formData.role}
                  onValueChange={(value: 'superadmin' | 'admin' | 'viewer') =>
                    setFormData({ ...formData, role: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='viewer'>
                      Viewer - Read-only access
                    </SelectItem>
                    <SelectItem value='admin'>
                      Admin - Review & manage submissions
                    </SelectItem>
                    <SelectItem value='superadmin'>
                      Superadmin - Full system access
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className='grid gap-2'>
                <Label htmlFor='full_name'>Full Name (Optional)</Label>
                <Input
                  id='full_name'
                  placeholder='John Doe'
                  value={formData.full_name}
                  onChange={(e) =>
                    setFormData({ ...formData, full_name: e.target.value })
                  }
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type='button'
                variant='outline'
                onClick={() => setIsCreateDialogOpen(false)}
                disabled={createAdminMutation.isPending}
              >
                Cancel
              </Button>
              <Button type='submit' disabled={createAdminMutation.isPending}>
                {createAdminMutation.isPending ? (
                  <>
                    <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                    Creating...
                  </>
                ) : (
                  'Create Admin User'
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
