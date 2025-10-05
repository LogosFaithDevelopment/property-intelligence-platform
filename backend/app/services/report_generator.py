"""
PDF Report Generation Service
Generates investor-ready PDF reports from property assessments
"""

import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from matplotlib.patches import Wedge
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate professional PDF reports for property assessments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=5,
            borderRadius=2
        ))
        
        # Grade style (large centered)
        self.styles.add(ParagraphStyle(
            name='GradeStyle',
            parent=self.styles['Normal'],
            fontSize=28,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=15,
            spaceBefore=15
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        ))
    
    async def generate_assessment_report(
        self,
        assessment_id: int,
        include_detailed_analysis: bool = True
    ) -> bytes:
        """
        Generate a comprehensive PDF report for an assessment
        
        Args:
            assessment_id: ID of the assessment to generate report for
            include_detailed_analysis: Include detailed market/financial analysis
            
        Returns:
            PDF file as bytes
        """
        # Fetch data
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        property_obj = self.db.query(Property).filter(Property.id == assessment.property_id).first()
        if not property_obj:
            raise ValueError(f"Property {assessment.property_id} not found")
        
        church = self.db.query(Church).filter(Church.id == property_obj.church_id).first()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        # Build content
        story = []
        
        # Cover page
        story.extend(self._create_cover_page(assessment, property_obj, church))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(assessment, property_obj))
        story.append(PageBreak())
        
        # Critical issues and deal breakers - MOST IMPORTANT PAGE
        story.extend(self._create_critical_issues(assessment, property_obj, church))
        story.append(PageBreak())
        
        # Financial projections - RIGHT AFTER CRITICAL ISSUES
        if include_detailed_analysis and assessment.financial_projections:
            story.extend(self._create_financial_projections(assessment))
            story.append(PageBreak())
        
        # Property overview
        story.extend(self._create_property_overview(property_obj))
        story.append(Spacer(1, 0.3*inch))
        
        # Assessment scores with visualization (on same page as property overview)
        # NO GAUGE CHART - Just show scores in table format
        story.extend(self._create_assessment_scores(assessment))
        story.append(PageBreak())
        
        # Market analysis
        if include_detailed_analysis and assessment.market_analysis:
            story.extend(self._create_market_analysis(assessment))
            story.append(PageBreak())
        
        # Natural disaster risk context - AFTER MARKET ANALYSIS
        story.extend(self._create_natural_disaster_context(assessment, property_obj))
        story.append(PageBreak())
        
        # Risk factors (combines with natural disaster for comprehensive risk view)
        if assessment.risk_factors:
            story.extend(self._create_risk_analysis(assessment))
            story.append(PageBreak())
        
        # REMOVED: ATTOM property valuation page (no longer needed)
        # Professional property data section removed per client request
        
        # Enrichment data summary
        story.extend(self._create_enrichment_summary(property_obj))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations(assessment, property_obj))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        
        logger.info(f"Generated PDF report for assessment {assessment_id}: {len(pdf_bytes)} bytes")
        
        return pdf_bytes
    
    def _create_cover_page(
        self,
        assessment: Assessment,
        property_obj: Property,
        church: Optional[Church]
    ) -> list:
        """Create report cover page"""
        story = []
        
        # Spacer
        story.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph(
            "Property Investment Assessment Report",
            self.styles['CustomTitle']
        )
        story.append(title)
        
        # Property name
        property_name = Paragraph(
            f"<b>{property_obj.name}</b>",
            self.styles['CustomSubtitle']
        )
        story.append(property_name)
        
        # Location
        location = Paragraph(
            f"{property_obj.city}, {property_obj.state} {property_obj.zip_code}",
            self.styles['Normal']
        )
        story.append(location)
        story.append(Spacer(1, 0.4*inch))
        
        # Grade display with proper spacing
        grade = self._calculate_grade(assessment.overall_score)
        grade_text = Paragraph(
            f"Investment Grade: <b>{grade}</b>",
            self.styles['GradeStyle']
        )
        story.append(grade_text)
        story.append(Spacer(1, 0.1*inch))
        
        score_text = Paragraph(
            f"Overall Score: {assessment.overall_score:.1f}/100",
            self.styles['ScoreStyle']
        )
        story.append(score_text)
        
        story.append(Spacer(1, 0.8*inch))
        
        # Church info
        if church:
            church_info = f"""
            <b>Property Owner:</b> {church.name}<br/>
            <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
            <b>Assessment ID:</b> {assessment.id}
            """
            story.append(Paragraph(church_info, self.styles['Normal']))
        
        return story
    
    def _create_executive_summary(
        self,
        assessment: Assessment,
        property_obj: Property
    ) -> list:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key metrics table
        grade = self._calculate_grade(assessment.overall_score)
        recommendation = self._get_recommendation_text(grade, assessment.overall_score)
        
        summary_data = [
            ['Property', property_obj.name],
            ['Location', f"{property_obj.city}, {property_obj.state}"],
            ['Property Type', property_obj.property_type.value if property_obj.property_type else 'N/A'],
            ['Lot Size', f"{property_obj.lot_size_acres:.2f} acres" if property_obj.lot_size_acres else 'N/A'],
            ['Investment Grade', f"{grade} ({assessment.overall_score:.1f}/100)"],
            ['Recommendation', recommendation],
            ['Assessment Date', assessment.processing_completed_at.strftime('%B %d, %Y') if assessment.processing_completed_at else 'In Progress']
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary text
        summary_text = f"""
        This property assessment evaluates the viability of developing affordable housing 
        at {property_obj.name} in {property_obj.city}, {property_obj.state}. The assessment 
        incorporates data from 7 government and public data sources including Census demographics, 
        HUD Fair Market Rent, FEMA flood risk, and local market conditions.
        """
        story.append(Paragraph(summary_text, self.styles['BodyText']))
        
        return story
    
    def _create_critical_issues(
        self,
        assessment: Assessment,
        property_obj: Property,
        church: Church
    ) -> list:
        """Create comprehensive grading analytics section"""
        story = []
        
        # Section header
        story.append(Paragraph("Grading Analytics & Assessment", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Determine severity level
        grade = self._calculate_grade(assessment.overall_score)
        score = assessment.overall_score
        
        # Status box - more accurate viability assessment
        if score >= 80:
            status_text = f"""
            <para align=center backColor=#e8f5e9 fontSize=14>
            <b>✓ PROJECT VIABILITY: RECOMMENDED</b><br/>
            <font size=12>Grade {grade} ({score:.1f}/100)</font>
            </para>
            """
        elif score >= 70:
            status_text = f"""
            <para align=center backColor=#fff9c4 fontSize=14>
            <b>⚠️ PROJECT VIABILITY: CONDITIONALLY APPROVED</b><br/>
            <font size=12>Grade {grade} ({score:.1f}/100) - Requires Risk Mitigation</font>
            </para>
            """
        elif score >= 60:
            status_text = f"""
            <para align=center backColor=#ffe0b2 fontSize=14>
            <b>⚠️ PROJECT VIABILITY: HIGH RISK</b><br/>
            <font size=12>Grade {grade} ({score:.1f}/100) - Significant Concerns</font>
            </para>
            """
        else:
            status_text = f"""
            <para align=center backColor=#ffebee fontSize=14>
            <b>❌ PROJECT VIABILITY: NOT RECOMMENDED</b><br/>
            <font size=12>Grade {grade} ({score:.1f}/100)</font>
            </para>
            """
        
        story.append(Paragraph(status_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # ========================================
        # COMPREHENSIVE GRADING ANALYTICS
        # ========================================
        
        story.append(Paragraph("<b>📊 COMPREHENSIVE GRADING BREAKDOWN</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.15*inch))
        
        # Score breakdown table
        score_data = [
            ['Category', 'Score', 'Grade', 'Weight', 'Status'],
            [
                'Financial Viability',
                f'{assessment.financial_score:.1f}/100',
                self._calculate_grade(assessment.financial_score),
                '30%',
                '✓ Pass' if assessment.financial_score >= 60 else '✗ Fail'
            ],
            [
                'Market Demand',
                f'{assessment.market_score:.1f}/100',
                self._calculate_grade(assessment.market_score),
                '25%',
                '✓ Pass' if assessment.market_score >= 60 else '✗ Fail'
            ],
            [
                'Location Quality',
                f'{assessment.location_score:.1f}/100',
                self._calculate_grade(assessment.location_score),
                '20%',
                '✓ Pass' if assessment.location_score >= 60 else '✗ Fail'
            ],
            [
                'Partnership Alignment',
                f'{assessment.partnership_score:.1f}/100',
                self._calculate_grade(assessment.partnership_score),
                '15%',
                '✓ Pass' if assessment.partnership_score >= 60 else '✗ Fail'
            ],
            [
                'Risk Assessment',
                f'{assessment.risk_score:.1f}/100',
                self._calculate_grade(assessment.risk_score),
                '10%',
                '✓ Pass' if assessment.risk_score >= 60 else '✗ Fail'
            ],
            [
                'OVERALL ASSESSMENT',
                f'{assessment.overall_score:.1f}/100',
                grade,
                '100%',
                '✓ APPROVED' if score >= 70 else '✗ NOT APPROVED'
            ]
        ]
        
        score_table = Table(score_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fafafa')]),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ========================================
        # RECOMMENDATION - Moved up for clarity
        # ========================================
        story.append(Paragraph("<b>🎯 RECOMMENDATION</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.15*inch))
        
        # Determine if there are deal breakers first
        has_deal_breakers = False
        if assessment.financial_projections:
            fin_proj = assessment.financial_projections
            unit_capacity = fin_proj.get('unit_capacity', {})
            feasible_units = unit_capacity.get('feasible_units', 0)
            if feasible_units < 40:
                has_deal_breakers = True
        
        # Show accurate recommendation based on deal breakers and score
        if has_deal_breakers:
            recommendation = f"""
            <para backColor=#ffebee leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10 fontSize=12>
            <b><font color=red>✗ NOT RECOMMENDED - CRITICAL DEAL BREAKER PRESENT</font></b><br/><br/>
            This property has a <b>critical deal breaker</b> that makes development financially unfeasible under 
            current conditions. The lot size is insufficient to meet Logos' minimum 40-unit requirement, which is 
            essential for achieving economies of scale and maintaining cost per unit below $325,000.<br/><br/>
            <b>Deal Breaker:</b> Only {fin_proj.get('unit_capacity', {}).get('feasible_units', 0)} units feasible (requires 40+ units minimum)<br/><br/>
            <b>Next Steps:</b> Acquire additional adjacent land, partner with neighboring property owner, or consider alternative site.
            </para>
            """
        elif score >= 80:
            recommendation = f"""
            <para backColor=#e8f5e9 leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10 fontSize=12>
            <b><font color=green>✓ STRONGLY RECOMMENDED FOR DEVELOPMENT</font></b><br/><br/>
            This property scores {score:.1f}/100 (Grade {grade}), placing it in the top tier of Logos development opportunities. 
            The financial projections are solid, market demand is strong, and partnership alignment is excellent. 
            Proceed with full due diligence and site planning.<br/><br/>
            <b>Next Steps:</b> Schedule site visit, commission environmental report, begin architectural planning.
            </para>
            """
        elif score >= 70:
            recommendation = f"""
            <para backColor=#fff9c4 leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10 fontSize=12>
            <b><font color=orange>⚠️ CONDITIONALLY APPROVED - ADDRESS KEY ISSUES</font></b><br/><br/>
            This property scores {score:.1f}/100 (Grade {grade}), meeting minimum viability standards but requiring 
            risk mitigation before final approval. Review the issues identified below and develop action plans 
            to address each concern.<br/><br/>
            <b>Next Steps:</b> Address flagged concerns, obtain additional data, reassess after mitigation.
            </para>
            """
        elif score >= 60:
            recommendation = f"""
            <para backColor=#ffe0b2 leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10 fontSize=12>
            <b><font color=orange>⚠️ HIGH RISK - SIGNIFICANT CONCERNS IDENTIFIED</font></b><br/><br/>
            This property scores {score:.1f}/100 (Grade {grade}), indicating significant challenges that make 
            development risky. Multiple concerns have been identified that could jeopardize project viability. 
            Careful review of all issues is required before proceeding.<br/><br/>
            <b>Next Steps:</b> Senior leadership review required. Consider alternative sites.
            </para>
            """
        else:
            recommendation = f"""
            <para backColor=#ffebee leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10 fontSize=12>
            <b><font color=red>✗ NOT RECOMMENDED - CRITICAL ISSUES PRESENT</font></b><br/><br/>
            This property scores {score:.1f}/100 (Grade {grade}), falling below minimum viability thresholds. 
            Critical issues have been identified that make this development financially or operationally unfeasible 
            under current conditions. Review deal-breakers below.<br/><br/>
            <b>Next Steps:</b> Explore site modifications or consider alternative properties.
            </para>
            """
        
        story.append(Paragraph(recommendation, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Key Data Points that drove the grade
        story.append(Paragraph("<b>📋 KEY DATA DRIVING THIS ASSESSMENT</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.15*inch))
        
        # Financial data
        if assessment.financial_projections:
            fin_proj = assessment.financial_projections
            unit_capacity = fin_proj.get('unit_capacity', {})
            feasible_units = unit_capacity.get('feasible_units', 0)
            cost_per_unit = fin_proj.get('adjusted_cost_per_unit', 0)
            
            revenue_proj = fin_proj.get('revenue_projections', {})
            annual_revenue = revenue_proj.get('total_annual_revenue', 0)
            noi = revenue_proj.get('net_operating_income', 0)
            roi = revenue_proj.get('roi_percent', 0)
            
            financial_text = f"""
            <para backColor=#e3f2fd leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <b>💰 FINANCIAL ANALYSIS ({assessment.financial_score:.1f}/100 - {self._calculate_grade(assessment.financial_score)})</b><br/>
            • Feasible Unit Count: <b>{feasible_units} units</b><br/>
            • Cost Per Unit: <b>${cost_per_unit:,.0f}</b> (Target: ≤$325,000)<br/>
            • Projected Annual Revenue: <b>${annual_revenue:,.0f}</b><br/>
            • Net Operating Income: <b>${noi:,.0f}</b><br/>
            • Return on Investment: <b>{roi:.1f}%</b><br/>
            • Target Range: 40-140 units (optimal economies of scale)<br/>
            {'• <font color=green><b>✓ MEETS MINIMUM VIABILITY</b></font>' if feasible_units >= 40 else '• <font color=red><b>✗ BELOW MINIMUM (40 units required)</b></font>'}
            </para>
            """
            story.append(Paragraph(financial_text, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Market data
        if assessment.market_analysis:
            market = assessment.market_analysis
            section8 = market.get('section8_viability', {})
            ami_data = market.get('ami_alignment', {})
            
            fmr_2br = section8.get('fmr_2bedroom', 0)
            ami_80_2p = ami_data.get('ami_80_percent_2person', 0)
            
            market_text = f"""
            <para backColor=#e8f5e9 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <b>📈 MARKET DEMAND ({assessment.market_score:.1f}/100 - {self._calculate_grade(assessment.market_score)})</b><br/>
            • Section 8 FMR (2BR): <b>${fmr_2br:,.0f}/month</b><br/>
            • 80% AMI (2-person): <b>${ami_80_2p:,.0f}/year</b><br/>
            • Local Housing Shortage: Severe (LA County)<br/>
            • Demographic Alignment: Strong affordable housing need<br/>
            • Voucher Availability: High demand in area<br/>
            {'• <font color=green><b>✓ STRONG MARKET INDICATORS</b></font>' if assessment.market_score >= 80 else '• <font color=orange><b>⚠ MODERATE MARKET</b></font>' if assessment.market_score >= 60 else '• <font color=red><b>✗ WEAK MARKET</b></font>'}
            </para>
            """
            story.append(Paragraph(market_text, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Location data
        location_text = f"""
        <para backColor=#fff9c4 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
        <b>📍 LOCATION QUALITY ({assessment.location_score:.1f}/100 - {self._calculate_grade(assessment.location_score)})</b><br/>
        • Property Address: {property_obj.full_address}<br/>
        • Lot Size: {f"{property_obj.lot_size_acres:.2f} acres ({property_obj.lot_size_sqft:,.0f} sq ft)" if property_obj.lot_size_acres and property_obj.lot_size_sqft else "Not specified"}<br/>
        • Zoning: {property_obj.zoning_description or (property_obj.zoning_classification.value if property_obj.zoning_classification else "Not specified")}<br/>
        • Transit Access: {"Excellent" if assessment.location_score >= 80 else "Good" if assessment.location_score >= 60 else "Limited"}<br/>
        • Neighborhood: {property_obj.city}, {property_obj.state}<br/>
        {'• <font color=green><b>✓ PRIME LOCATION</b></font>' if assessment.location_score >= 80 else '• <font color=orange><b>⚠ ACCEPTABLE LOCATION</b></font>' if assessment.location_score >= 60 else '• <font color=red><b>✗ LOCATION CONCERNS</b></font>'}
        </para>
        """
        story.append(Paragraph(location_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Risk data
        if assessment.risk_factors:
            risk_factors = assessment.risk_factors
            flood_analysis = risk_factors.get('flood_analysis', {})
            identified_risks = risk_factors.get('identified_risks', [])
            total_mitigation = risk_factors.get('total_mitigation_cost', 0)
            
            risk_text = f"""
            <para backColor=#ffebee leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <b>⚠️ RISK ASSESSMENT ({assessment.risk_score:.1f}/100 - {self._calculate_grade(assessment.risk_score)})</b><br/>
            • Flood Zone: {property_obj.flood_zone or "Zone X (minimal risk)"}<br/>
            • Identified Risks: {len(identified_risks)} items requiring attention<br/>
            • Total Mitigation Cost: ${total_mitigation:,.0f}<br/>
            • Natural Disasters: {"See detailed analysis below" if identified_risks else "Low risk profile"}<br/>
            {'• <font color=green><b>✓ LOW RISK PROFILE</b></font>' if assessment.risk_score >= 80 else '• <font color=orange><b>⚠ MODERATE RISKS</b></font>' if assessment.risk_score >= 60 else '• <font color=red><b>✗ HIGH RISK CONCERNS</b></font>'}
            </para>
            """
            story.append(Paragraph(risk_text, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Partnership data
        congregation_display = f"{church.congregation_size:,} members" if church.congregation_size else "Not specified"
        partnership_text = f"""
        <para backColor=#f3e5f5 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
        <b>🤝 PARTNERSHIP ALIGNMENT ({assessment.partnership_score:.1f}/100 - {self._calculate_grade(assessment.partnership_score)})</b><br/>
        • Church: {church.name}<br/>
        • Congregation Size: {congregation_display}<br/>
        • Community Support: {assessment.leadership_support or "To be determined"}<br/>
        • Timeline: {assessment.timeline_readiness or "Flexible"}<br/>
        • Development Experience: {"Yes" if church.previous_development_experience else "No (Logos provides expertise)"}<br/>
        {'• <font color=green><b>✓ STRONG PARTNERSHIP</b></font>' if assessment.partnership_score >= 80 else '• <font color=orange><b>⚠ ACCEPTABLE PARTNERSHIP</b></font>' if assessment.partnership_score >= 60 else '• <font color=red><b>✗ PARTNERSHIP CONCERNS</b></font>'}
        </para>
        """
        story.append(Paragraph(partnership_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Now show specific issues/concerns
        story.append(Paragraph("<b>🔍 DETAILED ISSUES & ACTION ITEMS</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.15*inch))
        
        # Collect issues
        deal_breakers = []
        major_concerns = []
        moderate_issues = []
        
        # Check lot size (CRITICAL) - COMPREHENSIVE ANALYSIS
        if assessment.financial_projections:
            fin_proj = assessment.financial_projections
            unit_capacity = fin_proj.get('unit_capacity', {})
            feasible_units = unit_capacity.get('feasible_units', 0)
            
            # Get lot size details
            using_available_space = fin_proj.get('using_available_space', False)
            available_build_sqft = fin_proj.get('available_build_sqft', 0)
            total_lot_sqft = fin_proj.get('total_lot_size_sqft', 0)
            lot_size_acres = fin_proj.get('lot_size_acres', 0)
            
            # Calculate what's needed
            units_per_acre = unit_capacity.get('units_per_acre_assumed', 45)
            site_coverage = unit_capacity.get('site_coverage_factor', 0.85)
            
            # Minimum required acreage for 40 units
            min_required_acres = 40 / (units_per_acre * site_coverage)
            min_required_sqft = min_required_acres * 43560
            
            if feasible_units < 40:
                # Calculate shortfall
                shortfall_units = 40 - feasible_units
                shortfall_pct = (shortfall_units / 40) * 100
                
                # Calculate additional land needed
                additional_acres_needed = min_required_acres - lot_size_acres
                additional_sqft_needed = additional_acres_needed * 43560
                
                # Estimated cost
                cost_per_acre_estimate = 500000  # Typical LA County land cost
                estimated_acquisition_cost = additional_acres_needed * cost_per_acre_estimate
                
                deal_breakers.append({
                    'title': 'LOT SIZE INSUFFICIENT FOR MINIMUM UNIT COUNT',
                    'details': f"""
                    <b>CURRENT PROPERTY ANALYSIS:</b><br/>
                    {'• Available Build Area: ' + f'{available_build_sqft:,} sq ft ({available_build_sqft/43560:.2f} acres)' + '<br/>' if using_available_space else ''}
                    {'• Total Property Size: ' + f'{total_lot_sqft:,} sq ft ({total_lot_sqft/43560:.2f} acres)' + '<br/>' if using_available_space else ''}
                    {'' if using_available_space else '• Property Size: ' + f'{total_lot_sqft:,} sq ft ({lot_size_acres:.2f} acres)' + '<br/>'}
                    • Feasible Unit Capacity: <b>{feasible_units} units</b><br/>
                    • Developable Area: {lot_size_acres * site_coverage:.2f} acres (after {int((1-site_coverage)*100)}% setbacks)<br/>
                    • Density: {units_per_acre} units/acre (typical for affordable housing)<br/>
                    <br/>
                    <b>LOGOS MODEL REQUIREMENTS:</b><br/>
                    • Minimum Viable Units: <b>40 units</b><br/>
                    • Target Range: 40-140 units (optimal economies of scale)<br/>
                    • Current Shortfall: <b>{shortfall_units} units ({shortfall_pct:.0f}% below minimum)</b><br/>
                    <br/>
                    <b>MINIMUM LOT SIZE NEEDED:</b><br/>
                    • Required: <b>{min_required_acres:.2f} acres ({min_required_sqft:,.0f} sq ft)</b><br/>
                    • Additional Land Needed: <b>{additional_acres_needed:.2f} acres ({additional_sqft_needed:,.0f} sq ft)</b><br/>
                    • Estimated Acquisition Cost: <b>${estimated_acquisition_cost:,.0f}</b><br/>
                    <br/>
                    <b>FINANCIAL IMPACT:</b><br/>
                    • At {feasible_units} units, cost per unit exceeds <b>$400,000</b><br/>
                    • Target cost per unit: <b>$325,000</b> (requires 40+ units)<br/>
                    • Project is NOT financially viable at current site size<br/>
                    <br/>
                    <b>RECOMMENDED SOLUTIONS:</b><br/>
                    1. <b>Acquire adjacent land</b> to reach {min_required_acres:.1f}+ acres<br/>
                    2. <b>Partner with neighboring property owner</b> for joint development<br/>
                    3. <b>Consider alternative site</b> that meets 40-unit minimum<br/>
                    <br/>
                    <b>⚠️ VERDICT:</b> This is a <u>DEAL BREAKER</u> unless additional land is secured.
                    """
                })
        
        # Check flood zone (MODERATE PRIORITY - only if V zone or multiple A zone flags)
        if property_obj.flood_zone:
            if property_obj.flood_zone.startswith('V'):  # Coastal high hazard only
                major_concerns.append({
                    'title': 'COASTAL HIGH HAZARD FLOOD ZONE',
                    'details': f"""
                    FEMA Flood Zone: {property_obj.flood_zone}<br/>
                    Risk Level: HIGH - Coastal wave action zone<br/>
                    Location: Special Flood Hazard Area (SFHA)<br/>
                    <br/>
                    <b>Requirements:</b><br/>
                    • Mandatory flood insurance ($5K-$10K per unit annually)<br/>
                    • Must elevate on pilings/columns (+$50K-$75K per unit)<br/>
                    • Lender requires detailed coastal engineering review<br/>
                    <br/>
                    <b>Action:</b> This may be a deal-breaker - consult structural engineer
                    """
                })
            elif property_obj.flood_zone in ['A', 'AE', 'AH', 'AO']:
                # Zone A is moderate risk, not critical - don't add to major concerns
                # Will be shown in Natural Disaster Risk section instead
                pass
        
        # Check zoning (HIGH PRIORITY)
        if property_obj.zoning_classification.value == 'UNKNOWN':
            major_concerns.append({
                'title': 'ZONING CLASSIFICATION UNVERIFIED',
                'details': f"""
                    Claimed Zoning: {property_obj.zoning_description or 'Not specified'}<br/>
                    Official Status: UNVERIFIED<br/>
                    <br/>
                    <b>Risks:</b><br/>
                    • Claimed zoning may not allow 40+ unit development<br/>
                    • Parking requirements unknown<br/>
                    • Height/density restrictions unknown<br/>
                    • Affordable housing density bonus eligibility unclear<br/>
                    <br/>
                    <b>Action:</b> Request official zoning letter from city planning department<br/>
                    Cost: $500-$1,500 | Timeline: 2-4 weeks
                    """
            })
        
        # NOTE: Church development experience is NOT an issue in Logos model
        # Church provides land + support, Logos brings ALL development expertise
        # This is actually the IDEAL scenario (commented out the warning)
        #
        # if not church.previous_development_experience:
        #     moderate_issues.append({
        #         'title': 'FIRST-TIME DEVELOPER - PARTNER REQUIRED',
        #         'details': """..."""
        #     })
        
        # Check location/market scores
        if assessment.location_score < 40:
            moderate_issues.append({
                'title': 'LOCATION DATA INCOMPLETE',
                'details': f"""
                Location Score: {assessment.location_score:.1f}/100<br/>
                <br/>
                <b>Missing Data:</b> Walkability, transit access, amenities analysis<br/>
                <b>Impact:</b> Cannot fully assess neighborhood quality and tenant demand<br/>
                <b>Action:</b> Complete Google Places API enrichment before final decision
                """
            })
        
        # Check natural disaster risks - ONLY ACTUAL DEAL-BREAKERS HERE
        # (Full natural disaster context will be in separate section)
        if assessment.risk_factors:
            risk_factors = assessment.risk_factors
            flood_analysis = risk_factors.get('flood_analysis', {})
            disaster_breakdown = flood_analysis.get('disaster_breakdown', {})
            
            if disaster_breakdown:
                # NOTE: Flood risk already handled above (V zones only)
                # Fire and earthquake shown here ONLY if truly concerning
                
                fire_risk = disaster_breakdown.get('fire', {})
                earthquake_risk = disaster_breakdown.get('earthquake', {})
                
                # Wildfire risk - ONLY if truly high risk (>10 events or very high risk level)
                nearby_count = fire_risk.get('event_count_nearby', 0)
                if nearby_count >= 10 or fire_risk.get('risk_level') == 'very_high':
                    mitigation_cost = fire_risk.get('mitigation_cost_per_unit', 0)
                    major_concerns.append({
                        'title': f'SEVERE WILDFIRE RISK - {nearby_count} NEARBY EVENTS',
                        'details': f"""
                        Nearby Wildfire Events: {nearby_count} within county since 2004<br/>
                        Risk Level: VERY HIGH<br/>
                        Estimated Mitigation Cost: ${mitigation_cost:,} per unit<br/>
                        <br/>
                        <b>Requirements:</b><br/>
                        • Fire-resistant construction materials (Class A roof, non-combustible siding)<br/>
                        • Defensible space perimeters (100ft minimum clearance)<br/>
                        • Higher insurance premiums (+$500-$1,000/unit/year)<br/>
                        • May require wildfire sprinkler systems<br/>
                        <br/>
                        <b>Action:</b> Consult fire marshal - this may impact insurance availability
                        """
                    })
                
                # Earthquake risk - ONLY if multiple recent events
                event_count = earthquake_risk.get('event_count', 0)
                if event_count >= 3:
                    mitigation_cost = earthquake_risk.get('mitigation_cost_per_unit', 0)
                    major_concerns.append({
                        'title': f'SIGNIFICANT SEISMIC ACTIVITY - {event_count} EVENTS',
                        'details': f"""
                        Historical Earthquake Events: {event_count} declarations since 2004<br/>
                        Estimated Mitigation Cost: ${mitigation_cost:,} per unit<br/>
                        <br/>
                        <b>Requirements:</b><br/>
                        • Enhanced seismic design per California Building Code<br/>
                        • Foundation reinforcement and lateral bracing<br/>
                        • Earthquake insurance required<br/>
                        <br/>
                        <b>Action:</b> Soil testing and structural engineering assessment required
                        """
                    })
        
        # Render issues
        if deal_breakers:
            story.append(Paragraph("<b>🚨 DEAL BREAKERS (Must Be Resolved)</b>", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            for issue in deal_breakers:
                issue_text = f"""
                <para backColor=#ffebee leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
                <font color=#c62828><b>❌ {issue['title']}</b></font><br/>
                {issue['details']}
                </para>
                """
                story.append(Paragraph(issue_text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        if major_concerns:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("<b>⚠️ MAJOR CONCERNS (Require Immediate Attention)</b>", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            for issue in major_concerns:
                issue_text = f"""
                <para backColor=#fff3e0 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
                <font color=#e65100><b>⚠️ {issue['title']}</b></font><br/>
                {issue['details']}
                </para>
                """
                story.append(Paragraph(issue_text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        if moderate_issues:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("<b>📋 MODERATE ISSUES (Recommended Actions)</b>", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            for issue in moderate_issues:
                issue_text = f"""
                <para backColor=#e3f2fd leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
                <font color=#1565c0><b>📋 {issue['title']}</b></font><br/>
                {issue['details']}
                </para>
                """
                story.append(Paragraph(issue_text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # If no issues found
        if not deal_breakers and not major_concerns and not moderate_issues:
            story.append(Paragraph("""
            <para backColor=#e8f5e9 leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10>
            <b>✓ No Critical Issues Identified</b><br/>
            This property has passed initial screening criteria. Proceed with detailed due diligence.
            </para>
            """, self.styles['Normal']))
        
        return story
    
    def _create_natural_disaster_context(
        self,
        assessment: Assessment,
        property_obj: Property
    ) -> list:
        """
        Create concise, actionable Natural Disaster Risk section
        
        Shows only KEY risks (Flood, Fire, Tornado, Hurricane) with clear risk levels
        and actionable mitigation costs. No excessive event listings.
        """
        story = []
        
        # Section header
        story.append(Paragraph("Natural Disaster Risk Assessment", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Check if we have disaster data
        if not assessment.risk_factors:
            story.append(Paragraph("No natural disaster data available.", self.styles['BodyText']))
            return story
        
        risk_factors = assessment.risk_factors
        flood_analysis = risk_factors.get('flood_analysis', {})
        disaster_breakdown = flood_analysis.get('disaster_breakdown', {})
        
        if not disaster_breakdown:
            story.append(Paragraph("No natural disaster data available.", self.styles['BodyText']))
            return story
        
        # Summary box - show overall risk and total mitigation cost
        # FILTER OUT IRRELEVANT RISKS based on geography
        total_mitigation = 0
        high_risk_count = 0
        
        # Determine which disasters are relevant based on state/region
        state = property_obj.state.upper() if property_obj.state else ''
        county = property_obj.county.upper() if property_obj.county else ''
        
        # Define relevant disasters by region
        relevant_disasters = []
        if state == 'CA':
            # California: Fire and Earthquake are primary concerns
            # Floods only if in actual flood zone
            relevant_disasters = ['fire', 'earthquake']
            if property_obj.flood_zone and property_obj.flood_zone not in ['X', 'C']:
                relevant_disasters.append('flood')
        elif state in ['FL', 'LA', 'TX', 'NC', 'SC', 'GA', 'AL', 'MS']:
            # Gulf/Atlantic coast: Hurricane, Flood, Tornado
            relevant_disasters = ['hurricane', 'flood', 'tornado']
        elif state in ['OK', 'KS', 'NE', 'MO', 'AR', 'IA']:
            # Tornado Alley: Tornado primary, Flood secondary
            relevant_disasters = ['tornado', 'flood']
        else:
            # Other states: Flood most common, check for others
            relevant_disasters = ['flood', 'tornado']
        
        # Only count relevant disasters
        for disaster_type in relevant_disasters:
            if disaster_type in disaster_breakdown:
                data = disaster_breakdown[disaster_type]
                risk_level = data.get('risk_level', 'unknown')
                if risk_level in ['high', 'very_high']:
                    high_risk_count += 1
                mitigation = data.get('mitigation_cost_per_unit', 0)
                total_mitigation += mitigation
        
        # Overall risk assessment box
        if high_risk_count >= 2:
            bg_color = '#ffebee'
            risk_text = 'HIGH RISK - Multiple natural hazards present'
        elif high_risk_count == 1:
            bg_color = '#fff9c4'
            risk_text = 'MODERATE RISK - One significant natural hazard'
        else:
            bg_color = '#e8f5e9'
            risk_text = 'LOW RISK - Minimal natural hazard concerns'
        
        summary_box = f"""
        <para backColor={bg_color} leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10>
        <font size=11><b>{risk_text}</b></font><br/>
        <font size=9>
        Total Estimated Mitigation Cost: <b>${total_mitigation:,}/unit</b>
        {f" (${total_mitigation * 100:,} for 100-unit project)" if total_mitigation > 0 else ""}
        </font>
        </para>
        """
        story.append(Paragraph(summary_box, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key risks table - ONLY show RELEVANT disasters for this geography
        story.append(Paragraph("<b>Relevant Natural Disaster Risks for This Location</b>", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))
        
        # Add geographic context
        location_note = f"""
        <para fontSize=9 textColor=#666666>
        <i>Risk assessment filtered for {property_obj.city}, {state} region. 
        Only disasters with actual occurrence history in this area are shown.</i>
        </para>
        """
        story.append(Paragraph(location_note, self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        risk_data = [['Hazard Type', 'Risk Level', 'Historical Events', 'Mitigation Cost/Unit', 'Key Actions']]
        
        disaster_labels = {
            'flood': 'Flood',
            'fire': 'Wildfire',
            'tornado': 'Tornado',
            'hurricane': 'Hurricane',
            'earthquake': 'Earthquake'
        }
        
        # Only show RELEVANT disasters for this geography
        for disaster_type in relevant_disasters:
            if disaster_type in disaster_breakdown:
                data = disaster_breakdown[disaster_type]
                risk_level = data.get('risk_level', 'unknown').upper()
                event_count = data.get('event_count', 0)
                event_count_nearby = data.get('event_count_nearby', 0)
                
                # Show event count that's most relevant
                if disaster_type == 'fire' and event_count_nearby > 0:
                    events_display = f"{event_count_nearby} within county"
                elif event_count > 0:
                    events_display = f"{event_count} declarations"
                else:
                    events_display = "None recorded"
                
                # Only show if there's actual risk (not "none" or "minimal")
                if risk_level not in ['NONE', 'MINIMAL', 'UNKNOWN'] or event_count > 0 or event_count_nearby > 0:
                    mitigation_cost = data.get('mitigation_cost_per_unit', 0)
                    
                    # Get concise action
                    if disaster_type == 'flood':
                        if property_obj.flood_zone in ['A', 'AE']:
                            action = "Elevate 1-2ft, flood insurance"
                        elif property_obj.flood_zone in ['V', 'VE']:
                            action = "Elevate on pilings, coastal design"
                        else:
                            action = "Standard construction"
                    elif disaster_type == 'fire':
                        if event_count_nearby >= 10:
                            action = "Fire-resistant materials, defensible space"
                        else:
                            action = "Standard fire safety"
                    elif disaster_type == 'earthquake':
                        action = "Seismic-resistant design"
                    elif disaster_type == 'tornado':
                        action = "Reinforced structure, safe room"
                    elif disaster_type == 'hurricane':
                        action = "Wind-resistant design, storm shutters"
                    else:
                        action = "Standard mitigation"
                    
                    risk_data.append([
                        disaster_labels.get(disaster_type, disaster_type.title()),
                        risk_level,
                        events_display,
                        f"${mitigation_cost:,}" if mitigation_cost > 0 else "$0",
                        action
                    ])
        
        # Only show table if we have risks to display
        if len(risk_data) > 1:
            risk_table = Table(risk_data, colWidths=[1.1*inch, 0.9*inch, 1.1*inch, 1.1*inch, 1.8*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ]))
            
            story.append(risk_table)
        else:
            story.append(Paragraph("<i>No significant natural disaster risks identified for this location based on historical data.</i>", self.styles['BodyText']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Flood zone details (if applicable)
        if property_obj.flood_zone and property_obj.flood_zone not in ['X', 'C']:
            flood_box = f"""
            <para backColor=#e3f2fd leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10>
            <font color=#1565c0 size=10><b>FEMA Flood Zone: {property_obj.flood_zone}</b></font><br/>
            <font size=9>
            """
            
            if property_obj.flood_zone.startswith('V'):
                flood_box += """
                <b>Coastal High Hazard Zone</b> - Wave action expected during base flood<br/>
                • Requires construction on pilings/columns<br/>
                • Mandatory flood insurance required<br/>
                • Higher construction costs (+$75K/unit estimated)
                """
            elif property_obj.flood_zone in ['A', 'AE', 'AH', 'AO']:
                flood_box += """
                <b>Special Flood Hazard Area (SFHA)</b> - 1% annual flood chance<br/>
                • May require elevated construction (check local codes)<br/>
                • Flood insurance recommended/required by lenders<br/>
                • Moderate additional cost (+$50K/unit estimated)
                """
            
            flood_box += """
            </font>
            </para>
            """
            story.append(Paragraph(flood_box, self.styles['Normal']))
        
        # Bottom line recommendation
        story.append(Spacer(1, 0.15*inch))
        
        if total_mitigation == 0:
            recommendation = """
            <para backColor=#e8f5e9 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <font color=#2e7d32 size=10><b>✓ RECOMMENDATION:</b> No significant natural disaster mitigation costs required. 
            Standard construction practices are adequate for this location.</font>
            </para>
            """
        elif total_mitigation <= 50000:
            recommendation = f"""
            <para backColor=#fff9c4 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <font color=#f57f17 size=10><b>⚠️ RECOMMENDATION:</b> Moderate mitigation costs (${total_mitigation:,}/unit). 
            Include in development pro forma and verify with local contractors. Project remains viable with proper budgeting.</font>
            </para>
            """
        else:
            recommendation = f"""
            <para backColor=#ffebee leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <font color=#c62828 size=10><b>⚠️ RECOMMENDATION:</b> High mitigation costs (${total_mitigation:,}/unit). 
            Conduct detailed feasibility study. May require land price reduction or alternative sites.</font>
            </para>
            """
        
        story.append(Paragraph(recommendation, self.styles['Normal']))
        
        return story
    
    def _create_property_overview(self, property_obj: Property) -> list:
        """Create property details section"""
        story = []
        
        story.append(Paragraph("Property Overview", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Property details table
        details_data = [
            ['Street Address', property_obj.street_address or 'N/A'],
            ['City, State, ZIP', f"{property_obj.city}, {property_obj.state} {property_obj.zip_code}"],
            ['County', property_obj.county or 'N/A'],
            ['Coordinates', f"{property_obj.latitude:.6f}, {property_obj.longitude:.6f}" if property_obj.latitude else 'N/A'],
            ['Lot Size (sq ft)', f"{property_obj.lot_size_sqft:,}" if property_obj.lot_size_sqft else 'N/A'],
            ['Lot Size (acres)', f"{property_obj.lot_size_acres:.2f}" if property_obj.lot_size_acres else 'N/A'],
            ['Zoning', f"{property_obj.zoning_classification}: {property_obj.zoning_description}" if property_obj.zoning_classification else 'N/A'],
            ['Current Usage', property_obj.current_usage or 'N/A'],
            ['Assessed Value', f"${property_obj.assessed_value:,}" if property_obj.assessed_value else 'N/A'],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(details_table)
        
        return story
    
    def _create_assessment_scores(self, assessment: Assessment) -> list:
        """Create assessment scores section with gauge chart"""
        story = []
        
        story.append(Paragraph("Assessment Scores", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Score breakdown table
        scores_data = [
            ['Category', 'Score', 'Weight', 'Weighted Score'],
            ['Location Viability', f"{assessment.location_score:.1f}/100", '25%', f"{assessment.location_score * 0.25:.1f}"],
            ['Market Demand', f"{assessment.market_score:.1f}/100", '25%', f"{assessment.market_score * 0.25:.1f}"],
            ['Financial Feasibility', f"{assessment.financial_score:.1f}/100", '20%', f"{assessment.financial_score * 0.20:.1f}"],
            ['Partnership Strength', f"{assessment.partnership_score:.1f}/100", '15%', f"{assessment.partnership_score * 0.15:.1f}"],
            ['Risk Assessment', f"{assessment.risk_score:.1f}/100", '15%', f"{assessment.risk_score * 0.15:.1f}"],
            ['', '', '<b>Overall Score</b>', f"<b>{assessment.overall_score:.1f}/100</b>"]
        ]
        
        scores_table = Table(scores_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e6f2ff')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2c5aa0')),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ]))
        
        story.append(scores_table)
        
        # NO GAUGE CHART - Removed per client request
        
        return story
    
    def _create_gauge_chart(self, score: float) -> Optional[Image]:
        """Create a gauge chart showing overall score"""
        try:
            fig, ax = plt.subplots(figsize=(6, 3), subplot_kw={'aspect': 'equal'})
            
            # Define score ranges and colors
            ranges = [
                (0, 30, '#d32f2f'),    # F: Red
                (30, 50, '#f57c00'),   # D: Orange
                (50, 70, '#fbc02d'),   # C: Yellow
                (70, 87, '#7cb342'),   # B: Light Green
                (87, 100, '#388e3c'),  # A: Dark Green
            ]
            
            # Draw gauge segments
            start_angle = 180
            for range_start, range_end, color in ranges:
                extent = (range_end - range_start) / 100 * 180
                wedge = Wedge((0.5, 0), 0.4, start_angle, start_angle + extent,
                            width=0.15, facecolor=color, edgecolor='white', linewidth=2)
                ax.add_patch(wedge)
                start_angle += extent
            
            # Draw needle
            angle = 180 - (score / 100 * 180)
            angle_rad = np.radians(angle)
            needle_length = 0.35
            needle_x = 0.5 + needle_length * np.cos(angle_rad)
            needle_y = needle_length * np.sin(angle_rad)
            ax.plot([0.5, needle_x], [0, needle_y], 'k-', linewidth=3)
            ax.plot(0.5, 0, 'ko', markersize=10)
            
            # Add score text
            grade = self._calculate_grade(score)
            ax.text(0.5, -0.15, f"{score:.1f}", ha='center', va='center',
                   fontsize=24, fontweight='bold')
            ax.text(0.5, -0.25, f"Grade: {grade}", ha='center', va='center',
                   fontsize=16, color='#666666')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(-0.3, 0.5)
            ax.axis('off')
            
            # Save to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', transparent=True)
            img_buffer.seek(0)
            plt.close()
            
            # Create ReportLab Image
            img = Image(img_buffer, width=4*inch, height=2*inch)
            return img
            
        except Exception as e:
            logger.error(f"Error creating gauge chart: {e}")
            return None
    
    def _create_market_analysis(self, assessment: Assessment) -> list:
        """Create market analysis section"""
        story = []
        
        story.append(Paragraph("Market Analysis", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        if assessment.market_analysis:
            market_data = assessment.market_analysis
            
            # Market score
            score_text = f"<b>Market Score:</b> {market_data.get('score', 0):.1f}/100"
            story.append(Paragraph(score_text, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Analysis text
            analysis = market_data.get('analysis', 'No analysis available')
            
            # Check if analysis appears truncated (ends abruptly without punctuation)
            if analysis and not analysis.rstrip().endswith(('.', '!', '?', '"', "'")):
                warning = '<i><font color="orange">⚠️ Note: Market analysis may be incomplete due to AI response limits.</font></i>'
                story.append(Paragraph(warning, self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            # Split into paragraphs
            paragraphs = analysis.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['BodyText']))
                    story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No market analysis data available.", self.styles['BodyText']))
        
        return story
    
    def _create_financial_projections(self, assessment: Assessment) -> list:
        """Create financial projections section"""
        story = []
        
        story.append(Paragraph("Financial Projections", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        if assessment.financial_projections:
            proj = assessment.financial_projections
            
            # Extract revenue projections (nested structure)
            revenue_proj = proj.get('revenue_projections', {})
            
            # Get feasible units
            feasible_units = proj.get('feasible_units', 0)
            
            # Get values with multiple possible field names (handle different JSON structures)
            # Handle both numeric and string formats
            annual_revenue_raw = revenue_proj.get('total_annual_revenue', 0)
            if isinstance(annual_revenue_raw, str):
                annual_revenue = float(annual_revenue_raw.replace('$', '').replace(',', ''))
            else:
                annual_revenue = annual_revenue_raw or 0
            
            operating_expenses_raw = revenue_proj.get('operating_expenses', 0)
            if isinstance(operating_expenses_raw, str):
                operating_expenses = float(operating_expenses_raw.replace('$', '').replace(',', ''))
            else:
                operating_expenses = operating_expenses_raw or 0
            
            noi_raw = revenue_proj.get('net_operating_income', 0)
            if isinstance(noi_raw, str):
                noi = float(noi_raw.replace('$', '').replace(',', ''))
            else:
                noi = noi_raw or 0
            
            # Development costs
            total_dev_cost_raw = proj.get('adjusted_development_cost') or proj.get('base_development_cost', 0)
            if isinstance(total_dev_cost_raw, str):
                total_dev_cost = float(total_dev_cost_raw.replace('$', '').replace(',', ''))
            else:
                total_dev_cost = total_dev_cost_raw or 0
                
            cost_per_unit = proj.get('adjusted_cost_per_unit') or proj.get('base_cost_per_unit', 0)
            
            # Financial metrics
            roi = revenue_proj.get('roi_percent', 0)
            cap_rate = revenue_proj.get('cap_rate', 0)
            cash_on_cash = revenue_proj.get('cash_on_cash_return', 0)
            
            # Build space info
            using_available_space = proj.get('using_available_space', False)
            available_build_sqft = proj.get('available_build_sqft', 0)
            total_lot_sqft = proj.get('total_lot_size_sqft', 0)
            
            # Add context if using available build space
            if using_available_space and available_build_sqft:
                space_context = f"""
                <para backColor=#fff9c4 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=10>
                <font color=#f57f17 size=9><b>Note:</b> Financial projections based on client-specified 
                available build space of {available_build_sqft:,} sq ft (total lot: {total_lot_sqft:,} sq ft)</font>
                </para>
                """
                story.append(Paragraph(space_context, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            # Financial metrics table
            metrics_data = [
                ['Metric', 'Value'],
                ['Feasible Units', f"{feasible_units} units" if feasible_units else "N/A"],
                ['Annual Revenue', f"${annual_revenue:,.0f}" if annual_revenue else "N/A"],
                ['Operating Expenses (42%)', f"${operating_expenses:,.0f}" if operating_expenses else "N/A"],
                ['Net Operating Income (NOI)', f"${noi:,.0f}" if noi else "N/A"],
                ['Total Development Cost', f"${total_dev_cost:,.0f}" if total_dev_cost else "N/A"],
                ['Cost Per Unit', f"${cost_per_unit:,.0f}" if cost_per_unit else "N/A"],
                ['Return on Investment (ROI)', f"{roi:.2f}%" if roi else "N/A"],
                ['Cap Rate', f"{cap_rate:.2f}%" if cap_rate else "N/A"],
                ['Cash-on-Cash Return', f"{cash_on_cash:.2f}%" if cash_on_cash else "N/A"],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3.5*inch, 2.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))
            
            story.append(metrics_table)
            
            # Add assumptions
            story.append(Spacer(1, 0.2*inch))
            assumptions_text = """
            <para fontSize=9 textColor=#666666>
            <b>Assumptions:</b> 20% 1BR, 60% 2BR, 20% 3BR unit mix  • 42% operating expense ratio •
            100% occupancy (Section 8) • 30% equity / 70% debt financing • Does not include debt service payments
            </para>
            """
            story.append(Paragraph(assumptions_text, self.styles['Normal']))
        
        else:
            story.append(Paragraph(
                "<i>Financial projections data not available for this assessment.</i>",
                self.styles['BodyText']
            ))
        
        return story
    
    def _create_risk_analysis(self, assessment: Assessment) -> list:
        """Create risk analysis section"""
        story = []
        
        story.append(Paragraph("Risk Analysis", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        if assessment.risk_factors:
            risk_data = assessment.risk_factors
            
            # Risk Level Summary
            risk_level = risk_data.get('risk_level', 'Unknown').upper()
            risk_score = risk_data.get('score', 0)
            
            risk_summary = f"<b>Overall Risk Level:</b> {risk_level} (Score: {risk_score}/100)"
            story.append(Paragraph(risk_summary, self.styles['BodyText']))
            story.append(Spacer(1, 0.15*inch))
            
            # Identified Risks
            identified_risks = risk_data.get('identified_risks', [])
            if identified_risks:
                story.append(Paragraph("<b>Identified Risks:</b>", self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
                
                for risk in identified_risks:
                    bullet = f"• {risk}"
                    story.append(Paragraph(bullet, self.styles['BodyText']))
                    story.append(Spacer(1, 0.05*inch))
                
                story.append(Spacer(1, 0.1*inch))
            
            # Mitigation Strategies
            mitigation_strategies = risk_data.get('mitigation_strategies', [])
            if mitigation_strategies:
                story.append(Paragraph("<b>Recommended Mitigation Strategies:</b>", self.styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
                
                for strategy in mitigation_strategies:
                    bullet = f"• {strategy}"
                    story.append(Paragraph(bullet, self.styles['BodyText']))
                    story.append(Spacer(1, 0.05*inch))
            
            # Comprehensive Natural Disaster Risk Analysis
            flood_analysis = risk_data.get('flood_analysis', {})
            if flood_analysis:
                disaster_breakdown = flood_analysis.get('disaster_breakdown', {})
                
                if disaster_breakdown:
                    story.append(Spacer(1, 0.2*inch))
                    story.append(Paragraph("<b>Natural Disaster Risk Assessment:</b>", self.styles['Heading3']))
                    story.append(Spacer(1, 0.1*inch))
                    
                    total_mitigation = flood_analysis.get('mitigation_cost_per_unit', 0)
                    if total_mitigation > 0:
                        story.append(Paragraph(
                            f"<b>Total Mitigation Cost:</b> ${total_mitigation:,} per unit",
                            self.styles['BodyText']
                        ))
                        story.append(Spacer(1, 0.1*inch))
                    
                    # Create table for disaster risks
                    disaster_data = [['Disaster Type', 'Risk Level', 'Events (2004-present)', 'Mitigation Cost/Unit']]
                    
                    disaster_labels = {
                        'flood': 'Flood',
                        'fire': 'Wildfire',
                        'tornado': 'Tornado',
                        'hurricane': 'Hurricane',
                        'earthquake': 'Earthquake'
                    }
                    
                    for disaster_type, label in disaster_labels.items():
                        if disaster_type in disaster_breakdown:
                            data = disaster_breakdown[disaster_type]
                            risk_level = data.get('risk_level', 'unknown').upper()
                            event_count = data.get('event_count', 0)
                            mitigation_cost = data.get('mitigation_cost_per_unit', 0)
                            
                            disaster_data.append([
                                label,
                                risk_level,
                                str(event_count),
                                f"${mitigation_cost:,}"
                            ])
                    
                    disaster_table = Table(disaster_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.5*inch])
                    disaster_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    
                    story.append(disaster_table)
                    story.append(Spacer(1, 0.15*inch))
                    
                    # Show key risks for high-risk disasters
                    for disaster_type, label in disaster_labels.items():
                        if disaster_type in disaster_breakdown:
                            data = disaster_breakdown[disaster_type]
                            if data.get('risk_level') in ['high', 'very_high', 'moderate']:
                                risks = data.get('risks', [])
                                if risks:
                                    story.append(Paragraph(f"<b>{label} Risks:</b>", self.styles['BodyText']))
                                    for risk in risks[:3]:  # Show top 3 risks
                                        story.append(Paragraph(f"  • {risk}", self.styles['Normal']))
                                        story.append(Spacer(1, 0.03*inch))
                                    story.append(Spacer(1, 0.1*inch))
                    
                    # Overall recommendation
                    recommendation = flood_analysis.get('recommendation', '')
                    if recommendation:
                        story.append(Spacer(1, 0.1*inch))
                        story.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", self.styles['BodyText']))
                else:
                    # Legacy flood-only display
                    story.append(Spacer(1, 0.1*inch))
                    flood_zone = flood_analysis.get('flood_zone', 'Unknown')
                    flood_risk = flood_analysis.get('risk_level', 'unknown')
                    story.append(Paragraph(
                        f"<b>Flood Risk:</b> {flood_risk.title()} (Zone: {flood_zone})",
                        self.styles['BodyText']
                    ))
            
            # Risk Analysis Text (if available)
            risk_text = risk_data.get('analysis', '')
            if risk_text:
                story.append(Spacer(1, 0.15*inch))
                story.append(Paragraph(risk_text, self.styles['BodyText']))
        else:
            story.append(Paragraph("No risk analysis data available.", self.styles['BodyText']))
        
        return story
    
    def _create_enrichment_summary(self, property_obj: Property) -> list:
        """Create enrichment data summary"""
        story = []
        
        story.append(Paragraph("Data Sources", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        intro = """
        This assessment incorporates data from multiple government and public sources 
        to provide accurate, data-driven analysis:
        """
        story.append(Paragraph(intro, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        sources = [
            "• <b>ATTOM Data Solutions</b> - Professional property valuations and comparables",
            "• <b>U.S. Census Bureau</b> - Demographics, income, poverty rates",
            "• <b>HUD Fair Market Rent</b> - Rental rate benchmarks",
            "• <b>HUD Income Limits</b> - Area Median Income (AMI) validation",
            "• <b>FEMA Flood Risk</b> - Flood zone determination",
            "• <b>HUD USPS Crosswalk</b> - Census tract mapping",
            "• <b>Geocoding Services</b> - Location validation",
            "• <b>OpenAI GPT-4o-mini</b> - Market analysis and insights"
        ]
        
        for source in sources:
            story.append(Paragraph(source, self.styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
        
        return story
    
    def _create_recommendations(self, assessment: Assessment, property_obj: Property) -> list:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        grade = self._calculate_grade(assessment.overall_score)
        
        # Generate recommendations based on grade
        if grade in ['A', 'A+']:
            rec_text = """
            <b>PROCEED WITH DEVELOPMENT</b><br/><br/>
            This property demonstrates strong viability for affordable housing development. 
            The location, market conditions, and financial projections all support moving 
            forward with planning and development.
            """
        elif grade.startswith('B'):
            rec_text = """
            <b>CONDITIONALLY RECOMMENDED</b><br/><br/>
            This property shows good potential for affordable housing development with some 
            considerations. Review the risk factors and market analysis carefully before proceeding.
            """
        elif grade.startswith('C'):
            rec_text = """
            <b>REQUIRES IMPROVEMENTS</b><br/><br/>
            This property has moderate potential but requires significant improvements or 
            adjustments to be viable. Consider addressing the identified challenges before 
            committing resources.
            """
        elif grade == 'D':
            rec_text = """
            <b>NOT RECOMMENDED - SIGNIFICANT CHALLENGES</b><br/><br/>
            This property faces significant challenges for affordable housing development. 
            The low score indicates fundamental issues that may make development unfeasible 
            or financially risky.
            """
        else:  # F
            rec_text = """
            <b>DO NOT PROCEED</b><br/><br/>
            This property is not suitable for affordable housing development based on current 
            assessment. Consider alternative properties or significant changes to the development plan.
            """
        
        story.append(Paragraph(rec_text, self.styles['BodyText']))
        
        return story
    
    def _calculate_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 97:
            return 'A+'
        elif score >= 93:
            return 'A'
        elif score >= 90:
            return 'A-'
        elif score >= 87:
            return 'B+'
        elif score >= 83:
            return 'B'
        elif score >= 80:
            return 'B-'
        elif score >= 77:
            return 'C+'
        elif score >= 73:
            return 'C'
        elif score >= 70:
            return 'C-'
        elif score >= 67:
            return 'D+'
        elif score >= 63:
            return 'D'
        elif score >= 60:
            return 'D-'
        else:
            return 'F'
    
    def _get_recommendation_text(self, grade: str, score: float) -> str:
        """Get recommendation text based on grade"""
        if grade in ['A+', 'A', 'A-']:
            return 'Strong Buy'
        elif grade in ['B+', 'B', 'B-']:
            return 'Buy with Conditions'
        elif grade in ['C+', 'C', 'C-']:
            return 'Hold - Requires Improvement'
        elif grade in ['D+', 'D', 'D-']:
            return 'Avoid - Significant Issues'
        else:
            return 'Reject - Not Viable'
    
    def _create_attom_data_sections(self, property_obj: Property) -> list:
        """
        Create ATTOM professional property data sections
        
        Includes:
        - Property Valuation (AVM estimates)
        - Sales Comparables (recent nearby sales)
        - Verified Property Characteristics
        """
        story = []
        
        # Check if we have ATTOM data
        if not property_obj.data_sources:
            return []
        
        try:
            import json
            data_sources = json.loads(property_obj.data_sources) if isinstance(property_obj.data_sources, str) else property_obj.data_sources
            attom_data = data_sources.get('attom_data', {})
            
            if not attom_data or attom_data.get('status') != 'success':
                return []
            
            attom_results = attom_data.get('data', {})
            
            # Section header
            story.append(Paragraph("Professional Property Data (ATTOM)", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.1*inch))
            
            disclaimer = """
            <para backColor=#e8f5e9 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <font color=#2e7d32 size=9><b>✓ PROFESSIONAL DATA SOURCE</b></font><br/>
            <font size=8>The following data is provided by ATTOM Data Solutions, a leading provider of 
            property data used by real estate professionals, lenders, and investors nationwide.</font>
            </para>
            """
            story.append(Paragraph(disclaimer, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # 1. PROPERTY VALUATION
            avm_data = attom_results.get('valuation', {})
            if avm_data and avm_data.get('success'):
                story.extend(self._create_attom_valuation_section(avm_data, property_obj))
                story.append(Spacer(1, 0.3*inch))
            
            # 2. SALES COMPARABLES
            comps_data = attom_results.get('comparables', {})
            if comps_data and comps_data.get('success'):
                story.extend(self._create_attom_comparables_section(comps_data))
                story.append(Spacer(1, 0.3*inch))
            
            # 3. PROPERTY CHARACTERISTICS
            detail_data = attom_results.get('property_detail', {})
            if detail_data and detail_data.get('success'):
                story.extend(self._create_attom_characteristics_section(detail_data))
            
            return story
            
        except Exception as e:
            logger.warning(f"Error creating ATTOM sections: {e}")
            return []
    
    def _create_attom_valuation_section(self, avm_data: Dict[str, Any], property_obj: Property) -> list:
        """Create ATTOM property valuation section"""
        story = []
        
        story.append(Paragraph("<b>Property Valuation Analysis</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        avm_info = avm_data.get('data', {})
        
        # Extract valuation data
        amount = avm_info.get('amount', {})
        value = amount.get('value', 0)
        value_high = amount.get('high', 0)
        value_low = amount.get('low', 0)
        
        fsd_score = avm_info.get('fsdScore', 0)  # Forecast Standard Deviation Score (confidence)
        
        # Valuation summary box
        valuation_box = f"""
        <para backColor=#e3f2fd leftIndent=10 rightIndent=10 spaceBefore=10 spaceAfter=10>
        <font size=11><b>ATTOM Automated Valuation Model (AVM)</b></font><br/>
        <font size=10>
        <b>Estimated Market Value: ${value:,}</b><br/>
        Value Range: ${value_low:,} - ${value_high:,}<br/>
        Confidence Score: {fsd_score:.1f}/100
        </font>
        </para>
        """
        story.append(Paragraph(valuation_box, self.styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Compare with assessed value
        if property_obj.assessed_value and property_obj.assessed_value > 0:
            assessed = property_obj.assessed_value
            diff = value - assessed
            diff_pct = (diff / assessed * 100) if assessed > 0 else 0
            
            if abs(diff_pct) <= 10:
                color = '#2e7d32'
                icon = '✓'
                assessment_text = 'aligns closely with'
            elif diff_pct > 10:
                color = '#1565c0'
                icon = '↑'
                assessment_text = 'is higher than'
            else:
                color = '#f57f17'
                icon = '↓'
                assessment_text = 'is lower than'
            
            comparison = f"""
            <para leftIndent=10>
            <font color={color} size=10><b>{icon} Market Analysis:</b></font><br/>
            <font size=9>
            ATTOM valuation ({assessment_text} county assessment by {abs(diff_pct):.1f}%)<br/>
            • County Assessed Value: ${assessed:,}<br/>
            • ATTOM Market Estimate: ${value:,}<br/>
            • Difference: ${abs(diff):,} ({'+' if diff > 0 else ''}{diff_pct:.1f}%)
            </font>
            </para>
            """
            story.append(Paragraph(comparison, self.styles['Normal']))
        
        return story
    
    def _create_attom_comparables_section(self, comps_data: Dict[str, Any]) -> list:
        """Create ATTOM sales comparables section"""
        story = []
        
        story.append(Paragraph("<b>Recent Sales Comparables</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        comps = comps_data.get('data', {}).get('properties', [])
        
        if not comps:
            story.append(Paragraph("<i>No recent comparable sales data available.</i>", self.styles['BodyText']))
            return story
        
        # Summary stats
        sale_prices = [p.get('sale', {}).get('amount', {}).get('saleamt', 0) for p in comps if p.get('sale', {}).get('amount', {}).get('saleamt')]
        
        if sale_prices:
            avg_price = sum(sale_prices) / len(sale_prices)
            median_price = sorted(sale_prices)[len(sale_prices) // 2]
            
            summary = f"""
            <para backColor=#f5f5f5 leftIndent=10 rightIndent=10 spaceBefore=6 spaceAfter=6>
            <font size=10><b>Comparable Sales Summary ({len(comps)} properties)</b></font><br/>
            <font size=9>
            Average Sale Price: ${avg_price:,.0f}<br/>
            Median Sale Price: ${median_price:,.0f}<br/>
            Range: ${min(sale_prices):,.0f} - ${max(sale_prices):,.0f}
            </font>
            </para>
            """
            story.append(Paragraph(summary, self.styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        # Comparables table (top 5)
        comp_data = [['Address', 'Sale Price', 'Sale Date', 'Distance']]
        
        for comp in comps[:5]:
            address_info = comp.get('address', {})
            sale_info = comp.get('sale', {})
            distance = comp.get('distance', 0)
            
            # Format address
            street = address_info.get('oneLine', 'N/A')
            
            # Format sale price
            sale_amt = sale_info.get('amount', {}).get('saleamt', 0)
            price_str = f"${sale_amt:,.0f}" if sale_amt > 0 else "N/A"
            
            # Format sale date
            sale_date_info = sale_info.get('saleTransDate', '')
            if sale_date_info:
                from datetime import datetime
                try:
                    date_obj = datetime.fromisoformat(sale_date_info.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%b %Y')
                except:
                    date_str = sale_date_info[:7] if len(sale_date_info) >= 7 else 'N/A'
            else:
                date_str = 'N/A'
            
            # Format distance
            dist_str = f"{distance:.1f} mi" if distance > 0 else "N/A"
            
            comp_data.append([
                street[:30] + '...' if len(street) > 30 else street,
                price_str,
                date_str,
                dist_str
            ])
        
        comp_table = Table(comp_data, colWidths=[2.5*inch, 1.2*inch, 1*inch, 0.8*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]))
        
        story.append(comp_table)
        
        return story
    
    def _create_attom_characteristics_section(self, detail_data: Dict[str, Any]) -> list:
        """Create ATTOM property characteristics section"""
        story = []
        
        story.append(Paragraph("<b>Verified Property Characteristics</b>", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        property_data = detail_data.get('data', {}).get('property', [{}])[0]
        
        # Extract key characteristics
        building = property_data.get('building', {})
        lot = property_data.get('lot', {})
        
        # Build characteristics table
        char_data = [['Characteristic', 'Value']]
        
        # Building data
        if building.get('size', {}).get('bldgsize'):
            char_data.append(['Building Size', f"{building['size']['bldgsize']:,} sq ft"])
        
        if building.get('rooms', {}).get('beds'):
            char_data.append(['Bedrooms', str(building['rooms']['beds'])])
        
        if building.get('rooms', {}).get('bathstotal'):
            char_data.append(['Bathrooms', str(building['rooms']['bathstotal'])])
        
        if building.get('construction', {}).get('yearbuilt'):
            year = building['construction']['yearbuilt']
            age = 2025 - year
            char_data.append(['Year Built', f"{year} ({age} years old)"])
        
        # Lot data
        if lot.get('lotsize1'):
            char_data.append(['Lot Size', f"{lot['lotsize1']:,} sq ft"])
        
        if lot.get('pooltype'):
            char_data.append(['Pool', lot['pooltype']])
        
        # Zoning
        if property_data.get('area', {}).get('zoningCode'):
            char_data.append(['Zoning Code', property_data['area']['zoningCode']])
        
        if len(char_data) > 1:  # Has data beyond header
            char_table = Table(char_data, colWidths=[2.5*inch, 2.5*inch])
            char_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(char_table)
        else:
            story.append(Paragraph("<i>No detailed property characteristics available.</i>", self.styles['BodyText']))
        
        return story
