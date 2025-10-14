/**
 * Admin Assessment Data Visualization Page
 * Shows all AI assessment data matching the PDF report structure
 * Redesigned to match the PDF report layout with grading analytics, recommendations, and key data
 */

'use client';

import { use } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  ArrowLeft,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  Users,
  MapPin,
  Building2,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  Target,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';

interface SubmissionDetail {
  id: number;
  status: string;
  overall_score: number | null;
  location_score: number | null;
  market_score: number | null;
  financial_score: number | null;
  partnership_score: number | null;
  risk_score: number | null;
  market_analysis: any | null;
  financial_projections: any | null;
  risk_factors: any | null;
  comparable_projects: any | null;

  // Church data
  church_name: string;

  // Property data
  property_street_address: string | null;
  property_city: string | null;
  property_state: string | null;
  property_zip_code: string | null;
  property_county: string | null;
  property_latitude: number | null;
  property_longitude: number | null;
  property_lot_size_sqft: number | null;
  property_lot_size_acres: number | null;
  property_zoning_classification: string | null;
  property_zoning_description: string | null;
  property_current_usage: string | null;
  property_assessed_value: number | null;
  property_data_sources: string | null; // JSON string with enriched data from APIs
  property_additional_addresses: any | null; // Additional addresses with enriched data
  property_demolish_all_structures: boolean | null;

  // Assessment data - user's custom inputs
  available_build_sqft: number | null; // User's custom available build space input
  available_build_acres: number | null;
}

