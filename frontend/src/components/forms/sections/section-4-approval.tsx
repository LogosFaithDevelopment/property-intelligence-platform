'use client';

import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { UseFormReturn } from 'react-hook-form';
import { ChurchSubmissionFormValues } from '@/lib/validations/submission';
import { LEADERSHIP_SUPPORT_OPTIONS } from '@/types/church';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface Section4ApprovalProps {
  form: UseFormReturn<ChurchSubmissionFormValues>;
}

/**
 * Section 4: Congregation Approval
 * Critical for partnership - need congregation support
 */
export function Section4Approval({ form }: Section4ApprovalProps) {
  const congregationVoted = form.watch('congregation_voted');
  const votePercentage = form.watch('vote_percentage');
  const denominationApprovalNeeded = form.watch('denomination_approval_needed');

  // Show vote percentage field if congregation voted
  const showVotePercentage = congregationVoted === true;

  // Calculate vote status
  const voteNotEnough = votePercentage && votePercentage <= 50;
  const voteLow = votePercentage && votePercentage > 50 && votePercentage < 66;
  const voteGood = votePercentage && votePercentage >= 66;

  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold'>Congregation Approval</h2>
        <p className='text-muted-foreground mt-1'>
          Congregation voting and leadership support details
        </p>
      </div>

      {/* Has Congregation Voted? */}
      <FormField
        control={form.control}
        name='congregation_voted'
        render={({ field }) => (
          <FormItem>
            <FormLabel className='text-lg font-semibold'>
              Has your congregation voted on this partnership?
              <span className='text-red-500'> *</span>
            </FormLabel>
            <Select
              onValueChange={(value) => field.onChange(value === 'true')}
              value={
                field.value === undefined ? undefined : String(field.value)
              }
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select an option' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value='true'>
                  Yes - Congregation has voted
                </SelectItem>
                <SelectItem value='false'>No - Not yet voted</SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              We prefer churches that have congregation support before applying
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Vote Percentage (if voted) */}
      {showVotePercentage && (
        <FormField
          control={form.control}
          name='vote_percentage'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                What percentage of the congregation approved?
                <span className='text-red-500'> *</span>
              </FormLabel>
              <FormControl>
                <Input
                  type='number'
                  min='0'
                  max='100'
                  placeholder='e.g., 75'
                  {...field}
                  value={
                    field.value === undefined ||
                    field.value === null ||
                    isNaN(field.value)
                      ? ''
                      : String(field.value)
                  }
                  onChange={(e) => {
                    const val = e.target.value;
                    field.onChange(val === '' ? undefined : Number(val));
                  }}
                />
              </FormControl>
              <FormDescription>
                Enter the approval percentage (0-100%)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      )}

      {/* Vote Status Alerts */}
      {voteNotEnough && (
        <Alert variant='destructive'>
          <AlertTriangle className='h-4 w-4' />
          <AlertDescription>
            <strong>Vote percentage must be greater than 50%</strong> to proceed
            with the partnership. Please ensure you have majority approval
            before submitting.
          </AlertDescription>
        </Alert>
      )}

      {voteLow && (
        <Alert className='border-yellow-500 bg-yellow-50'>
          <Info className='h-4 w-4 text-yellow-600' />
          <AlertDescription className='text-yellow-800'>
            <strong>Note:</strong> While {votePercentage}% approval meets the
            minimum requirement, Logos prefers{' '}
            <strong>66%+ congregation support</strong> for stronger partnership
            alignment.
          </AlertDescription>
        </Alert>
      )}

      {voteGood && (
        <Alert className='border-green-500 bg-green-50'>
          <CheckCircle className='h-4 w-4 text-green-600' />
          <AlertDescription className='text-green-800'>
            ✅ Excellent! {votePercentage}% approval demonstrates strong
            congregation support for this partnership.
          </AlertDescription>
        </Alert>
      )}

      {/* Leadership Support */}
      <FormField
        control={form.control}
        name='leadership_support'
        render={({ field }) => (
          <FormItem>
            <FormLabel>
              Level of leadership support
              <span className='text-red-500'> *</span>
            </FormLabel>
            <Select onValueChange={field.onChange} value={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select support level' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {LEADERSHIP_SUPPORT_OPTIONS.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormDescription>
              How much does your church leadership (elders, board, pastor)
              support this project?
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Denomination Approval Needed */}
      <FormField
        control={form.control}
        name='denomination_approval_needed'
        render={({ field }) => (
          <FormItem>
            <FormLabel className='text-lg font-semibold'>
              Does your denomination require approval for this type of
              partnership? <span className='text-red-500'>*</span>
            </FormLabel>
            <Select
              onValueChange={(value) => field.onChange(value === 'true')}
              value={
                field.value === undefined ? undefined : String(field.value)
              }
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select an option' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value='true'>
                  Yes - Denomination approval required
                </SelectItem>
                <SelectItem value='false'>
                  No - Church is autonomous / no approval needed
                </SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              Some denominations require regional or national approval for
              property partnerships
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Denomination Approval Info */}
      {denominationApprovalNeeded === true && (
        <Alert className='border-blue-500 bg-blue-50'>
          <Info className='h-4 w-4 text-blue-600' />
          <AlertDescription className='text-blue-800'>
            <strong>Denomination Approval Process:</strong>
            <p className='mt-2'>
              We understand that some denominations require approval for
              property partnerships. Logos has experience working with various
              denominational structures and can provide the necessary
              documentation and presentations to help secure approval.
            </p>
            <p className='mt-2'>
              We&apos;ll work with you through this process if your application
              is approved.
            </p>
          </AlertDescription>
        </Alert>
      )}

      {/* No Denomination Approval Info */}
      {congregationVoted === false && (
        <Alert className='border-blue-500 bg-blue-50'>
          <Info className='h-4 w-4 text-blue-600' />
          <AlertDescription className='text-blue-800'>
            <strong>Haven&apos;t voted yet?</strong>
            <p className='mt-2'>
              You can still submit this application! However, congregation
              approval will be required before we can proceed with the
              partnership. We recommend presenting this opportunity to your
              congregation soon.
            </p>
            <p className='mt-2'>
              Logos can provide presentation materials and attend a congregation
              meeting to answer questions if helpful.
            </p>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
