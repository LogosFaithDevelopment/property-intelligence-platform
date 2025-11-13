/**
 * Clear Admin Cache
 * Clears the cached admin role stored in cookies
 * Useful when user roles change or for testing
 */

import { NextResponse } from 'next/server';

export async function POST() {
  const response = NextResponse.json({ success: true });

  // Delete admin cache cookies
  response.cookies.delete('admin_role');
  response.cookies.delete('admin_cache_time');

  return response;
}