export default function AssessmentVisualizationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { getToken } = useAuth();

  // Fetch submission details with assessment data
  const { data: submission, isLoading } = useQuery<SubmissionDetail>({
    queryKey: ['admin-submission-assessment', id],
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
        throw new Error('Failed to fetch submission assessment data');
      }

      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-96'>
        <div className='text-center'>
          <Loader2 className='h-12 w-12 animate-spin text-blue-600 mx-auto mb-4' />
          <p className='text-gray-600'>Loading assessment data...</p>
        </div>
      </div>
    );
  }

  if (!submission) {
    return (
      <div className='text-center py-12'>
        <p className='text-red-600'>Assessment data not found</p>
      </div>
    );
  }

  // Check if AI assessment has been run
  const hasAssessment = submission.overall_score !== null;

  if (!hasAssessment) {
    return (
      <div className='max-w-5xl mx-auto'>
        <div className='mb-6 flex items-center gap-4'>
          <Link href={`/admin/submissions/${id}`}>
            <Button variant='outline' size='icon'>
              <ArrowLeft className='h-4 w-4' />
            </Button>
          </Link>
          <div>
            <h1 className='text-3xl font-bold'>{submission.church_name}</h1>
            <p className='text-gray-600'>Assessment Data</p>
          </div>
        </div>

        <Card>
          <CardContent className='py-12 text-center'>
            <AlertTriangle className='h-16 w-16 text-yellow-500 mx-auto mb-4' />
            <h2 className='text-2xl font-semibold mb-2'>
              AI Assessment Not Yet Run
            </h2>
            <p className='text-gray-600'>
              This submission has not been processed by the AI assessment engine
              yet.
            </p>
            <p className='text-sm text-gray-500 mt-2'>
              The assessment will show detailed scores, financial projections,
              market analysis, and risk factors once processed.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Get grade letter (matching PDF report grading system)
  const getGrade = (score: number): string => {
    if (score >= 97) return 'A+';
    if (score >= 93) return 'A';
    if (score >= 90) return 'A-';
    if (score >= 87) return 'B+';
    if (score >= 83) return 'B';
    if (score >= 80) return 'B-';
    if (score >= 77) return 'C+';
    if (score >= 73) return 'C';
    if (score >= 70) return 'C-';
    if (score >= 67) return 'D+';
    if (score >= 63) return 'D';
    if (score >= 60) return 'D-';
    return 'F';
  };

  const getGradeColor = (score: number): string => {
    if (score >= 80) return 'bg-green-50 text-green-700 border-green-200';
    if (score >= 70) return 'bg-yellow-50 text-yellow-700 border-yellow-200';
    if (score >= 60) return 'bg-orange-50 text-orange-700 border-orange-200';
    return 'bg-red-50 text-red-700 border-red-200';
  };

  const getStatusColor = (score: number): string => {
    if (score >= 60) return 'text-green-600';
    return 'text-red-600';
  };

  const grade = getGrade(submission.overall_score || 0);
  const score = submission.overall_score || 0;

  // Check for deal breakers
  const hasDealBreakers =
    submission.financial_projections?.unit_capacity?.feasible_units < 40;
  const feasibleUnits =
    submission.financial_projections?.unit_capacity?.feasible_units || 0;

  return (
    <div className='max-w-7xl mx-auto pb-12'>
      {/* Header */}
      <div className='mb-6 flex items-center justify-between'>
        <div className='flex items-center gap-4'>
          <Link href={`/admin/submissions/${id}`}>
            <Button variant='outline' size='icon'>
              <ArrowLeft className='h-4 w-4' />
            </Button>
          </Link>
          <div>
            <h1 className='text-3xl font-bold'>{submission.church_name}</h1>
            <p className='text-gray-600'>Grading Analytics & Assessment</p>
            {submission.property_street_address && (
              <p className='text-sm text-gray-500'>
                {submission.property_street_address}
              </p>
            )}
          </div>
        </div>
        <div className='flex items-center gap-4'>
          <Button
            onClick={async () => {
              try {
                toast.loading('Generating report...', {
                  id: 'download-report',
                });
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
                console.error('Download error:', error);
                toast.error('Failed to download report. Please try again.', {
                  id: 'download-report',
                });
              }
            }}
            className='bg-gradient-to-r from-yellow-500 to-yellow-700 hover:from-yellow-600 hover:to-yellow-800'
          >
            Download Report
          </Button>
          <div className='text-right'>
            <div className={`text-5xl font-bold ${getStatusColor(score)}`}>
              {grade}
            </div>
            <div className='text-2xl font-semibold text-gray-700'>
              {score.toFixed(1)}/100
            </div>
            <div className='text-xs text-gray-500 mt-1'>Overall Score</div>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <Card className='mb-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200'>
        <CardHeader>
          <CardTitle className='text-2xl flex items-center gap-2'>
            📄 Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent className='space-y-4'>
          <div>
            <h3 className='font-semibold text-lg mb-2'>Overall Assessment</h3>
            <p className='text-gray-700'>
              This property has been evaluated across five key dimensions:
              Financial Viability (30%), Market Demand (25%), Location Quality
              (20%), Partnership Alignment (15%), and Risk Assessment (10%). The
              weighted composite score is{' '}
              <strong>
                {score.toFixed(1)}/100 (Grade {grade})
              </strong>
              .
            </p>
          </div>

          {/* Property Summary with Demolish Info */}
          {(() => {
            let smartyData = null;
            try {
              if (submission.property_data_sources) {
                const dataSources =
                  typeof submission.property_data_sources === 'string'
                    ? JSON.parse(submission.property_data_sources)
                    : submission.property_data_sources;
                smartyData = dataSources?.smarty_data?.data;
              }
            } catch (error) {
              console.error('Error parsing property data:', error);
            }

            const propertyInfo = smartyData?.property;
            const multiAddressInfo = smartyData?.multi_address;
            const individualParcels =
              multiAddressInfo?.individual_parcels || [];
            const primaryParcel = individualParcels[0] || {};
            const lotInfo = primaryParcel?.lot || smartyData?.lot;
            const buildingInfo =
              primaryParcel?.building || smartyData?.building;
            const additionalAddresses =
              submission.property_additional_addresses || [];
            const isDemolish = submission.property_demolish_all_structures;
            const combinedLotSize = multiAddressInfo?.combined_lot_size_sqft;

            // PRIORITY: Use custom lot size if available (user-provided)
            const displayLotSize =
              submission.available_build_sqft ||
              submission.property_lot_size_sqft ||
              lotInfo?.size_sqft;
            const isUserProvidedLot = !!submission.available_build_sqft;

            // Show property details if: demolition planned, additional addresses, OR custom lot size provided
            if (
              isDemolish ||
              additionalAddresses.length > 0 ||
              isUserProvidedLot
            ) {
              return (
                <div className='bg-amber-50 border border-amber-200 rounded-lg p-4'>
                  <h4 className='font-semibold text-sm text-amber-900 mb-2 flex items-center gap-2'>
                    <Building2 className='h-4 w-4' />
                    Property Details
                  </h4>
                  <div className='space-y-2 text-sm'>
                    {/* Primary Address */}
                    <div className='flex items-start gap-2'>
                      <span className='text-gray-600'>•</span>
                      <div className='flex-1'>
                        <span className='font-medium'>
                          {submission.property_street_address}
                        </span>
                        <span className='text-gray-600'>
                          {' '}
                          - Lot: {displayLotSize?.toLocaleString() || 'N/A'} sq
                          ft
                        </span>
                        {isUserProvidedLot && (
                          <span className='text-amber-600 font-semibold ml-1'>
                            ⚠️ (Applicant-Submitted)
                          </span>
                        )}
                        {buildingInfo?.size_sqft && (
                          <span className='text-gray-600'>
                            , Building:{' '}
                            {buildingInfo.size_sqft.toLocaleString()} sq ft
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Additional Addresses */}
                    {additionalAddresses.map((addr: any, idx: number) => (
                      <div key={idx} className='flex items-start gap-2'>
                        <span className='text-gray-600'>•</span>
                        <div className='flex-1'>
                          <span className='font-medium'>{addr.address}</span>
                          {addr.enriched_data?.lot?.size_sqft && (
                            <span className='text-gray-600'>
                              {' '}
                              - Lot:{' '}
                              {addr.enriched_data.lot.size_sqft.toLocaleString()}{' '}
                              sq ft
                            </span>
                          )}
                          {addr.enriched_data?.building?.size_sqft && (
                            <span className='text-gray-600'>
                              , Building:{' '}
                              {addr.enriched_data.building.size_sqft.toLocaleString()}{' '}
                              sq ft
                            </span>
                          )}
                        </div>
                      </div>
                    ))}

                    {/* Combined Total */}
                    {(displayLotSize || combinedLotSize) && (
                      <div className='mt-2 pt-2 border-t border-amber-300'>
                        <span className='font-semibold text-amber-900'>
                          Combined Total:{' '}
                          {(
                            displayLotSize || combinedLotSize
                          )?.toLocaleString()}{' '}
                          sq ft ({1 + additionalAddresses.length} parcel
                          {additionalAddresses.length > 0 ? 's' : ''})
                        </span>
                        {isUserProvidedLot && (
                          <span className='text-amber-600 font-semibold ml-2'>
                            ⚠️ (Applicant-Submitted)
                          </span>
                        )}
                      </div>
                    )}

                    {/* Demolish Badge */}
                    {isDemolish && (
                      <div className='mt-2 pt-2 border-t border-amber-300'>
                        <Badge className='bg-amber-500 hover:bg-amber-600 text-white'>
                          🏗️ Full Demolition Planned
                        </Badge>
                        <span className='text-xs text-gray-600 ml-2'>
                          Existing structures to be removed for new development
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            }
            return null;
          })()}

          {/* Recommendation */}
          <div>
            <h3 className='font-semibold text-lg mb-2'>Recommendation</h3>
            {hasDealBreakers ? (
              <div className='bg-red-50 border-2 border-red-200 rounded-lg p-4'>
                <div className='flex items-start gap-3'>
                  <XCircle className='h-5 w-5 text-red-600 flex-shrink-0 mt-0.5' />
                  <div>
                    <p className='font-semibold text-red-700 mb-2'>
                      NOT RECOMMENDED - CRITICAL DEAL BREAKER PRESENT
                    </p>
                    <p className='text-sm text-red-800'>
                      This property has a <strong>critical deal breaker</strong>{' '}
                      that makes development financially unfeasible. Only{' '}
                      <strong>{feasibleUnits} units</strong> feasible (requires
                      40+ units minimum). The lot size is insufficient to meet
                      Logos' minimum 40-unit requirement, which is essential for
                      achieving economies of scale and maintaining cost per unit
                      below $325,000.
                    </p>
                  </div>
                </div>
              </div>
            ) : score >= 80 ? (
              <div className='bg-green-50 border-2 border-green-200 rounded-lg p-4'>
                <div className='flex items-start gap-3'>
                  <CheckCircle className='h-5 w-5 text-green-600 flex-shrink-0 mt-0.5' />
                  <div>
                    <p className='font-semibold text-green-700 mb-2'>
                      STRONGLY RECOMMENDED FOR DEVELOPMENT
                    </p>
                    <p className='text-sm text-green-800'>
                      This property scores {score.toFixed(1)}/100 (Grade {grade}
                      ), placing it in the top tier of Logos development
                      opportunities. The financial projections are solid, market
                      demand is strong, and partnership alignment is excellent.
                      Proceed with full due diligence and site planning.
                    </p>
                  </div>
                </div>
              </div>
            ) : score >= 70 ? (
              <div className='bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4'>
                <div className='flex items-start gap-3'>
                  <AlertCircle className='h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5' />
                  <div>
                    <p className='font-semibold text-yellow-700 mb-2'>
                      CONDITIONALLY APPROVED - ADDRESS KEY ISSUES
                    </p>
                    <p className='text-sm text-yellow-800'>
                      This property scores {score.toFixed(1)}/100 (Grade {grade}
                      ), meeting minimum viability standards but requiring risk
                      mitigation before final approval. Review the issues
                      identified below and develop action plans to address each
                      concern.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className='bg-red-50 border-2 border-red-200 rounded-lg p-4'>
                <div className='flex items-start gap-3'>
                  <XCircle className='h-5 w-5 text-red-600 flex-shrink-0 mt-0.5' />
                  <div>
                    <p className='font-semibold text-red-700 mb-2'>
                      NOT RECOMMENDED - CRITICAL ISSUES PRESENT
                    </p>
                    <p className='text-sm text-red-800'>
                      This property scores {score.toFixed(1)}/100 (Grade {grade}
                      ), falling below minimum viability thresholds. Critical
                      issues have been identified that make this development
                      financially or operationally unfeasible under current
                      conditions.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div>
            <h3 className='font-semibold text-lg mb-2'>Key Findings</h3>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
              <div className='bg-white rounded-lg p-3 border border-blue-200'>
                <p className='text-sm text-gray-600'>Financial Score</p>
                <p className='text-xl font-bold text-blue-600'>
                  {(submission.financial_score || 0).toFixed(1)}/100
                </p>
                <p className='text-xs text-gray-500'>
                  {submission.financial_projections?.unit_capacity
                    ?.feasible_units || 'N/A'}{' '}
                  units @ $
                  {submission.financial_projections?.adjusted_cost_per_unit?.toLocaleString() ||
                    'N/A'}
                  /unit
                </p>
              </div>
              <div className='bg-white rounded-lg p-3 border border-blue-200'>
                <p className='text-sm text-gray-600'>Market Score</p>
                <p className='text-xl font-bold text-green-600'>
                  {(submission.market_score || 0).toFixed(1)}/100
                </p>
                <p className='text-xs text-gray-500'>
                  {submission.market_analysis?.housing_demand ||
                    'Demand analysis pending'}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Property Overview - Enhanced Multi-Parcel Display */}
      {(() => {
        // Parse enriched Smarty data from property_data_sources
        let smartyData = null;
        try {
          if (submission.property_data_sources) {
            const dataSources =
              typeof submission.property_data_sources === 'string'
                ? JSON.parse(submission.property_data_sources)
                : submission.property_data_sources;
            smartyData = dataSources?.smarty_data?.data;
          }
        } catch (error) {
          console.error('Error parsing property data sources:', error);
        }

        const propertyInfo = smartyData?.property;
        const multiAddressInfo = smartyData?.multi_address;
        const individualParcels = multiAddressInfo?.individual_parcels || [];

        // Get PRIMARY parcel data (index 0 in individual_parcels)
        const primaryParcel = individualParcels[0] || {};
        const lotInfo = primaryParcel?.lot || smartyData?.lot;
        const buildingInfo = primaryParcel?.building || smartyData?.building;

        const combinedLotSize =
          multiAddressInfo?.combined_lot_size_sqft ||
          propertyInfo?.combined_lot_size_sqft;

        // Get additional addresses from the property table (not nested in smarty_data)
        const additionalAddresses =
          submission.property_additional_addresses || [];
        const isDemolish =
          submission.property_demolish_all_structures ||
          multiAddressInfo?.demolish_all_structures ||
          propertyInfo?.demolish_all_structures;

        return (
          <Card className='mb-6 border-2 border-gray-300'>
            <CardHeader className='bg-gray-50 py-2 pb-2'>
              <CardTitle className='text-base flex items-center gap-2'>
                <MapPin className='h-4 w-4 text-blue-600' />
                Property Overview
              </CardTitle>
            </CardHeader>
            <CardContent className='pt-2 pb-3'>
              {/* Primary Address */}
              <div className='mb-4 pb-4 border-b border-gray-200'>
                <div className='grid grid-cols-1 md:grid-cols-4 gap-3'>
                  <div>
                    <label className='text-xs font-semibold text-gray-500 uppercase block mb-0.5'>
                      Street Address
                    </label>
                    <p className='text-base font-semibold text-gray-900'>
                      {submission.property_street_address || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className='text-xs font-semibold text-gray-500 uppercase block mb-0.5'>
                      City, State, ZIP
                    </label>
                    <p className='text-base font-semibold text-gray-900'>
                      {[
                        submission.property_city,
                        submission.property_state,
                        submission.property_zip_code,
                      ]
                        .filter(Boolean)
                        .join(', ') || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className='text-xs font-semibold text-gray-500 uppercase block mb-0.5'>
                      County
                    </label>
                    <p className='text-base font-semibold text-gray-900'>
                      {submission.property_county || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className='text-xs font-semibold text-gray-500 uppercase block mb-0.5'>
                      Year Built
                    </label>
                    <p className='text-base font-semibold text-gray-900'>
                      {buildingInfo?.year_built || 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Primary Parcel Details */}
                {lotInfo && (
                  <div className='mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200'>
                    <h4 className='font-semibold text-sm text-blue-900 mb-2 flex items-center justify-between'>
                      <span>
                        Primary Parcel - {submission.property_street_address}
                      </span>
                      {isDemolish && (
                        <Badge className='bg-amber-500 hover:bg-amber-600 text-white text-xs'>
                          To Be Demolished
                        </Badge>
                      )}
                    </h4>
                    <div className='grid grid-cols-2 md:grid-cols-4 gap-3 text-sm'>
                      {lotInfo.size_sqft && (
                        <div>
                          <label className='text-xs text-gray-600 block'>
                            Lot Size
                          </label>
                          <p className='font-bold text-gray-900'>
                            {lotInfo.size_sqft.toLocaleString()} sq ft
                          </p>
                          {lotInfo.size_acres > 0 && (
                            <p className='text-xs text-gray-600'>
                              ({lotInfo.size_acres.toFixed(2)} acres)
                            </p>
                          )}
                        </div>
                      )}
                      {buildingInfo?.size_sqft && (
                        <div>
                          <label className='text-xs text-gray-600 block'>
                            Building Size
                          </label>
                          <p className='font-bold text-gray-900'>
                            {buildingInfo.size_sqft.toLocaleString()} sq ft
                          </p>
                        </div>
                      )}
                      {lotInfo.parcel_number && (
                        <div>
                          <label className='text-xs text-gray-600 block'>
                            Parcel Number
                          </label>
                          <p className='font-bold text-gray-900'>
                            {lotInfo.parcel_number}
                          </p>
                        </div>
                      )}
                      {lotInfo.lot_numbers && (
                        <div>
                          <label className='text-xs text-gray-600 block'>
                            Lot Number(s)
                          </label>
                          <p className='font-bold text-gray-900'>
                            {lotInfo.lot_numbers}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Additional Addresses (Multi-Parcel Property) */}
              {additionalAddresses.length > 0 && (
                <div className='mb-4 pb-4 border-b border-gray-200'>
                  <h3 className='font-semibold text-base mb-3 flex items-center gap-2'>
                    <Building2 className='h-5 w-5 text-orange-600' />
                    Additional Parcels ({additionalAddresses.length})
                  </h3>
                  <div className='space-y-3'>
                    {additionalAddresses.map((addr: any, idx: number) => (
                      <div
                        key={idx}
                        className='p-3 bg-orange-50 rounded-lg border border-orange-200'
                      >
                        <div className='grid grid-cols-1 md:grid-cols-2 gap-3 mb-3'>
                          <div>
                            <label className='text-xs font-semibold text-gray-600 uppercase block mb-1 flex items-center justify-between'>
                              <span>Address</span>
                              {isDemolish && (
                                <Badge className='bg-amber-500 hover:bg-amber-600 text-white text-xs'>
                                  To Be Demolished
                                </Badge>
                              )}
                            </label>
                            <p className='font-semibold text-gray-900'>
                              {addr.address}, {addr.city}, {addr.state}{' '}
                              {addr.zip_code}
                            </p>
                          </div>
                          {addr.county && (
                            <div>
                              <label className='text-xs font-semibold text-gray-600 uppercase block mb-1'>
                                County
                              </label>
                              <p className='font-semibold text-gray-900'>
                                {addr.county}
                              </p>
                            </div>
                          )}
                        </div>
                        {addr.enriched_data && (
                          <div className='grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mt-3 pt-3 border-t border-orange-300'>
                            {addr.enriched_data.lot?.size_sqft && (
                              <div>
                                <label className='text-xs text-gray-600 block'>
                                  Lot Size
                                </label>
                                <p className='font-bold text-gray-900'>
                                  {addr.enriched_data.lot.size_sqft.toLocaleString()}{' '}
                                  sq ft
                                </p>
                              </div>
                            )}
                            {addr.enriched_data.building?.size_sqft && (
                              <div>
                                <label className='text-xs text-gray-600 block'>
                                  Building Size
                                </label>
                                <p className='font-bold text-gray-900'>
                                  {addr.enriched_data.building.size_sqft.toLocaleString()}{' '}
                                  sq ft
                                </p>
                              </div>
                            )}
                            {addr.enriched_data.lot?.parcel_number && (
                              <div>
                                <label className='text-xs text-gray-600 block'>
                                  Parcel Number
                                </label>
                                <p className='font-bold text-gray-900'>
                                  {addr.enriched_data.lot.parcel_number}
                                </p>
                              </div>
                            )}
                            {addr.enriched_data.lot?.lot_numbers && (
                              <div>
                                <label className='text-xs text-gray-600 block'>
                                  Lot Number(s)
                                </label>
                                <p className='font-bold text-gray-900'>
                                  {addr.enriched_data.lot.lot_numbers}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Combined Site Summary (for multi-parcel) */}
              {/* {combinedLotSize && (
                <div className='p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-300'>
                  <h3 className='font-bold text-base text-green-900 mb-2 flex items-center gap-2'>
                    <Building2 className='h-5 w-5' />
                    Combined Development Site
                  </h3>
                  <div className='grid grid-cols-2 md:grid-cols-3 gap-4'>
                    <div>
                      <label className='text-xs font-semibold text-green-700 uppercase block mb-1'>
                        Total Lot Size
                      </label>
                      <p className='text-2xl font-bold text-green-900'>
                        {combinedLotSize.toLocaleString()}{' '}
                        <span className='text-sm font-normal'>sq ft</span>
                      </p>
                    </div>
                    <div>
                      <label className='text-xs font-semibold text-green-700 uppercase block mb-1'>
                        Total Parcels
                      </label>
                      <p className='text-2xl font-bold text-green-900'>
                        {1 + additionalAddresses.length}
                      </p>
                    </div>
                    {isDemolish && (
                      <div>
                        <label className='text-xs font-semibold text-green-700 uppercase block mb-1'>
                          Development Plan
                        </label>
                        <Badge className='bg-amber-500 hover:bg-amber-600 text-white'>
                          Full Demolition Planned
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              )} */}
            </CardContent>
          </Card>
        );
      })()}

      {/* Comprehensive Grading Breakdown */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            📊 Comprehensive Grading Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='overflow-x-auto'>
            <table className='w-full border-collapse'>
              <thead>
                <tr className='bg-blue-600 text-white'>
                  <th className='border border-gray-300 px-4 py-2 text-left'>
                    Category
                  </th>
                  <th className='border border-gray-300 px-4 py-2 text-center'>
                    Score
                  </th>
                  <th className='border border-gray-300 px-4 py-2 text-center'>
                    Grade
                  </th>
                  <th className='border border-gray-300 px-4 py-2 text-center'>
                    Weight
                  </th>
                  <th className='border border-gray-300 px-4 py-2 text-center'>
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className='bg-white hover:bg-gray-50'>
                  <td className='border border-gray-300 px-4 py-2 font-medium'>
                    Financial Viability
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.financial_score || 0).toFixed(1)}/100
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center font-semibold'>
                    {getGrade(submission.financial_score || 0)}
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    30%
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.financial_score || 0) >= 60 ? (
                      <span className='text-green-600 font-medium'>✓ Pass</span>
                    ) : (
                      <span className='text-red-600 font-medium'>✗ Fail</span>
                    )}
                  </td>
                </tr>
                <tr className='bg-gray-50 hover:bg-gray-100'>
                  <td className='border border-gray-300 px-4 py-2 font-medium'>
                    Market Demand
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.market_score || 0).toFixed(1)}/100
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center font-semibold'>
                    {getGrade(submission.market_score || 0)}
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    25%
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.market_score || 0) >= 60 ? (
                      <span className='text-green-600 font-medium'>✓ Pass</span>
                    ) : (
                      <span className='text-red-600 font-medium'>✗ Fail</span>
                    )}
                  </td>
                </tr>
                <tr className='bg-white hover:bg-gray-50'>
                  <td className='border border-gray-300 px-4 py-2 font-medium'>
                    Location Quality
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.location_score || 0).toFixed(1)}/100
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center font-semibold'>
                    {getGrade(submission.location_score || 0)}
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    20%
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.location_score || 0) >= 60 ? (
                      <span className='text-green-600 font-medium'>✓ Pass</span>
                    ) : (
                      <span className='text-red-600 font-medium'>✗ Fail</span>
                    )}
                  </td>
                </tr>
                <tr className='bg-gray-50 hover:bg-gray-100'>
                  <td className='border border-gray-300 px-4 py-2 font-medium'>
                    Partnership Alignment
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.partnership_score || 0).toFixed(1)}/100
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center font-semibold'>
                    {getGrade(submission.partnership_score || 0)}
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    15%
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.partnership_score || 0) >= 60 ? (
                      <span className='text-green-600 font-medium'>✓ Pass</span>
                    ) : (
                      <span className='text-red-600 font-medium'>✗ Fail</span>
                    )}
                  </td>
                </tr>
                <tr className='bg-white hover:bg-gray-50'>
                  <td className='border border-gray-300 px-4 py-2 font-medium'>
                    Risk Assessment
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.risk_score || 0).toFixed(1)}/100
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center font-semibold'>
                    {getGrade(submission.risk_score || 0)}
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    10%
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {(submission.risk_score || 0) >= 60 ? (
                      <span className='text-green-600 font-medium'>✓ Pass</span>
                    ) : (
                      <span className='text-red-600 font-medium'>✗ Fail</span>
                    )}
                  </td>
                </tr>
                <tr className='bg-gray-100 font-bold'>
                  <td className='border border-gray-300 px-4 py-2'>
                    OVERALL ASSESSMENT
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {score.toFixed(1)}/100
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {grade}
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    100%
                  </td>
                  <td className='border border-gray-300 px-4 py-2 text-center'>
                    {score >= 70 && !hasDealBreakers ? (
                      <span className='text-green-600'>✓ APPROVED</span>
                    ) : (
                      <span className='text-red-600'>✗ NOT APPROVED</span>
                    )}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Multi-Story Development Scenarios */}
      {submission.financial_projections?.multi_story_scenarios && (
        <Card className='mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              🏢 Development Scenarios Analysis
            </CardTitle>
            <p className='text-sm text-gray-600 mt-2'>
              Updated Requirements (Oct 2025): $325K/unit construction cost, 425
              sqft planning factor (gross area), 20% equity / 80% debt financing
            </p>
            <p className='text-sm text-gray-600 mt-1'>
              <strong>
                Unit totals based on conservative 65% site coverage
              </strong>{' '}
              (accounts for parking, setbacks, open space)
            </p>
          </CardHeader>
          <CardContent>
            <div className='overflow-x-auto'>
              <table className='w-full border-collapse'>
                <thead>
                  <tr className='bg-blue-600 text-white'>
                    <th className='border border-gray-300 px-4 py-2 text-left'>
                      Scenario
                    </th>
                    <th className='border border-gray-300 px-4 py-2 text-right'>
                      Units
                    </th>
                    <th className='border border-gray-300 px-4 py-2 text-right'>
                      IRR
                    </th>
                    <th className='border border-gray-300 px-4 py-2 text-right'>
                      Year 1 NOI
                    </th>
                    <th className='border border-gray-300 px-4 py-2 text-right'>
                      Dev Cost
                    </th>
                    <th className='border border-gray-300 px-4 py-2 text-right'>
                      Equity (20%)
                    </th>
                    <th className='border border-gray-300 px-4 py-2 text-right'>
                      Debt (80%)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {submission.financial_projections.multi_story_scenarios
                    .scenarios?.['3_story'] && (
                    <tr
                      className={
                        submission.financial_projections.multi_story_scenarios
                          .recommended === '3_story'
                          ? 'bg-green-50 hover:bg-green-100'
                          : 'bg-white hover:bg-gray-50'
                      }
                    >
                      <td className='border border-gray-300 px-4 py-2 font-medium'>
                        3-Story
                        {submission.financial_projections.multi_story_scenarios
                          .recommended === '3_story' && (
                          <Badge className='ml-2 bg-green-600'>
                            Recommended
                          </Badge>
                        )}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios.scenarios[
                          '3_story'
                        ].units.toLocaleString()}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right font-semibold text-green-600'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['3_story'].irr_percent
                          ? `${submission.financial_projections.multi_story_scenarios.scenarios[
                              '3_story'
                            ].irr_percent.toFixed(1)}%`
                          : 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['3_story'].noi_formatted || 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['3_story']
                          .total_development_cost_formatted || 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right text-blue-600 font-semibold'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['3_story'].equity_required_formatted ||
                          'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['3_story'].debt_financing_formatted ||
                          'N/A'}
                      </td>
                    </tr>
                  )}
                  {submission.financial_projections.multi_story_scenarios
                    .scenarios?.['4_story'] && (
                    <tr
                      className={
                        submission.financial_projections.multi_story_scenarios
                          .recommended === '4_story'
                          ? 'bg-green-50 hover:bg-green-100'
                          : 'bg-white hover:bg-gray-50'
                      }
                    >
                      <td className='border border-gray-300 px-4 py-2 font-medium'>
                        4-Story
                        {submission.financial_projections.multi_story_scenarios
                          .recommended === '4_story' && (
                          <Badge className='ml-2 bg-green-600'>
                            Recommended
                          </Badge>
                        )}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios.scenarios[
                          '4_story'
                        ].units.toLocaleString()}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right font-semibold text-green-600'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['4_story'].irr_percent
                          ? `${submission.financial_projections.multi_story_scenarios.scenarios[
                              '4_story'
                            ].irr_percent.toFixed(1)}%`
                          : 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['4_story'].noi_formatted || 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['4_story']
                          .total_development_cost_formatted || 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right text-blue-600 font-semibold'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['4_story'].equity_required_formatted ||
                          'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['4_story'].debt_financing_formatted ||
                          'N/A'}
                      </td>
                    </tr>
                  )}
                  {submission.financial_projections.multi_story_scenarios
                    .scenarios?.['5_story'] && (
                    <tr
                      className={
                        submission.financial_projections.multi_story_scenarios
                          .recommended === '5_story'
                          ? 'bg-green-50 hover:bg-green-100'
                          : 'bg-white hover:bg-gray-50'
                      }
                    >
                      <td className='border border-gray-300 px-4 py-2 font-medium'>
                        5-Story
                        {submission.financial_projections.multi_story_scenarios
                          .recommended === '5_story' && (
                          <Badge className='ml-2 bg-green-600'>
                            Recommended
                          </Badge>
                        )}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios.scenarios[
                          '5_story'
                        ].units.toLocaleString()}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right font-semibold text-green-600'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['5_story'].irr_percent
                          ? `${submission.financial_projections.multi_story_scenarios.scenarios[
                              '5_story'
                            ].irr_percent.toFixed(1)}%`
                          : 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['5_story'].noi_formatted || 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['5_story']
                          .total_development_cost_formatted || 'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right text-blue-600 font-semibold'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['5_story'].equity_required_formatted ||
                          'N/A'}
                      </td>
                      <td className='border border-gray-300 px-4 py-2 text-right'>
                        {submission.financial_projections.multi_story_scenarios
                          .scenarios['5_story'].debt_financing_formatted ||
                          'N/A'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {submission.financial_projections.multi_story_scenarios
              .recommended_reason && (
              <div className='mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200'>
                <p className='text-sm font-semibold text-blue-800'>
                  <strong>Recommended:</strong>{' '}
                  {submission.financial_projections.multi_story_scenarios.recommended
                    ?.replace('_', ' ')
                    .replace(/\b\w/g, (l: string) => l.toUpperCase())}
                </p>
                <p className='text-sm text-blue-700 mt-1'>
                  {
                    submission.financial_projections.multi_story_scenarios
                      .recommended_reason
                  }
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Parse property data sources for enriched Smarty data */}
      {(() => {
        let propertyData: any = null;
        try {
          if (submission.property_data_sources) {
            propertyData = JSON.parse(submission.property_data_sources);
          }
        } catch (e) {
          console.error('Failed to parse property_data_sources:', e);
        }

        const smartyData = propertyData?.smarty_data?.data;
        const multiAddressInfo = smartyData?.multi_address;
        const individualParcels = multiAddressInfo?.individual_parcels || [];

        // PRIORITY: Use manual user input FIRST, then fall back to API data
        // Check assessment.available_build_sqft (user's custom input from form)
        const lotData = smartyData?.lot;
        const buildingData = smartyData?.building;

        // PRIORITY 1: User's custom available build space from assessment form
        // PRIORITY 2: Property lot size (if entered separately)
        // PRIORITY 3: API data from Smarty
        const combinedLotSize =
          submission.available_build_sqft ||
          submission.property_lot_size_sqft ||
          multiAddressInfo?.combined_lot_size_sqft ||
          lotData?.size_sqft;
        const combinedLotAcres = combinedLotSize
          ? (combinedLotSize / 43560).toFixed(2)
          : lotData?.size_acres?.toFixed(2);

        // Calculate combined building size from individual parcels (includes ALL buildings regardless of demolish flag)
        let combinedBuildingSize = 0;
        if (individualParcels.length > 0) {
          combinedBuildingSize = individualParcels.reduce(
            (total: number, parcel: any) => {
              return total + (parcel?.building?.size_sqft || 0);
            },
            0
          );
        } else {
          combinedBuildingSize = buildingData?.size_sqft || 0;
        }

        // Calculate available build space - prioritize user input from assessment
        let availableBuildSpace = smartyData?.available_build_space;
        let isUserProvidedSpace = false;

        // PRIORITY 1: User provided custom available space in assessment form (most accurate)
        if (submission.available_build_sqft) {
          availableBuildSpace = {
            sqft: submission.available_build_sqft,
            acres:
              submission.available_build_acres ||
              submission.available_build_sqft / 43560,
            qualifies_for_logos: submission.available_build_sqft >= 10000,
            minimum_required: 10000,
          };
          isUserProvidedSpace = true;
        }
        // PRIORITY 2: User provided custom lot size (calculate available space)
        else if (submission.property_lot_size_sqft) {
          // If full demolition is selected, ALL land is available (don't subtract buildings)
          const userAvailableSpace = submission.property_demolish_all_structures
            ? submission.property_lot_size_sqft
            : submission.property_lot_size_sqft - combinedBuildingSize;
          availableBuildSpace = {
            sqft: userAvailableSpace,
            acres: userAvailableSpace / 43560,
            qualifies_for_logos: userAvailableSpace >= 10000,
            minimum_required: 10000,
          };
          // DO NOT set isUserProvidedSpace = true here
          // property_lot_size_sqft is standard form input, not a custom override
        }

        const valuationData = smartyData?.valuation;
        const financialData = smartyData?.financial;
        const ownerData = smartyData?.owner;
        const propertyTypeData = smartyData?.property_type;
        const floodData = smartyData?.flood;

        return (
          <>
            {/* Available Build Space - THE KEY METRIC */}
            {availableBuildSpace && (
              <Card className='mb-6 border-2 border-green-500 bg-gradient-to-br from-green-50 to-emerald-50'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2 text-green-700'>
                    <Target className='h-5 w-5' />
                    💰 Available Build Space - LOGOS Qualification
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='space-y-3'>
                    {/* Main Qualification Badge */}
                    <div className='text-center py-4 bg-white rounded-lg border-2 border-green-300'>
                      {availableBuildSpace.qualifies_for_logos ? (
                        <div>
                          <CheckCircle className='h-12 w-12 text-green-600 mx-auto mb-2' />
                          <h3 className='text-2xl font-bold text-green-700 mb-1'>
                            ✅ QUALIFIES FOR LOGOS
                          </h3>
                          <p className='text-base text-green-600'>
                            {availableBuildSpace.sqft?.toLocaleString()} sqft
                            available (Min:{' '}
                            {availableBuildSpace.minimum_required?.toLocaleString()}{' '}
                            sqft)
                          </p>
                        </div>
                      ) : (
                        <div>
                          <XCircle className='h-12 w-12 text-red-600 mx-auto mb-2' />
                          <h3 className='text-2xl font-bold text-red-700 mb-1'>
                            ❌ DOES NOT QUALIFY
                          </h3>
                          <p className='text-base text-red-600'>
                            {availableBuildSpace.sqft?.toLocaleString()} sqft
                            available (Min:{' '}
                            {availableBuildSpace.minimum_required?.toLocaleString()}{' '}
                            sqft required)
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Demolish Note */}
                    {(() => {
                      const isDemolish =
                        submission.property_demolish_all_structures;

                      if (isDemolish) {
                        return (
                          <div className='bg-amber-50 border border-amber-300 rounded-lg p-3 mb-3'>
                            <p className='text-sm text-amber-900 flex items-center gap-2'>
                              <Building2 className='h-4 w-4' />
                              <span className='font-semibold'>
                                Full Demolition:
                              </span>
                              <span>
                                Existing structures will be removed, maximizing
                                available build space
                              </span>
                            </p>
                          </div>
                        );
                      }
                      return null;
                    })()}

                    {/* Breakdown */}
                    <div className='grid grid-cols-1 md:grid-cols-3 gap-3'>
                      <div className='bg-blue-50 rounded-lg p-3 border border-blue-200'>
                        <p className='text-xs text-gray-600 mb-1'>
                          📐 Total Lot Size
                          {submission.available_build_sqft && (
                            <span
                              className='ml-1 text-amber-600'
                              title='User-provided value - verify with property owner'
                            >
                              ⚠️
                            </span>
                          )}
                        </p>
                        <p className='text-xl font-bold text-blue-700'>
                          {combinedLotSize?.toLocaleString() || 'N/A'}
                        </p>
                        <p className='text-xs text-gray-600'>
                          sqft ({combinedLotAcres || 'N/A'} acres)
                          {individualParcels.length > 0 &&
                            ` • ${individualParcels.length} parcel${
                              individualParcels.length > 1 ? 's' : ''
                            }`}
                          {submission.available_build_sqft && (
                            <span className='block text-amber-600 mt-1'>
                              User-provided
                            </span>
                          )}
                        </p>
                      </div>
                      <div className='bg-orange-50 rounded-lg p-3 border border-orange-200'>
                        <p className='text-xs text-gray-600 mb-1'>
                          🏠{' '}
                          {submission.property_demolish_all_structures
                            ? 'Existing Buildings'
                            : 'Building Size'}
                        </p>
                        <p className='text-xl font-bold text-orange-700'>
                          {combinedBuildingSize?.toLocaleString() || 'N/A'}
                        </p>
                        <p className='text-xs text-gray-600'>
                          sqft{' '}
                          {submission.property_demolish_all_structures &&
                            '(to be demolished)'}
                        </p>
                      </div>
                      <div className='bg-green-50 rounded-lg p-3 border border-green-200'>
                        <p className='text-xs text-gray-600 mb-1'>
                          ✨ Available Space
                          {isUserProvidedSpace && (
                            <span
                              className='ml-1 text-amber-600'
                              title='Calculated from user-provided lot size - verify with property owner'
                            >
                              ⚠️
                            </span>
                          )}
                        </p>
                        <p className='text-xl font-bold text-green-700'>
                          {availableBuildSpace.sqft?.toLocaleString() || 'N/A'}
                        </p>
                        <p className='text-xs text-gray-600'>
                          sqft ({availableBuildSpace.acres?.toFixed(2) || 'N/A'}{' '}
                          acres)
                          {isUserProvidedSpace && (
                            <span className='block text-amber-600 mt-1'>
                              Calculated from user input
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 📊 FINANCIAL PROJECTIONS & ANALYSIS - MOVED UP */}
            {submission.financial_projections && (
              <Card className='mb-6'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <DollarSign className='h-5 w-5' />
                    📊 Financial Projections & Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className='space-y-6'>
                  {/* 🎯 IRR & INVESTMENT RETURNS - FEATURED SECTION */}
                  {submission.financial_projections.revenue_projections
                    ?.irr_analysis && (
                    <div className='bg-gradient-to-br from-emerald-50 to-green-50 rounded-lg p-6 border-2 border-green-300'>
                      <div className='flex items-center justify-between mb-4 flex-wrap gap-2'>
                        <h3 className='text-2xl font-bold text-green-800 flex items-center gap-2'>
                          <TrendingUp className='h-6 w-6' />
                          💰 IRR & Investment Returns
                        </h3>
                        {submission.financial_projections.revenue_projections
                          .irr_analysis.meets_logos_target && (
                          <Badge className='bg-green-600 text-white text-base px-4 py-1.5'>
                            ✅ MEETS 20% TARGET
                          </Badge>
                        )}
                      </div>

                      {/* Main IRR Display */}
                      <div className='text-center bg-white rounded-lg p-6 mb-4 border-2 border-green-400'>
                        <p className='text-sm text-gray-600 mb-2'>
                          10-Year IRR (with Tax Benefits)
                        </p>
                        <p className='text-6xl font-bold text-green-700 mb-2'>
                          {submission.financial_projections.revenue_projections.irr_analysis.irr_percent?.toFixed(
                            1
                          )}
                          %
                        </p>
                        <p className='text-base text-gray-600'>
                          Target: 20% minimum • Exit Cap:{' '}
                          {(
                            (submission.financial_projections
                              .revenue_projections.irr_analysis.exit_cap_rate ||
                              0.0425) * 100
                          ).toFixed(2)}
                          % • Rent Growth:{' '}
                          {(
                            (submission.financial_projections
                              .revenue_projections.irr_analysis
                              .annual_rent_growth || 0.03) * 100
                          ).toFixed(0)}
                          %/yr
                        </p>
                      </div>

                      {/* Tax Benefits Breakdown */}
                      {(submission.financial_projections.revenue_projections
                        .irr_analysis.lihtc_proceeds ||
                        submission.financial_projections.revenue_projections
                          .irr_analysis.annual_property_tax_savings) && (
                        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
                          {/* LIHTC 4% Credits */}
                          {submission.financial_projections.revenue_projections
                            .irr_analysis.lihtc_proceeds && (
                            <div className='bg-blue-50 rounded-lg p-4 border border-blue-200'>
                              <p className='text-sm font-semibold text-blue-900 mb-2'>
                                🏆 LIHTC 4% Tax Credits
                              </p>
                              <p className='text-2xl font-bold text-blue-700 mb-1'>
                                $
                                {submission.financial_projections.revenue_projections.irr_analysis.lihtc_proceeds?.toLocaleString()}
                              </p>
                              <p className='text-xs text-gray-600'>
                                Syndication proceeds (received at construction)
                              </p>
                            </div>
                          )}

                          {/* CA Welfare Exemption */}
                          {submission.financial_projections.revenue_projections
                            .irr_analysis.annual_property_tax_savings && (
                            <div className='bg-amber-50 rounded-lg p-4 border border-amber-200'>
                              <p className='text-sm font-semibold text-amber-900 mb-2'>
                                💸 CA Welfare Tax Exemption
                              </p>
                              <p className='text-2xl font-bold text-amber-700 mb-1'>
                                $
                                {submission.financial_projections.revenue_projections.irr_analysis.annual_property_tax_savings?.toLocaleString()}
                                /yr
                              </p>
                              <p className='text-xs text-gray-600'>
                                98% property tax savings (increases NOI)
                              </p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Equity Analysis */}
                      {(submission.financial_projections.revenue_projections
                        .irr_analysis.gross_equity_required ||
                        submission.financial_projections.revenue_projections
                          .irr_analysis.net_equity_required) && (
                        <div className='bg-purple-50 rounded-lg p-4 border border-purple-200 mb-4'>
                          <p className='text-sm font-semibold text-purple-900 mb-3'>
                            💼 Equity Analysis
                          </p>
                          <div className='grid grid-cols-3 gap-4 text-center'>
                            <div>
                              <p className='text-xs text-gray-600 mb-1'>
                                Gross Equity (20%)
                              </p>
                              <p className='text-lg font-bold text-purple-700'>
                                $
                                {submission.financial_projections.revenue_projections.irr_analysis.gross_equity_required?.toLocaleString() ||
                                  'N/A'}
                              </p>
                            </div>
                            <div>
                              <p className='text-xs text-gray-600 mb-1'>
                                LIHTC Reduction
                              </p>
                              <p className='text-lg font-bold text-green-700'>
                                -$
                                {submission.financial_projections.revenue_projections.irr_analysis.equity_reduction_from_lihtc?.toLocaleString() ||
                                  '0'}
                              </p>
                            </div>
                            <div>
                              <p className='text-xs text-gray-600 mb-1'>
                                Net Equity Required
                              </p>
                              <p className='text-lg font-bold text-emerald-700'>
                                $
                                {submission.financial_projections.revenue_projections.irr_analysis.net_equity_required?.toLocaleString() ||
                                  'N/A'}
                              </p>
                              {submission.financial_projections
                                .revenue_projections.irr_analysis
                                .essentially_zero_equity && (
                                <p className='text-[10px] text-green-600 font-semibold mt-1'>
                                  ✨ ESSENTIALLY ZERO!
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Key Highlights */}
                      {submission.financial_projections.revenue_projections
                        .irr_analysis.highlights &&
                        submission.financial_projections.revenue_projections
                          .irr_analysis.highlights.length > 0 && (
                          <div className='bg-white rounded-lg p-4 border border-gray-200'>
                            <p className='text-sm font-semibold text-gray-700 mb-2'>
                              📌 Key Highlights
                            </p>
                            <ul className='space-y-1 text-sm text-gray-700'>
                              {submission.financial_projections.revenue_projections.irr_analysis.highlights.map(
                                (highlight: string, idx: number) => (
                                  <li
                                    key={idx}
                                    className='flex items-start gap-2'
                                  >
                                    <CheckCircle className='h-4 w-4 text-green-600 flex-shrink-0 mt-0.5' />
                                    <span>{highlight}</span>
                                  </li>
                                )
                              )}
                            </ul>
                          </div>
                        )}
                    </div>
                  )}

                  {/* Unit Capacity */}
                  {submission.financial_projections.multi_story_scenarios && (
                    <div>
                      <h4 className='font-semibold mb-3 text-blue-700 flex items-center gap-2'>
                        Unit Capacity Analysis
                        {(() => {
                          const additionalAddresses =
                            submission.property_additional_addresses || [];
                          const totalParcels = 1 + additionalAddresses.length;
                          if (totalParcels > 1) {
                            return (
                              <span className='text-xs font-normal text-gray-600 bg-gray-100 px-2 py-1 rounded'>
                                Based on{' '}
                                {combinedLotSize?.toLocaleString() || 'N/A'}{' '}
                                sqft ({totalParcels} parcels)
                              </span>
                            );
                          }
                          return null;
                        })()}
                      </h4>
                      <div className='grid grid-cols-2 md:grid-cols-5 gap-4'>
                        {(() => {
                          // Get recommended scenario or fallback to available scenarios
                          const scenarios =
                            submission.financial_projections
                              .multi_story_scenarios.scenarios;
                          const recommended =
                            submission.financial_projections
                              .multi_story_scenarios.recommended;
                          const recommendedScenario =
                            scenarios?.[recommended] ||
                            scenarios?.['5_story'] ||
                            scenarios?.['4_story'] ||
                            scenarios?.['3_story'] ||
                            {};

                          const totalUnits = recommendedScenario.units || 0;
                          const avgUnitSize = 425; // Efficiency planning factor (gross building area per unit, ~88% efficiency)

                          // Unit mix: 20% studios (325sf), 55% 1BR (450sf), 25% 2BR (675sf)
                          const studioUnits = Math.floor(totalUnits * 0.2);
                          const oneBedUnits = Math.floor(totalUnits * 0.55);
                          const twoBedUnits = Math.floor(totalUnits * 0.25);

                          return (
                            <>
                              <div className='bg-blue-50 rounded-lg p-3'>
                                <p className='text-sm text-gray-600'>
                                  Feasible Units
                                </p>
                                <p className='text-2xl font-bold text-blue-600'>
                                  {totalUnits}
                                </p>
                                <p className='text-[10px] text-gray-500 mt-1'>
                                  {recommended
                                    ?.replace('_', '-')
                                    .replace(/\b\w/g, (l: string) =>
                                      l.toUpperCase()
                                    )}{' '}
                                  scenario
                                </p>
                              </div>
                              <div className='bg-gray-50 rounded-lg p-3'>
                                <p className='text-sm text-gray-600'>
                                  Studio (325 sf)
                                </p>
                                <p className='text-xl font-semibold'>
                                  {studioUnits}
                                </p>
                                <p className='text-[10px] text-gray-500 mt-1'>
                                  20% of units
                                </p>
                              </div>
                              <div className='bg-gray-50 rounded-lg p-3'>
                                <p className='text-sm text-gray-600'>
                                  1-Bedroom (450 sf)
                                </p>
                                <p className='text-xl font-semibold'>
                                  {oneBedUnits}
                                </p>
                                <p className='text-[10px] text-gray-500 mt-1'>
                                  55% of units
                                </p>
                              </div>
                              <div className='bg-gray-50 rounded-lg p-3'>
                                <p className='text-sm text-gray-600'>
                                  2-Bedroom (675 sf)
                                </p>
                                <p className='text-xl font-semibold'>
                                  {twoBedUnits}
                                </p>
                                <p className='text-[10px] text-gray-500 mt-1'>
                                  25% of units
                                </p>
                              </div>
                              <div className='bg-gray-50 rounded-lg p-3'>
                                <p className='text-sm text-gray-600'>
                                  Avg Unit Size
                                </p>
                                <p className='text-xl font-semibold'>
                                  {avgUnitSize} sf
                                </p>
                                <p className='text-[10px] text-gray-500 mt-1'>
                                  Planning factor (gross area)
                                </p>
                              </div>
                            </>
                          );
                        })()}
                      </div>
                      {(() => {
                        // Check if feasible units meet minimum threshold
                        const scenarios =
                          submission.financial_projections.multi_story_scenarios
                            .scenarios;
                        const recommended =
                          submission.financial_projections.multi_story_scenarios
                            .recommended;
                        const recommendedScenario =
                          scenarios?.[recommended] ||
                          scenarios?.['5_story'] ||
                          scenarios?.['4_story'] ||
                          scenarios?.['3_story'] ||
                          {};
                        const totalUnits = recommendedScenario.units || 0;

                        return (
                          totalUnits < 40 && (
                            <div className='mt-3 bg-red-100 border border-red-300 rounded-lg p-3'>
                              <p className='text-sm text-red-800 font-medium'>
                                ⚠️ Below minimum threshold: Logos requires 40+
                                units for financial viability
                              </p>
                            </div>
                          )
                        );
                      })()}
                    </div>
                  )}

                  {/* Development Costs */}
                  {submission.financial_projections.total_development_cost && (
                    <div>
                      <h4 className='font-semibold mb-3 text-blue-700'>
                        Development Cost Breakdown
                      </h4>
                      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
                        <div className='bg-gray-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>
                            Total Development Cost
                          </p>
                          <p className='text-xl font-bold text-blue-600'>
                            $
                            {submission.financial_projections.total_development_cost.toLocaleString()}
                          </p>
                        </div>
                        <div className='bg-gray-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>Cost Per Unit</p>
                          <p className='text-xl font-bold text-blue-600'>
                            $
                            {submission.financial_projections.adjusted_cost_per_unit?.toLocaleString() ||
                              'N/A'}
                          </p>
                          <p className='text-xs text-gray-500 mt-1'>
                            Target: ≤$325,000/unit
                          </p>
                        </div>
                        <div className='bg-gray-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>
                            Land Acquisition
                          </p>
                          <p className='text-lg font-semibold'>
                            $
                            {submission.financial_projections.land_acquisition_cost?.toLocaleString() ||
                              '0'}
                          </p>
                          <p className='text-xs text-gray-500 mt-1'>
                            Church contribution
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Revenue Projections - Simplified */}
                  {submission.financial_projections.revenue_projections && (
                    <div>
                      <h4 className='font-semibold mb-3 text-green-700'>
                        Revenue & Operating Performance
                      </h4>
                      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
                        <div className='bg-green-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>
                            Annual Revenue
                          </p>
                          <p className='text-xl font-bold text-green-600'>
                            $
                            {submission.financial_projections.revenue_projections.total_annual_revenue?.toLocaleString() ||
                              'N/A'}
                          </p>
                        </div>
                        <div className='bg-yellow-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>
                            Operating Expenses
                          </p>
                          <p className='text-xl font-bold text-yellow-600'>
                            $
                            {submission.financial_projections.revenue_projections.operating_expenses?.toLocaleString() ||
                              'N/A'}
                          </p>
                          <p className='text-xs text-gray-500 mt-1'>
                            {submission.financial_projections
                              .revenue_projections.operating_expense_ratio ||
                              '42%'}
                          </p>
                        </div>
                        <div className='bg-blue-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>
                            Net Operating Income
                          </p>
                          <p className='text-xl font-bold text-blue-600'>
                            $
                            {submission.financial_projections.revenue_projections.net_operating_income?.toLocaleString() ||
                              'N/A'}
                          </p>
                        </div>
                        <div className='bg-purple-50 rounded-lg p-3'>
                          <p className='text-sm text-gray-600'>Yield on Cost</p>
                          <p className='text-xl font-bold text-purple-600'>
                            {submission.financial_projections
                              .revenue_projections.yield_on_cost ||
                            submission.financial_projections.revenue_projections
                              .cap_rate
                              ? `${(
                                  submission.financial_projections
                                    .revenue_projections.yield_on_cost ||
                                  submission.financial_projections
                                    .revenue_projections.cap_rate
                                ).toFixed(2)}%`
                              : 'N/A'}
                          </p>
                          <p className='text-xs text-gray-500 mt-1'>
                            Target: 7%
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Assumptions */}
                  {submission.financial_projections.revenue_projections
                    ?.assumptions && (
                    <div>
                      <h4 className='font-semibold mb-3 text-gray-700'>
                        Key Assumptions
                      </h4>
                      <div className='bg-gray-50 rounded-lg p-4'>
                        <ul className='grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700'>
                          {submission.financial_projections.revenue_projections.assumptions.map(
                            (assumption: string, idx: number) => (
                              <li key={idx} className='flex items-start gap-2'>
                                <Info className='h-4 w-4 text-gray-400 flex-shrink-0 mt-0.5' />
                                <span>{assumption}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Property Valuation */}
            {valuationData && (
              <Card className='mb-6'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <DollarSign className='h-5 w-5' />
                    💵 Property Valuation & Assessment
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='space-y-4'>
                    {/* Market Value Range */}
                    <div className='bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border-2 border-green-200'>
                      <p className='text-sm text-gray-600 mb-2'>
                        📈 Estimated Market Value
                      </p>
                      <p className='text-3xl font-bold text-green-700'>
                        ${valuationData.estimated_market_min?.toLocaleString()}{' '}
                        - $
                        {valuationData.estimated_market_max?.toLocaleString()}
                      </p>
                      <p className='text-xs text-gray-600 mt-1'>
                        {valuationData.note ||
                          'Based on 3-5x multiplier of assessed value'}
                      </p>
                    </div>

                    {/* Assessed Value Breakdown */}
                    <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                      <div className='bg-blue-50 rounded-lg p-4 border border-blue-200'>
                        <p className='text-sm text-gray-600 mb-1'>
                          🏛️ Assessed Total
                        </p>
                        <p className='text-xl font-bold text-blue-700'>
                          $
                          {valuationData.assessed_total?.toLocaleString() ||
                            'N/A'}
                        </p>
                        <p className='text-xs text-gray-600'>
                          Tax Year: {valuationData.assessed_year || 'N/A'}
                        </p>
                      </div>
                      <div className='bg-amber-50 rounded-lg p-4 border border-amber-200'>
                        <p className='text-sm text-gray-600 mb-1'>
                          🌍 Land Value
                        </p>
                        <p className='text-xl font-bold text-amber-700'>
                          $
                          {valuationData.assessed_land?.toLocaleString() ||
                            'N/A'}
                        </p>
                        <p className='text-xs text-gray-600'>
                          Assessed land only
                        </p>
                      </div>
                      <div className='bg-purple-50 rounded-lg p-4 border border-purple-200'>
                        <p className='text-sm text-gray-600 mb-1'>
                          🏗️ Improvement Value
                        </p>
                        <p className='text-xl font-bold text-purple-700'>
                          $
                          {valuationData.assessed_improvement?.toLocaleString() ||
                            'N/A'}
                        </p>
                        <p className='text-xs text-gray-600'>
                          Buildings & structures
                        </p>
                      </div>
                    </div>

                    {/* CA Prop 13 Notice */}
                    <div className='bg-yellow-50 border border-yellow-300 rounded-lg p-3'>
                      <div className='flex items-start gap-2'>
                        <Info className='h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5' />
                        <div>
                          <p className='font-semibold text-yellow-800 text-sm'>
                            California Prop 13 Impact
                          </p>
                          <p className='text-xs text-yellow-700 mt-1'>
                            Assessed values are capped at 2% annual increase
                            since last sale. For long-held properties, market
                            value is typically 3-5x higher than assessed value.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Ownership & Financial History */}
            {(ownerData || financialData) && (
              <Card className='mb-6'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <Users className='h-5 w-5' />
                    👤 Ownership & Financial Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='space-y-4'>
                    {/* Owner Information */}
                    {ownerData && (
                      <div className='bg-blue-50 rounded-lg p-4 border border-blue-200'>
                        <h4 className='font-semibold text-blue-900 mb-3'>
                          Current Owner
                        </h4>
                        <div className='space-y-2'>
                          <div>
                            <p className='text-sm text-gray-600'>Owner Name</p>
                            <p className='font-semibold text-gray-900'>
                              {ownerData.name || 'N/A'}
                            </p>
                          </div>
                          <div className='grid grid-cols-2 gap-4'>
                            <div>
                              <p className='text-sm text-gray-600'>
                                Purchase Date
                              </p>
                              <p className='font-semibold text-gray-900'>
                                {ownerData.last_sale_date || 'N/A'}
                              </p>
                            </div>
                            <div>
                              <p className='text-sm text-gray-600'>
                                Purchase Price
                              </p>
                              <p className='font-semibold text-gray-900'>
                                $
                                {ownerData.last_sale_price?.toLocaleString() ||
                                  'N/A'}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Mortgage Status */}
                    {financialData && (
                      <div>
                        {financialData.has_mortgages ? (
                          <div className='bg-orange-50 rounded-lg p-4 border border-orange-200'>
                            <div className='flex items-start gap-2 mb-3'>
                              <AlertCircle className='h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5' />
                              <div>
                                <h4 className='font-semibold text-orange-900'>
                                  🏦 Active Mortgages
                                </h4>
                                <p className='text-sm text-orange-700'>
                                  {financialData.mortgage_count} mortgage(s)
                                  totaling $
                                  {financialData.total_mortgage_amount?.toLocaleString() ||
                                    'N/A'}
                                </p>
                              </div>
                            </div>
                            {financialData.mortgages &&
                              financialData.mortgages.length > 0 && (
                                <div className='space-y-2 mt-3'>
                                  {financialData.mortgages.map(
                                    (mortgage: any, idx: number) => (
                                      <div
                                        key={idx}
                                        className='bg-white rounded p-3 border border-orange-200'
                                      >
                                        <div className='grid grid-cols-2 gap-2 text-sm'>
                                          <div>
                                            <p className='text-gray-600'>
                                              Amount
                                            </p>
                                            <p className='font-semibold'>
                                              $
                                              {mortgage.amount?.toLocaleString()}
                                            </p>
                                          </div>
                                          <div>
                                            <p className='text-gray-600'>
                                              Lender
                                            </p>
                                            <p className='font-semibold'>
                                              {mortgage.lender_name || 'N/A'}
                                            </p>
                                          </div>
                                          <div>
                                            <p className='text-gray-600'>
                                              Recording Date
                                            </p>
                                            <p className='font-semibold'>
                                              {mortgage.recording_date || 'N/A'}
                                            </p>
                                          </div>
                                          <div>
                                            <p className='text-gray-600'>
                                              Term
                                            </p>
                                            <p className='font-semibold'>
                                              {mortgage.term}{' '}
                                              {mortgage.term_type || 'Years'}
                                            </p>
                                          </div>
                                        </div>
                                      </div>
                                    )
                                  )}
                                </div>
                              )}
                          </div>
                        ) : (
                          <div className='bg-green-50 rounded-lg p-4 border border-green-200'>
                            <div className='flex items-start gap-2'>
                              <CheckCircle className='h-5 w-5 text-green-600 flex-shrink-0 mt-0.5' />
                              <div>
                                <h4 className='font-semibold text-green-900'>
                                  ✅ Owned Free & Clear
                                </h4>
                                <p className='text-sm text-green-700'>
                                  No active mortgages or liens detected.
                                  Property appears to be owned outright.
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Zoning & Land Use */}
            {propertyTypeData && (
              <Card className='mb-6'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <MapPin className='h-5 w-5' />
                    🗺️ Zoning & Land Use Classification
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                    <div className='bg-indigo-50 rounded-lg p-4 border border-indigo-200'>
                      <p className='text-sm text-gray-600 mb-1'>Zoning Code</p>
                      <p className='text-2xl font-bold text-indigo-700'>
                        {propertyTypeData.zoning || 'N/A'}
                      </p>
                      <p className='text-xs text-gray-600 mt-1'>
                        {propertyTypeData.rdi || 'Classification N/A'}
                      </p>
                    </div>
                    <div className='bg-purple-50 rounded-lg p-4 border border-purple-200'>
                      <p className='text-sm text-gray-600 mb-1'>Land Use</p>
                      <p className='text-base font-bold text-purple-700 break-words'>
                        {propertyTypeData.land_use || 'N/A'}
                      </p>
                      <p className='text-xs text-gray-600 mt-1'>
                        Code: {propertyTypeData.land_use_code || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Parcel Information */}
                  {lotData &&
                    (lotData.parcel_number || lotData.lot_numbers) && (
                      <div className='mt-4 bg-gray-50 rounded-lg p-4 border border-gray-200'>
                        <h4 className='font-semibold text-gray-900 mb-2'>
                          Parcel Details
                        </h4>
                        <div className='grid grid-cols-2 gap-3 text-sm'>
                          {lotData.parcel_number && (
                            <div>
                              <p className='text-gray-600'>
                                APN / Parcel Number
                              </p>
                              <p className='font-semibold font-mono'>
                                {lotData.parcel_number}
                              </p>
                            </div>
                          )}
                          {lotData.lot_numbers && (
                            <div>
                              <p className='text-gray-600'>Lot Numbers</p>
                              <p className='font-semibold font-mono'>
                                {lotData.lot_numbers}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                </CardContent>
              </Card>
            )}

            {/* Flood Risk */}
            {floodData && (
              <Card className='mb-6'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <AlertTriangle className='h-5 w-5' />
                    🌊 Flood Risk & Insurance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                    <div
                      className={`rounded-lg p-4 border-2 ${
                        floodData.risk_level === 'low' ||
                        floodData.risk_level === 'minimal'
                          ? 'bg-green-50 border-green-200'
                          : floodData.risk_level === 'moderate'
                          ? 'bg-yellow-50 border-yellow-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <p className='text-sm text-gray-600'>Flood Zone</p>
                      <p className='text-2xl font-bold'>
                        {floodData.flood_zone || 'N/A'}
                      </p>
                    </div>
                    <div
                      className={`rounded-lg p-4 border-2 ${
                        floodData.risk_level === 'low' ||
                        floodData.risk_level === 'minimal'
                          ? 'bg-green-50 border-green-200'
                          : floodData.risk_level === 'moderate'
                          ? 'bg-yellow-50 border-yellow-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <p className='text-sm text-gray-600'>Risk Level</p>
                      <p className='text-2xl font-bold capitalize'>
                        {floodData.risk_level || 'N/A'}
                      </p>
                    </div>
                    <div
                      className={`rounded-lg p-4 border-2 ${
                        floodData.insurance_required
                          ? 'bg-orange-50 border-orange-200'
                          : 'bg-green-50 border-green-200'
                      }`}
                    >
                      <p className='text-sm text-gray-600'>
                        Insurance Required
                      </p>
                      <p className='text-2xl font-bold'>
                        {floodData.insurance_required ? '⚠️ Yes' : '✅ No'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        );
      })()}

      {/* HUD Fair Market Rent Data */}
      {submission.market_analysis?.fair_market_rent && (
        <Card className='mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <TrendingUp className='h-5 w-5' />
              HUD Fair Market Rent (Section 8)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='grid grid-cols-2 md:grid-cols-5 gap-3'>
              <div className='bg-blue-50 rounded-lg p-3 text-center'>
                <p className='text-xs text-gray-600'>Studio</p>
                <p className='text-lg font-bold text-blue-600'>
                  $
                  {submission.market_analysis.fair_market_rent.studio?.toLocaleString() ||
                    'N/A'}
                </p>
                <p className='text-xs text-gray-500'>per month</p>
              </div>
              <div className='bg-blue-50 rounded-lg p-3 text-center'>
                <p className='text-xs text-gray-600'>1-Bedroom</p>
                <p className='text-lg font-bold text-blue-600'>
                  $
                  {submission.market_analysis.fair_market_rent.one_bedroom?.toLocaleString() ||
                    'N/A'}
                </p>
                <p className='text-xs text-gray-500'>per month</p>
              </div>
              <div className='bg-blue-50 rounded-lg p-3 text-center'>
                <p className='text-xs text-gray-600'>2-Bedroom</p>
                <p className='text-lg font-bold text-blue-600'>
                  $
                  {submission.market_analysis.fair_market_rent.two_bedroom?.toLocaleString() ||
                    'N/A'}
                </p>
                <p className='text-xs text-gray-500'>per month</p>
              </div>
              <div className='bg-blue-50 rounded-lg p-3 text-center'>
                <p className='text-xs text-gray-600'>3-Bedroom</p>
                <p className='text-lg font-bold text-blue-600'>
                  $
                  {submission.market_analysis.fair_market_rent.three_bedroom?.toLocaleString() ||
                    'N/A'}
                </p>
                <p className='text-xs text-gray-500'>per month</p>
              </div>
              <div className='bg-blue-50 rounded-lg p-3 text-center'>
                <p className='text-xs text-gray-600'>4-Bedroom</p>
                <p className='text-lg font-bold text-blue-600'>
                  $
                  {submission.market_analysis.fair_market_rent.four_bedroom?.toLocaleString() ||
                    'N/A'}
                </p>
                <p className='text-xs text-gray-500'>per month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AMI Limits */}
      {submission.market_analysis?.ami_limits && (
        <Card className='mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <TrendingUp className='h-5 w-5' />
              Area Median Income (AMI) Limits
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='grid grid-cols-2 md:grid-cols-4 gap-3'>
              <div className='bg-purple-50 rounded p-3 text-center'>
                <p className='text-xs text-gray-600'>50% AMI (2-person)</p>
                <p className='text-sm font-bold text-purple-600'>
                  $
                  {submission.market_analysis.ami_limits.ami_50_percent_2person?.toLocaleString() ||
                    'N/A'}
                </p>
              </div>
              <div className='bg-purple-50 rounded p-3 text-center'>
                <p className='text-xs text-gray-600'>60% AMI (2-person)</p>
                <p className='text-sm font-bold text-purple-600'>
                  $
                  {submission.market_analysis.ami_limits.ami_60_percent_2person?.toLocaleString() ||
                    'N/A'}
                </p>
              </div>
              <div className='bg-purple-50 rounded p-3 text-center'>
                <p className='text-xs text-gray-600'>80% AMI (2-person)</p>
                <p className='text-sm font-bold text-purple-600'>
                  $
                  {submission.market_analysis.ami_limits.ami_80_percent_2person?.toLocaleString() ||
                    'N/A'}
                </p>
              </div>
              <div className='bg-purple-50 rounded p-3 text-center'>
                <p className='text-xs text-gray-600'>100% AMI (2-person)</p>
                <p className='text-sm font-bold text-purple-600'>
                  $
                  {submission.market_analysis.ami_limits.ami_100_percent_2person?.toLocaleString() ||
                    'N/A'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Census Demographics */}
      {submission.market_analysis?.census_data && (
        <Card className='mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <TrendingUp className='h-5 w-5' />
              Demographics (Census Data)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {submission.market_analysis.ami_limits && (
              <div>
                <h4 className='font-semibold mb-3 text-purple-700'>
                  Area Median Income (AMI) Limits
                </h4>
                <div className='grid grid-cols-2 md:grid-cols-4 gap-3'>
                  <div className='bg-purple-50 rounded p-3 text-center'>
                    <p className='text-xs text-gray-600'>50% AMI (2-person)</p>
                    <p className='text-sm font-bold text-purple-600'>
                      $
                      {submission.market_analysis.ami_limits.ami_50_percent_2person?.toLocaleString() ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-purple-50 rounded p-3 text-center'>
                    <p className='text-xs text-gray-600'>60% AMI (2-person)</p>
                    <p className='text-sm font-bold text-purple-600'>
                      $
                      {submission.market_analysis.ami_limits.ami_60_percent_2person?.toLocaleString() ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-purple-50 rounded p-3 text-center'>
                    <p className='text-xs text-gray-600'>80% AMI (2-person)</p>
                    <p className='text-sm font-bold text-purple-600'>
                      $
                      {submission.market_analysis.ami_limits.ami_80_percent_2person?.toLocaleString() ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-purple-50 rounded p-3 text-center'>
                    <p className='text-xs text-gray-600'>100% AMI (2-person)</p>
                    <p className='text-sm font-bold text-purple-600'>
                      $
                      {submission.market_analysis.ami_limits.ami_100_percent_2person?.toLocaleString() ||
                        'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Census Demographics */}
            {submission.market_analysis.census_data && (
              <div>
                <h4 className='font-semibold mb-3 text-gray-700'>
                  Demographics (Census Data)
                </h4>
                <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
                  <div className='bg-gray-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Total Population</p>
                    <p className='text-xl font-bold'>
                      {submission.market_analysis.census_data.total_population?.toLocaleString() ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-gray-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Median Income</p>
                    <p className='text-xl font-bold'>
                      $
                      {submission.market_analysis.census_data.median_income?.toLocaleString() ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-gray-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Poverty Rate</p>
                    <p className='text-xl font-bold'>
                      {submission.market_analysis.census_data.poverty_rate ||
                        'N/A'}
                      %
                    </p>
                  </div>
                  <div className='bg-gray-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Renter Households</p>
                    <p className='text-xl font-bold'>
                      {submission.market_analysis.census_data
                        .renter_percentage || 'N/A'}
                      %
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Risk Factors & Mitigation */}
      {submission.risk_factors && (
        <Card className='mb-6'>
          <CardHeader>
            <CardTitle className='flex items-center gap-2'>
              <AlertTriangle className='h-5 w-5' />
              Risk Assessment & Mitigation Costs
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-6'>
            {/* Identified Risks */}
            {submission.risk_factors.identified_risks &&
              submission.risk_factors.identified_risks.length > 0 && (
                <div>
                  <h4 className='font-semibold mb-3 text-red-700'>
                    Identified Risks
                  </h4>
                  <div className='space-y-2'>
                    {submission.risk_factors.identified_risks.map(
                      (risk: string, index: number) => (
                        <div
                          key={index}
                          className='flex items-start gap-2 bg-red-50 border border-red-200 rounded p-3'
                        >
                          <AlertTriangle className='h-5 w-5 text-red-600 mt-0.5 flex-shrink-0' />
                          <span className='text-gray-800'>{risk}</span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

            {/* Mitigation Costs */}
            {submission.risk_factors.mitigation_costs && (
              <div>
                <h4 className='font-semibold mb-3 text-yellow-700'>
                  Mitigation Cost Estimates
                </h4>
                <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4'>
                  <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                    {Object.entries(
                      submission.risk_factors.mitigation_costs
                    ).map(([key, value]) => (
                      <div
                        key={key}
                        className='flex justify-between items-center'
                      >
                        <span className='text-gray-700 text-sm'>
                          {key
                            .replace(/_/g, ' ')
                            .replace(/\b\w/g, (l) => l.toUpperCase())}
                          :
                        </span>
                        <span className='font-bold text-lg'>
                          $
                          {typeof value === 'number'
                            ? value.toLocaleString()
                            : 'N/A'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Flood Zone Analysis */}
            {submission.risk_factors.flood_analysis && (
              <div>
                <h4 className='font-semibold mb-3 text-blue-700'>
                  Flood Risk Analysis
                </h4>
                <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                  <div className='bg-blue-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Flood Zone</p>
                    <p className='text-xl font-bold text-blue-600'>
                      {submission.risk_factors.flood_analysis.flood_zone ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-blue-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Risk Level</p>
                    <p className='text-xl font-bold text-blue-600 capitalize'>
                      {submission.risk_factors.flood_analysis.risk_level ||
                        'N/A'}
                    </p>
                  </div>
                  <div className='bg-blue-50 rounded-lg p-3'>
                    <p className='text-sm text-gray-600'>Insurance Required</p>
                    <p className='text-xl font-bold text-blue-600'>
                      {submission.risk_factors.flood_analysis.insurance_required
                        ? 'Yes'
                        : 'No'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Comparable Projects */}
      {submission.comparable_projects &&
        submission.comparable_projects.projects &&
        submission.comparable_projects.projects.length > 0 && (
          <Card className='mb-6'>
            <CardHeader>
              <CardTitle className='flex items-center gap-2'>
                <Building2 className='h-5 w-5' />
                Comparable Projects Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                {submission.comparable_projects.projects.map(
                  (project: any, index: number) => (
                    <div
                      key={index}
                      className='bg-gray-50 border border-gray-200 rounded-lg p-4'
                    >
                      <h4 className='font-semibold text-lg mb-2'>
                        {project.name || `Project ${index + 1}`}
                      </h4>
                      <div className='grid grid-cols-2 md:grid-cols-4 gap-3 text-sm'>
                        <div>
                          <p className='text-gray-600'>Location</p>
                          <p className='font-semibold'>
                            {project.location || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className='text-gray-600'>Units</p>
                          <p className='font-semibold'>
                            {project.units || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className='text-gray-600'>Cost per Unit</p>
                          <p className='font-semibold'>
                            ${project.cost_per_unit?.toLocaleString() || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className='text-gray-600'>Year Completed</p>
                          <p className='font-semibold'>
                            {project.year_completed || 'N/A'}
                          </p>
                        </div>
                      </div>
                      {project.notes && (
                        <p className='mt-2 text-sm text-gray-700 italic'>
                          {project.notes}
                        </p>
                      )}
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>
        )}
    </div>
  );
}
