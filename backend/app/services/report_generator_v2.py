"""
PDF Report Generation Service V2
Generates professional 3-page PDF reports from property assessments
"""

import io
import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional

from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

logger = logging.getLogger(__name__)


class ReportGeneratorV2:
    """Generate professional 3-page PDF reports for property assessments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Colors
        self.gold_start = colors.HexColor('#D4AF37')  # Gold
        self.gold_end = colors.HexColor('#B8860B')     # Darker gold
        self.black = colors.HexColor('#000000')
        self.dark_gray = colors.HexColor('#333333')
        self.light_gray = colors.HexColor('#666666')
        self.bg_gray = colors.HexColor('#F5F5F5')
    
    @staticmethod
    def _parse_json_field(field_value):
        """Safely parse a JSON field that might be a string or already a dict/list"""
        if field_value is None:
            return {}
        if isinstance(field_value, (dict, list)):
            return field_value
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse JSON field: {field_value[:100]}")
                return {}
        return {}
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the report"""
        
        # Helper function to add style only if it doesn't exist
        def add_style_if_not_exists(style_name, style_config):
            if style_name not in self.styles:
                self.styles.add(ParagraphStyle(name=style_name, **style_config))
        
        # Cover title (gold gradient effect)
        add_style_if_not_exists('CoverTitle', {
            'parent': self.styles['Heading1'],
            'fontSize': 32,
            'textColor': colors.HexColor('#D4AF37'),
            'spaceAfter': 20,
            'spaceBefore': 40,
            'alignment': TA_CENTER,
            'fontName': 'Helvetica-Bold',
            'leading': 38
        })
        
        # Cover subtitle
        add_style_if_not_exists('CoverSubtitle', {
            'parent': self.styles['Normal'],
            'fontSize': 18,
            'textColor': colors.HexColor('#333333'),
            'spaceAfter': 10,
            'alignment': TA_CENTER,
            'fontName': 'Helvetica',
            'leading': 22
        })
        
        # Section header (gold)
        add_style_if_not_exists('SectionHeader', {
            'parent': self.styles['Heading2'],
            'fontSize': 16,
            'textColor': colors.HexColor('#D4AF37'),
            'spaceAfter': 12,
            'spaceBefore': 20,
            'fontName': 'Helvetica-Bold',
            'borderWidth': 1,
            'borderColor': colors.HexColor('#D4AF37'),
            'borderPadding': 6,
            'leftIndent': 0,
            'leading': 20
        })
        
        # Subsection header
        add_style_if_not_exists('SubsectionHeader', {
            'parent': self.styles['Heading3'],
            'fontSize': 13,
            'textColor': colors.HexColor('#000000'),
            'spaceAfter': 8,
            'spaceBefore': 12,
            'fontName': 'Helvetica-Bold',
            'leading': 16
        })
        
        # Body text
        add_style_if_not_exists('BodyText', {
            'parent': self.styles['Normal'],
            'fontSize': 10,
            'textColor': colors.HexColor('#333333'),
            'spaceAfter': 6,
            'alignment': TA_LEFT,
            'fontName': 'Helvetica',
            'leading': 14
        })
        
        # Table header
        add_style_if_not_exists('TableHeader', {
            'parent': self.styles['Normal'],
            'fontSize': 10,
            'textColor': colors.white,
            'fontName': 'Helvetica-Bold',
            'alignment': TA_LEFT,
            'leading': 12
        })
        
        # Table cell
        add_style_if_not_exists('TableCell', {
            'parent': self.styles['Normal'],
            'fontSize': 9,
            'textColor': colors.HexColor('#333333'),
            'fontName': 'Helvetica',
            'alignment': TA_LEFT,
            'leading': 11
        })
        
        # Highlight text (for key metrics)
        add_style_if_not_exists('HighlightText', {
            'parent': self.styles['Normal'],
            'fontSize': 14,
            'textColor': colors.HexColor('#D4AF37'),
            'fontName': 'Helvetica-Bold',
            'alignment': TA_CENTER,
            'leading': 18
        })
    
    def _add_watermark(self, canvas_obj, doc):
        """Add CONFIDENTIAL watermark to first page"""
        canvas_obj.saveState()
        canvas_obj.setFillColor(colors.red)
        canvas_obj.setFont('Helvetica-Bold', 60)
        canvas_obj.setFillAlpha(0.2)  # 20% opacity
        # Center the watermark diagonally
        canvas_obj.translate(letter[0]/2, letter[1]/2)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, 'CONFIDENTIAL')
        canvas_obj.restoreState()
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page numbers to pages 2 and 3 (no watermark)"""
        pass  # Just a placeholder, no watermark on later pages

    async def generate_assessment_report(
        self,
        assessment_id: int
    ) -> bytes:
        """
        Generate a comprehensive 3-page PDF report for an assessment
        
        Args:
            assessment_id: ID of the assessment to generate report for
            
        Returns:
            PDF file as bytes
        """
        # Fetch data with relationships
        assessment = self.db.query(Assessment).options(
            joinedload(Assessment.property_obj).joinedload(Property.church)
        ).filter(Assessment.id == assessment_id).first()
        
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        property_obj = assessment.property_obj
        church = property_obj.church if property_obj else None
        
        # The assessment object already has all the fields we need as direct attributes
        # No need to parse JSON - all data is on the assessment model itself
        
        # Track current page number for watermark
        self.current_page = 0
        
        # Create PDF document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build content
        story = []
        
        # PAGE 1: Cover Page
        story.extend(self._create_cover_page(assessment, property_obj, church))
        story.append(PageBreak())
        
        # PAGE 2: Property & Financial Overview
        story.extend(self._create_property_overview(
            assessment, property_obj, church
        ))
        story.append(PageBreak())
        
        # PAGE 3: Development Analysis & Financial Projections
        story.extend(self._create_development_analysis(assessment))
        
        # Build PDF with watermark on first page
        doc.build(story, onFirstPage=self._add_watermark, onLaterPages=self._add_page_number)
        
        # Get PDF bytes
        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_bytes

    def _get_grade_from_score(self, score):
        """Convert numeric score to letter grade"""
        if score >= 95: return 'A+'
        elif score >= 90: return 'A'
        elif score >= 87: return 'A-'
        elif score >= 83: return 'B+'
        elif score >= 80: return 'B'
        elif score >= 77: return 'B-'
        elif score >= 73: return 'C+'
        elif score >= 70: return 'C'
        elif score >= 67: return 'C-'
        elif score >= 63: return 'D+'
        elif score >= 60: return 'D'
        else: return 'F'
    
    def _get_recommendation(self, score):
        """Get recommendation text based on score"""
        if score >= 85:
            return "STRONGLY RECOMMENDED FOR DEVELOPMENT"
        elif score >= 75:
            return "RECOMMENDED FOR DEVELOPMENT"
        elif score >= 65:
            return "PROCEED WITH CAUTION"
        else:
            return "NOT RECOMMENDED"
    
    def _get_recommendation_detail(self, score, grade):
        """Get detailed recommendation text"""
        if score >= 85:
            return f"This property scores {score:.1f}/100 (Grade {grade}), placing it in the top tier of Logos development opportunities. The financial projections are solid, market demand is strong, and partnership alignment is excellent. Proceed with full due diligence and site planning."
        elif score >= 75:
            return f"This property scores {score:.1f}/100 (Grade {grade}), showing strong development potential. Financial viability is good and market conditions are favorable. Recommend proceeding with detailed feasibility analysis."
        elif score >= 65:
            return f"This property scores {score:.1f}/100 (Grade {grade}), indicating moderate development potential with some concerns. Further investigation recommended to address identified risks before proceeding."
        else:
            return f"This property scores {score:.1f}/100 (Grade {grade}), indicating significant challenges for development. Not recommended unless major issues can be resolved."

    def _create_cover_page(self, assessment, property_obj, church):
        """Create comprehensive cover page with executive summary"""
        content = []
        
        # Logo at top - smaller and higher up
        # No spacer at all - logo starts at the very top of the page
        logo_path = Path(__file__).parent.parent.parent / "static" / "home-logos.png"
        if logo_path.exists():
            # Moderately sized logo: 4.5 inches wide with proportional height
            logo = Image(str(logo_path), width=4.5*inch, height=1.46*inch, kind='proportional')
            logo.hAlign = 'CENTER'
            content.append(logo)
            content.append(Spacer(1, 0.05*inch))  # Minimal space between logo and title
        else:
            content.append(Paragraph("LOGOS", self.styles['CoverTitle']))
            content.append(Spacer(1, 0.05*inch))
        
        # Gold title section
        gold_title_style = ParagraphStyle(
            'GoldTitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=self.gold_start,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=20,
            spaceAfter=4
        )
        
        content.append(Paragraph("<b>Property Development Assessment</b>", gold_title_style))
        
        # Report details
        detail_style = ParagraphStyle(
            'Detail',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.dark_gray,
            alignment=TA_CENTER,
            leading=16
        )
        
        if church:
            content.append(Paragraph(f"<b>Prepared for:</b> {church.name}", detail_style))
        content.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}", detail_style))
        content.append(Paragraph(f"<b>Assessment ID:</b> #{assessment.id}", detail_style))
        content.append(Spacer(1, 0.3*inch))
        
        # Get score and grade
        score = assessment.overall_score or 0
        grade = self._get_grade_from_score(score)
        
        # Executive Summary Header
        exec_header_style = ParagraphStyle(
            'ExecHeader',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=self.black,
            fontName='Helvetica-Bold',
            leading=18,
            spaceAfter=8
        )
        content.append(Paragraph("📄 <b>Executive Summary</b>", exec_header_style))
        
        # Overall Assessment
        subsection_style = ParagraphStyle(
            'Subsection',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.black,
            fontName='Helvetica-Bold',
            leading=14,
            spaceAfter=4
        )
        content.append(Paragraph("<b>Overall Assessment</b>", subsection_style))
        
        body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.dark_gray,
            leading=14,
            spaceAfter=8
        )
        
        content.append(Paragraph(
            f"This property has been evaluated across five key dimensions: Financial Viability (30%), "
            f"Market Demand (25%), Location Quality (20%), Partnership Alignment (15%), and Risk Assessment (10%). "
            f"The weighted composite score is <b>{score:.1f}/100 (Grade {grade})</b>.",
            body_style
        ))
        
        # Property Details (parse enriched data)
        content.append(Paragraph("<b>Property Details</b>", subsection_style))
        
        # Get enriched data from property_obj - PRIORITY: assessment custom input > property form input > API data
        # CRITICAL PRIORITY ORDER:
        # 1. assessment.available_build_sqft (user manually entered on form - highest priority)
        # 2. property_obj.lot_size_sqft (from property form or API enrichment)
        # 3. smarty_data (API fallback)
        
        data_sources = self._parse_json_field(property_obj.data_sources) if hasattr(property_obj, 'data_sources') else {}
        smarty_data = data_sources.get('smarty_data', {}).get('data', {}) if isinstance(data_sources, dict) else {}
        
        is_user_provided = False  # Flag to track if using applicant-submitted custom value
        
        # PRIORITY 1: Assessment custom lot size (applicant manually entered - most accurate)
        if hasattr(assessment, 'available_build_sqft') and assessment.available_build_sqft:
            primary_lot_sqft = assessment.available_build_sqft
            primary_building_sqft = property_obj.building_sqft if hasattr(property_obj, 'building_sqft') else 0
            is_user_provided = True
        # PRIORITY 2: Property form lot size (user entered in property form)
        elif hasattr(property_obj, 'lot_size_sqft') and property_obj.lot_size_sqft:
            primary_lot_sqft = property_obj.lot_size_sqft
            primary_building_sqft = property_obj.building_sqft if hasattr(property_obj, 'building_sqft') else 0
        else:
            # PRIORITY 3: API data (smarty_data)
            # Get from individual_parcels[0] if multi-address, otherwise from root smarty_data
            multi_address_info = smarty_data.get('multi_address', {})
            individual_parcels = multi_address_info.get('individual_parcels', []) if isinstance(multi_address_info, dict) else []
            
            if individual_parcels and len(individual_parcels) > 0:
                primary_parcel = individual_parcels[0]
                primary_lot_sqft = primary_parcel.get('lot', {}).get('size_sqft') if isinstance(primary_parcel, dict) else None
                primary_building_sqft = primary_parcel.get('building', {}).get('size_sqft') if isinstance(primary_parcel, dict) else None
            else:
                # Fallback to root smarty_data
                primary_lot_sqft = smarty_data.get('lot', {}).get('size_sqft') if smarty_data else None
                primary_building_sqft = smarty_data.get('building', {}).get('size_sqft') if smarty_data else None
        
        # Build property details text
        prop_details = []
        if property_obj.street_address:
            detail_line = f"• {property_obj.street_address}"
            if primary_lot_sqft:
                detail_line += f" - Lot: {primary_lot_sqft:,} sq ft"
                # Add indicator if this is applicant-submitted custom value
                if is_user_provided:
                    detail_line += " ⚠️ (Applicant-Submitted)"
            if primary_building_sqft:
                detail_line += f", Building: {primary_building_sqft:,} sq ft"
            prop_details.append(detail_line)
        
        # Additional addresses
        additional_addresses = self._parse_json_field(property_obj.additional_addresses) if hasattr(property_obj, 'additional_addresses') else []
        if isinstance(additional_addresses, list):
            for addr in additional_addresses:
                if isinstance(addr, dict):
                    addr_line = f"• {addr.get('address', 'Unknown')}"
                    enriched = addr.get('enriched_data', {})
                    if isinstance(enriched, dict):
                        lot_sqft = enriched.get('lot', {}).get('size_sqft')
                        bldg_sqft = enriched.get('building', {}).get('size_sqft')
                        if lot_sqft:
                            addr_line += f" - Lot: {lot_sqft:,} sq ft"
                        if bldg_sqft:
                            addr_line += f", Building: {bldg_sqft:,} sq ft"
                    prop_details.append(addr_line)
        
        # Total parcels
        total_parcels = 1 + len(additional_addresses) if additional_addresses else 1
        combined_lot = (primary_lot_sqft or 0)
        if isinstance(additional_addresses, list):
            for addr in additional_addresses:
                if isinstance(addr, dict):
                    enriched = addr.get('enriched_data', {})
                    if isinstance(enriched, dict):
                        combined_lot += enriched.get('lot', {}).get('size_sqft', 0) or 0
        
        if prop_details:
            for detail in prop_details:
                content.append(Paragraph(detail, body_style))
        
        if total_parcels > 1:
            combined_text = f"<b>Combined Total:</b> {combined_lot:,} sq ft ({total_parcels} parcels)"
            if is_user_provided:
                combined_text += " ⚠️ (Applicant-Submitted)"
            content.append(Paragraph(combined_text, body_style))
        elif is_user_provided and total_parcels == 1:
            # Single parcel with user-provided value - add note after property details
            content.append(Paragraph(
                "⚠️ <i>Note: Lot size is applicant-submitted value. Verify with property records.</i>",
                body_style
            ))
        
        # Demolition notice
        is_demolish = property_obj.demolish_all_structures if hasattr(property_obj, 'demolish_all_structures') else False
        if is_demolish:
            content.append(Paragraph(
                "🏗️ <b>Full Demolition Planned</b> - Existing structures to be removed for new development",
                body_style
            ))
        
        content.append(Spacer(1, 0.2*inch))
        
        # Recommendation
        content.append(Paragraph("<b>Recommendation</b>", subsection_style))
        recommendation = self._get_recommendation(score)
        rec_detail = self._get_recommendation_detail(score, grade)
        
        # Color-code recommendation: Green if recommended (score >= 70), Red if not
        rec_color = colors.HexColor('#008000') if score >= 70 else colors.HexColor('#DC143C')
        
        rec_style = ParagraphStyle(
            'Recommendation',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=rec_color,
            fontName='Helvetica-Bold',
            leading=16,
            spaceAfter=8
        )
        content.append(Paragraph(recommendation, rec_style))
        content.append(Paragraph(rec_detail, body_style))
        
        # Comprehensive Grading Breakdown (matches assessment page)
        content.append(Spacer(1, 0.15*inch))
        content.append(Paragraph("<b>Comprehensive Grading Breakdown</b>", subsection_style))
        
        # Create cell style for grading table
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11
        )
        
        # Define scoring categories with weights (matching the assessment page exactly)
        scoring_categories = [
            ('Financial Viability', assessment.financial_score, 30),
            ('Market Demand', assessment.market_score, 25),
            ('Location Quality', assessment.location_score, 20),
            ('Partnership Alignment', assessment.partnership_score, 15),
            ('Risk Assessment', assessment.risk_score, 10),
        ]
        
        # Build comprehensive grading table
        grading_headers = [
            Paragraph('<b>Category</b>', cell_style),
            Paragraph('<b>Score</b>', cell_style),
            Paragraph('<b>Grade</b>', cell_style),
            Paragraph('<b>Weight</b>', cell_style),
            Paragraph('<b>Status</b>', cell_style)
        ]
        grading_data = [grading_headers]
        
        for category_name, score_value, weight in scoring_categories:
            if score_value is None:
                continue
                
            grade = self._get_grade_from_score(score_value)
            status = '✓ Pass' if score_value >= 60 else '✗ Fail'
            status_color = 'green' if score_value >= 60 else 'red'
            
            grading_data.append([
                Paragraph(f'{category_name}', cell_style),
                Paragraph(f'{score_value:.1f}/100', cell_style),
                Paragraph(f'<b>{grade}</b>', cell_style),
                Paragraph(f'{weight}%', cell_style),
                Paragraph(f'<font color="{status_color}"><b>{status}</b></font>', cell_style)
            ])
        
        if len(grading_data) > 1:  # Has data rows beyond header
            grading_table = Table(grading_data, colWidths=[1.8*inch, 1*inch, 0.8*inch, 0.8*inch, 0.9*inch])
            grading_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.gold_start),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.dark_gray),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_gray]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            content.append(grading_table)
        
        return content

    def _create_property_overview(self, assessment, property_obj, church):
        """Create Page 2: Property & Financial Overview"""
        content = []
        
        # Page title
        content.append(Paragraph(
            "Property & Financial Overview",
            self.styles['SectionHeader']
        ))
        content.append(Spacer(1, 0.2*inch))
        
        # 1. Property Information
        content.append(Paragraph("Property Information", self.styles['SubsectionHeader']))
        
        # Create cell style for tables
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11
        )
        
        property_data = [
            [Paragraph('<b>Address</b>', table_cell_style), Paragraph(f"{property_obj.street_address or 'N/A'}", table_cell_style)],
            [Paragraph('<b>City, State</b>', table_cell_style), Paragraph(f"{property_obj.city or 'N/A'}, {property_obj.state or 'N/A'} {property_obj.zip_code or ''}", table_cell_style)],
            [Paragraph('<b>Lot Size</b>', table_cell_style), Paragraph(self._format_lot_size(property_obj), table_cell_style)],
            [Paragraph('<b>Building Size</b>', table_cell_style), Paragraph(f"{property_obj.building_sqft:,} sqft" if property_obj.building_sqft else "N/A", table_cell_style)],
            [Paragraph('<b>Year Built</b>', table_cell_style), Paragraph(str(property_obj.year_built) if property_obj.year_built else "N/A", table_cell_style)],
            [Paragraph('<b>Current Use</b>', table_cell_style), Paragraph(property_obj.current_usage or "N/A", table_cell_style)],
            [Paragraph('<b>Zoning</b>', table_cell_style), Paragraph(property_obj.zoning_description or "N/A", table_cell_style)],
        ]
        
        # Don't add additional parcels inline - we'll show them in a separate detailed section below
        
        property_table = Table(property_data, colWidths=[2*inch, 4.5*inch])
        property_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(property_table)
        content.append(Spacer(1, 0.15*inch))
        
        # Detailed Parcel Breakdown (if multi-parcel)
        additional_addresses = self._parse_json_field(property_obj.additional_addresses) if hasattr(property_obj, 'additional_addresses') else []
        if isinstance(additional_addresses, list) and len(additional_addresses) > 0:
            content.append(Paragraph(f"<b>Parcel Breakdown ({1 + len(additional_addresses)} parcels)</b>", self.styles['SubsectionHeader']))
            
            # Primary Parcel - use same source as above
            data_sources_detail = self._parse_json_field(property_obj.data_sources) if hasattr(property_obj, 'data_sources') else {}
            smarty_data_detail = data_sources_detail.get('smarty_data', {}).get('data', {}) if isinstance(data_sources_detail, dict) else {}
            multi_address_detail = smarty_data_detail.get('multi_address', {})
            parcels_detail = multi_address_detail.get('individual_parcels', []) if isinstance(multi_address_detail, dict) else []
            
            if parcels_detail and len(parcels_detail) > 0:
                primary_parcel_detail = parcels_detail[0]
                primary_lot = primary_parcel_detail.get('lot', {}).get('size_sqft') if isinstance(primary_parcel_detail, dict) else None
                primary_bldg = primary_parcel_detail.get('building', {}).get('size_sqft') if isinstance(primary_parcel_detail, dict) else None
            else:
                primary_lot = smarty_data_detail.get('lot', {}).get('size_sqft')
                primary_bldg = smarty_data_detail.get('building', {}).get('size_sqft')
            
            parcel_details = [
                [Paragraph('<b>Parcel</b>', table_cell_style), Paragraph('<b>Address</b>', table_cell_style), 
                 Paragraph('<b>Lot Size</b>', table_cell_style), Paragraph('<b>Building Size</b>', table_cell_style)]
            ]
            
            # Add primary
            parcel_details.append([
                Paragraph('Primary', table_cell_style),
                Paragraph(property_obj.street_address or 'N/A', table_cell_style),
                Paragraph(f"{primary_lot:,} sq ft" if primary_lot else 'N/A', table_cell_style),
                Paragraph(f"{primary_bldg:,} sq ft" if primary_bldg else 'N/A', table_cell_style)
            ])
            
            # Add additional parcels
            total_lot = primary_lot or 0
            total_bldg = primary_bldg or 0
            
            for i, addr in enumerate(additional_addresses):
                if isinstance(addr, dict):
                    addr_str = addr.get('address', 'Unknown')
                    enriched = addr.get('enriched_data', {})
                    if isinstance(enriched, dict):
                        lot_sqft = enriched.get('lot', {}).get('size_sqft', 0) or 0
                        bldg_sqft = enriched.get('building', {}).get('size_sqft', 0) or 0
                        total_lot += lot_sqft
                        total_bldg += bldg_sqft
                        
                        parcel_details.append([
                            Paragraph(f'Additional {i+1}', table_cell_style),
                            Paragraph(addr_str, table_cell_style),
                            Paragraph(f"{lot_sqft:,} sq ft" if lot_sqft else 'N/A', table_cell_style),
                            Paragraph(f"{bldg_sqft:,} sq ft" if bldg_sqft else 'N/A', table_cell_style)
                        ])
            
            # Add totals row
            parcel_details.append([
                Paragraph('<b>TOTAL</b>', table_cell_style),
                Paragraph('', table_cell_style),
                Paragraph(f"<b>{total_lot:,} sq ft</b>", table_cell_style),
                Paragraph(f"<b>{total_bldg:,} sq ft</b>", table_cell_style)
            ])
            
            parcel_table = Table(parcel_details, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            parcel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.gold_start),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, -1), (-1, -1), self.bg_gray),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            content.append(parcel_table)
            content.append(Spacer(1, 0.15*inch))
        
        content.append(Spacer(1, 0.05*inch))
        
        # 2. Available Build Space - LOGOS Qualification
        content.append(Paragraph("Available Build Space - LOGOS Qualification", self.styles['SubsectionHeader']))
        
        # Calculate available build space
        available_build_sqft = assessment.available_build_sqft or 0
        combined_lot_size = property_obj.lot_size_sqft or 0
        
        # Add lot sizes from additional parcels
        if isinstance(additional_addresses, list):
            for addr in additional_addresses:
                if isinstance(addr, dict) and addr.get('lot_size_sqft'):
                    combined_lot_size += addr['lot_size_sqft']
        
        # If user provided custom available space, use it; otherwise calculate
        if available_build_sqft > 0:
            available_space = available_build_sqft
        else:
            # Calculate based on lot size minus building size
            building_size = property_obj.building_sqft or 0
            available_space = combined_lot_size - building_size if not property_obj.demolish_all_structures else combined_lot_size
        
        available_acres = available_space / 43560 if available_space > 0 else 0
        qualifies_for_logos = available_space >= 5000
        
        # Create qualification box
        qual_style = ParagraphStyle(
            'QualificationBox',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.green if qualifies_for_logos else colors.red
        )
        
        qual_data = []
        if qualifies_for_logos:
            qual_data.append([Paragraph("✓ QUALIFIES FOR LOGOS", qual_style)])
            qual_data.append([Paragraph(f"{available_space:,} sqft available (Min: 5,000 sqft)", table_cell_style)])
        else:
            qual_data.append([Paragraph("✗ DOES NOT QUALIFY", qual_style)])
            qual_data.append([Paragraph(f"{available_space:,} sqft available (Min: 5,000 sqft required)", table_cell_style)])
        
        qual_table = Table(qual_data, colWidths=[6.5*inch])
        qual_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen if qualifies_for_logos else colors.mistyrose),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2, colors.green if qualifies_for_logos else colors.red),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        content.append(qual_table)
        content.append(Spacer(1, 0.1*inch))
        
        # Add breakdown details
        space_data = []
        space_data.append([Paragraph('<b>Total Lot Size</b>', table_cell_style), 
                          Paragraph(f"{combined_lot_size:,} sqft ({combined_lot_size/43560:.2f} acres)", table_cell_style)])
        if property_obj.demolish_all_structures:
            space_data.append([Paragraph('<b>Development Plan</b>', table_cell_style), 
                              Paragraph("Full Demolition - All land available", table_cell_style)])
        else:
            space_data.append([Paragraph('<b>Existing Buildings</b>', table_cell_style), 
                              Paragraph(f"{property_obj.building_sqft:,} sqft" if property_obj.building_sqft else "N/A", table_cell_style)])
        space_data.append([Paragraph('<b>Available Space</b>', table_cell_style), 
                          Paragraph(f"{available_space:,} sqft ({available_acres:.2f} acres)", table_cell_style)])
        
        space_table = Table(space_data, colWidths=[2*inch, 4.5*inch])
        space_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(space_table)
        content.append(Spacer(1, 0.2*inch))
        
        # 3. Ownership & Financial Details
        content.append(Paragraph("Ownership & Financial Details", self.styles['SubsectionHeader']))
        
        owns_free = assessment.owns_property_free_clear or False
        has_mortgage = assessment.existing_debt_amount and assessment.existing_debt_amount > 0
        mortgage_balance = assessment.existing_debt_amount
        willing_ground_lease = assessment.willing_to_ground_lease or False
        assessed_value = property_obj.assessed_value
        expects_sanctuary = assessment.expects_sanctuary_replacement or False
        sanctuary_cost = assessment.sanctuary_replacement_cost_estimate
        
        ownership_data = [
            [Paragraph('<b>Ownership Status</b>', table_cell_style), Paragraph('Owned Free & Clear' if owns_free else 'Has Mortgage/Debt', table_cell_style)],
        ]
        
        if has_mortgage and mortgage_balance:
            ownership_data.append([Paragraph('<b>Mortgage Balance</b>', table_cell_style), Paragraph(f"${mortgage_balance:,}", table_cell_style)])
        
        ownership_data.extend([
            [Paragraph('<b>Assessed Value</b>', table_cell_style), Paragraph(f"${assessed_value:,}" if assessed_value else "N/A", table_cell_style)],
            [Paragraph('<b>Ground Lease Willing</b>', table_cell_style), Paragraph('Yes' if willing_ground_lease else 'No', table_cell_style)],
        ])
        
        if expects_sanctuary:
            ownership_data.append([Paragraph('<b>Sanctuary Replacement</b>', table_cell_style), Paragraph('Required', table_cell_style)])
            if sanctuary_cost:
                ownership_data.append([Paragraph('<b>Est. Replacement Cost</b>', table_cell_style), Paragraph(f"${sanctuary_cost:,}", table_cell_style)])
        
        ownership_table = Table(ownership_data, colWidths=[2*inch, 4.5*inch])
        ownership_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(ownership_table)
        content.append(Spacer(1, 0.2*inch))
        
        # 3.5. Property Needs & Financing (NEW SECTION)
        property_improvement_needs = self._parse_json_field(assessment.property_improvement_needs)
        capital_financing_need = assessment.capital_financing_need
        
        if property_improvement_needs or capital_financing_need:
            content.append(Paragraph("Property Needs & Financing", self.styles['SubsectionHeader']))
            
            needs_data = []
            
            if property_improvement_needs and isinstance(property_improvement_needs, list) and len(property_improvement_needs) > 0:
                # Map improvement codes to readable labels
                improvement_labels = {
                    'hvac': 'HVAC/AC System',
                    'roof': 'Roof',
                    'landscaping': 'Landscaping',
                    'painting': 'Painting',
                    'interior': 'Interior Improvements',
                    'other': 'Other'
                }
                improvements = [improvement_labels.get(need, need) for need in property_improvement_needs]
                improvements_text = ', '.join(improvements)
                needs_data.append([Paragraph('<b>Property Improvements Needed</b>', table_cell_style), 
                                  Paragraph(improvements_text, table_cell_style)])
            
            if capital_financing_need:
                needs_data.append([Paragraph('<b>Capital/Financing Need</b>', table_cell_style), 
                                  Paragraph(capital_financing_need, table_cell_style)])
            
            if needs_data:
                needs_table = Table(needs_data, colWidths=[2*inch, 4.5*inch])
                needs_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                    ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                content.append(needs_table)
                content.append(Spacer(1, 0.2*inch))
        
        # 3. Development Preferences
        content.append(Paragraph("Development Preferences & Requirements", self.styles['SubsectionHeader']))
        
        parking_needed = assessment.parking_spaces_needed_after
        timeline_pref = assessment.timeline_readiness or 'N/A'
        min_units = assessment.preferred_unit_count
        revenue_share = assessment.revenue_sharing_preference or 'N/A'
        special_reqs = assessment.special_requirements or 'None specified'
        
        preferences_data = [
            [Paragraph('<b>Parking Required</b>', table_cell_style), Paragraph(f"{parking_needed} spaces" if parking_needed else "N/A", table_cell_style)],
            [Paragraph('<b>Timeline Preference</b>', table_cell_style), Paragraph(timeline_pref, table_cell_style)],
        ]
        
        if min_units:
            preferences_data.append([Paragraph('<b>Minimum Units</b>', table_cell_style), Paragraph(str(min_units), table_cell_style)])
        
        preferences_data.extend([
            [Paragraph('<b>Revenue Sharing</b>', table_cell_style), Paragraph(revenue_share, table_cell_style)],
            [Paragraph('<b>Special Requirements</b>', table_cell_style), Paragraph(special_reqs[:200] + '...' if len(str(special_reqs)) > 200 else str(special_reqs), table_cell_style)],
        ])
        
        preferences_table = Table(preferences_data, colWidths=[2*inch, 4.5*inch])
        preferences_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(preferences_table)
        content.append(Spacer(1, 0.2*inch))
        
        # 5. Financial Overview (if we have financial projections)
        financial_projections = self._parse_json_field(assessment.financial_projections)
        if financial_projections and isinstance(financial_projections, dict):
            multi_story_data = financial_projections.get('multi_story_scenarios', {})
            if isinstance(multi_story_data, dict):
                scenarios = multi_story_data.get('scenarios', {})
                recommended = multi_story_data.get('recommended', '4_story')
                
                # Get the recommended scenario
                rec_scenario = scenarios.get(recommended, {})
                if rec_scenario and isinstance(rec_scenario, dict):
                    content.append(Paragraph("Financial Overview - Recommended Scenario", self.styles['SubsectionHeader']))
                    
                    # Create highlight box
                    highlight_style = ParagraphStyle(
                        'HighlightBox',
                        parent=self.styles['Normal'],
                        fontSize=10,
                        textColor=self.dark_gray,
                        alignment=TA_CENTER,
                        fontName='Helvetica-Bold'
                    )
                    
                    # Extract key metrics
                    story_name = recommended.replace('_', '-').title()
                    units = rec_scenario.get('units', 0)
                    irr = rec_scenario.get('irr_percent', 0)
                    equity = rec_scenario.get('equity_required', 0)
                    debt = rec_scenario.get('debt_financing', 0)
                    noi_year1 = rec_scenario.get('noi_year_1', 0)
                    total_cost = rec_scenario.get('total_development_cost', 0)
                    
                    # Create financial highlights table
                    highlights_data = []
                    highlights_data.append([Paragraph(f"<b>Recommended Development:</b> {story_name} ({units} units)", table_cell_style)])
                    highlights_data.append([Paragraph(f"<b>Target IRR:</b> {irr:.1f}% {'✓ MEETS 20% TARGET' if irr >= 20 else '✗ Below 20% target'}", table_cell_style)])
                    
                    highlights_table = Table(highlights_data, colWidths=[6.5*inch])
                    highlights_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOX', (0, 0), (-1, -1), 1.5, self.gold_start),
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    content.append(highlights_table)
                    content.append(Spacer(1, 0.1*inch))
                    
                    # Key metrics in two columns
                    metrics_data = [
                        [Paragraph('<b>Equity Required (20%)</b>', table_cell_style), 
                         Paragraph(f"${equity:,}", table_cell_style),
                         Paragraph('<b>Permanent Loan (65% LTV)</b>', table_cell_style),
                         Paragraph(f"${int(debt * 0.65):,}", table_cell_style)],
                        [Paragraph('<b>Total Development Cost</b>', table_cell_style),
                         Paragraph(f"${total_cost:,}", table_cell_style),
                         Paragraph('<b>First Year NOI</b>', table_cell_style),
                         Paragraph(f"${noi_year1:,}" if noi_year1 else "N/A", table_cell_style)],
                    ]
                    
                    metrics_table = Table(metrics_data, colWidths=[1.625*inch, 1.625*inch, 1.625*inch, 1.625*inch])
                    metrics_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                        ('BACKGROUND', (2, 0), (2, -1), self.bg_gray),
                        ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                        ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    content.append(metrics_table)
        
        return content

    def _create_development_analysis(self, assessment):
        """Create Page 3: Development Analysis & Financial Projections"""
        content = []
        
        # Page title
        content.append(Paragraph(
            "Development Analysis & Financial Projections",
            self.styles['SectionHeader']
        ))
        content.append(Spacer(1, 0.2*inch))
        
        # Get financial projections from assessment (safely parse JSON)
        financial_projections = self._parse_json_field(assessment.financial_projections)
        
        # Extract scenarios - CRITICAL: scenarios is a DICT with keys '3_story', '4_story', '5_story', NOT a list!
        multi_story_data = financial_projections.get('multi_story_scenarios', {}) if isinstance(financial_projections, dict) else {}
        if isinstance(multi_story_data, dict):
            scenarios = multi_story_data.get('scenarios', {})
            recommended = multi_story_data.get('recommended', '5_story')
            recommended_reason = multi_story_data.get('recommended_reason', '')
        else:
            scenarios = {}
            recommended = '5_story'
            recommended_reason = ''
        
        # Table cell style for reuse
        table_cell_style = self.styles['TableCell']
        
        if scenarios and isinstance(scenarios, dict):
            # 1. Multi-Story Development Scenarios Comparison
            content.append(Paragraph("Multi-Story Development Scenarios", self.styles['SubsectionHeader']))
            
            scenario_headers = [
                Paragraph('<b>Scenario</b>', table_cell_style),
                Paragraph('<b>Units</b>', table_cell_style),
                Paragraph('<b>IRR %</b>', table_cell_style),
                Paragraph('<b>Annual NOI</b>', table_cell_style),
                Paragraph('<b>Total Dev Cost</b>', table_cell_style),
                Paragraph('<b>Equity (20%)</b>', table_cell_style),
                Paragraph('<b>Debt (80%)</b>', table_cell_style)
            ]
            scenario_data = [scenario_headers]
            
            # Process 3, 4, and 5 story scenarios
            for story_key in ['3_story', '4_story', '5_story']:
                if story_key in scenarios:
                    scenario = scenarios[story_key]
                    if not isinstance(scenario, dict):
                        continue
                    
                    # Format story name with recommended badge
                    story_name = story_key.replace('_', '-').title()
                    if story_key == recommended:
                        story_name += ' ✓ RECOMMENDED'
                    
                    units = scenario.get('units', 0)
                    irr_percent = scenario.get('irr_percent', 0)
                    noi_formatted = scenario.get('noi_formatted', 'N/A')
                    total_cost_formatted = scenario.get('total_development_cost_formatted', 'N/A')
                    equity_formatted = scenario.get('equity_required_formatted', 'N/A')
                    debt_formatted = scenario.get('debt_financing_formatted', 'N/A')
                    
                    scenario_data.append([
                        Paragraph(f"<b>{story_name}</b>" if story_key == recommended else story_name, table_cell_style),
                        Paragraph(f"{units:,}" if units else 'N/A', table_cell_style),
                        Paragraph(f"<b>{irr_percent:.1f}%</b>" if irr_percent else 'N/A', table_cell_style),
                        Paragraph(noi_formatted, table_cell_style),
                        Paragraph(total_cost_formatted, table_cell_style),
                        Paragraph(f"<b>{equity_formatted}</b>", table_cell_style),
                        Paragraph(debt_formatted, table_cell_style)
                    ])
            
            scenario_table = Table(scenario_data, colWidths=[1.2*inch, 0.7*inch, 0.7*inch, 1*inch, 1.1*inch, 1*inch, 1*inch])
            scenario_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.gold_start),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_gray]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(scenario_table)
            content.append(Spacer(1, 0.15*inch))
            
            # Add recommended reason if available
            if recommended_reason:
                content.append(Paragraph(
                    f"<b>Recommendation:</b> {recommended_reason}",
                    self.styles['Normal']
                ))
                content.append(Spacer(1, 0.2*inch))
            
            # 2. Detailed Analysis of Recommended Scenario
            recommended_scenario = scenarios.get(recommended) if recommended in scenarios else None
            if recommended_scenario and isinstance(recommended_scenario, dict):
                story_name = recommended.replace('_', '-').title()
                content.append(Paragraph(
                    f"{story_name} Development - Detailed Analysis",
                    self.styles['SubsectionHeader']
                ))
                
                # Extract detailed metrics from the recommended scenario
                units = recommended_scenario.get('units', 0)
                irr_percent = recommended_scenario.get('irr_percent', 0)
                total_cost_formatted = recommended_scenario.get('total_development_cost_formatted', 'N/A')
                noi_formatted = recommended_scenario.get('noi_formatted', 'N/A')
                equity_formatted = recommended_scenario.get('equity_required_formatted', 'N/A')
                debt_formatted = recommended_scenario.get('debt_financing_formatted', 'N/A')
                
                metrics_data = [
                    [Paragraph('<b>Total Units</b>', table_cell_style), Paragraph(f"{units:,}" if units else 'N/A', table_cell_style)],
                    [Paragraph('<b>Total Development Cost</b>', table_cell_style), Paragraph(total_cost_formatted, table_cell_style)],
                    [Paragraph('<b>Annual NOI</b>', table_cell_style), Paragraph(noi_formatted, table_cell_style)],
                    [Paragraph('<b>IRR (25 years)</b>', table_cell_style), Paragraph(f"<b>{irr_percent:.2f}%</b>" if irr_percent else 'N/A', table_cell_style)],
                    [Paragraph('<b>Equity Required (20%)</b>', table_cell_style), Paragraph(f"<b>{equity_formatted}</b>", table_cell_style)],
                    [Paragraph('<b>Debt Financing (80%)</b>', table_cell_style), Paragraph(debt_formatted, table_cell_style)],
                ]
                
                metrics_table = Table(metrics_data, colWidths=[3*inch, 3.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                    ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                content.append(metrics_table)
                content.append(Spacer(1, 0.2*inch))
                
                # 3. Unit Mix Breakdown
                unit_mix = recommended_scenario.get('unit_mix', {})
                if unit_mix:
                    content.append(Paragraph("Unit Mix & Specifications", self.styles['SubsectionHeader']))
                    
                    mix_headers = ['<b>Type</b>', '<b>Size (sqft)</b>', '<b>Count</b>', '<b>% of Total</b>']
                    mix_data = [mix_headers]
                    
                    for unit_type, details in unit_mix.items():
                        count = details.get('count', 0)
                        avg_size = details.get('avg_size', 0)
                        percentage = (count / units * 100) if units > 0 else 0
                        
                        mix_data.append([
                            unit_type.replace('_', ' ').title(),
                            f"{avg_size:,}",
                            str(count),
                            f"{percentage:.0f}%"
                        ])
                    
                    mix_table = Table(mix_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1.5*inch])
                    mix_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), self.gold_start),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, self.light_gray),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_gray]),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    content.append(mix_table)
                    content.append(Spacer(1, 0.15*inch))
                
                # 4. Financial Structure
                content.append(Paragraph("Financial Structure", self.styles['SubsectionHeader']))
                
                equity = recommended_scenario.get('equity_required', 0)
                debt = recommended_scenario.get('debt_financing', 0)
                total_dev_cost = recommended_scenario.get('total_development_cost', 0)
                
                structure_data = [
                    [Paragraph('<b>Equity (20%)</b>', table_cell_style), Paragraph(f"{equity_formatted}", table_cell_style)],
                    [Paragraph('<b>Debt (80%)</b>', table_cell_style), Paragraph(f"{debt_formatted}", table_cell_style)],
                    [Paragraph('<b>Total Development Cost</b>', table_cell_style), Paragraph(f"{total_cost_formatted}", table_cell_style)],
                ]
                
                structure_table = Table(structure_data, colWidths=[3*inch, 3.5*inch])
                structure_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                    ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                content.append(structure_table)
                content.append(Spacer(1, 0.2*inch))
                
                # 5. Revenue & Operating Performance
                revenue_projections = financial_projections.get('revenue_projections', {})
                if revenue_projections and isinstance(revenue_projections, dict):
                    content.append(Paragraph("Revenue & Operating Performance", self.styles['SubsectionHeader']))
                    
                    # Extract revenue metrics
                    annual_revenue = revenue_projections.get('total_annual_revenue', 0)
                    operating_expenses = revenue_projections.get('operating_expenses', 0)
                    noi = revenue_projections.get('net_operating_income', 0)
                    expense_ratio = revenue_projections.get('operating_expense_ratio', '42%')
                    yield_on_cost = revenue_projections.get('yield_on_cost') or revenue_projections.get('cap_rate', 0)
                    
                    revenue_data = [
                        [Paragraph('<b>Annual Revenue</b>', table_cell_style), 
                         Paragraph(f"${annual_revenue:,}" if annual_revenue else "N/A", table_cell_style)],
                        [Paragraph('<b>Operating Expenses</b>', table_cell_style), 
                         Paragraph(f"${operating_expenses:,} ({expense_ratio})" if operating_expenses else "N/A", table_cell_style)],
                        [Paragraph('<b>Net Operating Income (NOI)</b>', table_cell_style), 
                         Paragraph(f"${noi:,}" if noi else "N/A", table_cell_style)],
                        [Paragraph('<b>Yield on Cost</b>', table_cell_style), 
                         Paragraph(f"{yield_on_cost:.2f}% (Target: 7%)" if yield_on_cost else "N/A", table_cell_style)],
                    ]
                    
                    revenue_table = Table(revenue_data, colWidths=[3*inch, 3.5*inch])
                    revenue_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                        ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_gray]),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    content.append(revenue_table)
                    
                    # Add assumptions if available
                    assumptions = revenue_projections.get('assumptions', [])
                    if assumptions and isinstance(assumptions, list):
                        content.append(Spacer(1, 0.1*inch))
                        content.append(Paragraph("<b>Key Assumptions:</b>", self.styles['BodyText']))
                        for assumption in assumptions[:5]:  # Limit to 5 assumptions
                            content.append(Paragraph(f"• {assumption}", self.styles['BodyText']))
                
        else:
            # Show basic financial info even without detailed scenarios
            content.append(Paragraph("Financial Analysis", self.styles['SubsectionHeader']))
            
            # Show key metrics from the financial projections if available
            if financial_projections and isinstance(financial_projections, dict):
                metrics = []
                
                if financial_projections.get('score') is not None:
                    metrics.append(f"<b>Financial Score:</b> {financial_projections['score']:.1f}/100")
                if financial_projections.get('total_lot_size_sqft'):
                    metrics.append(f"<b>Total Lot Size:</b> {financial_projections['total_lot_size_sqft']:,} sq ft")
                if financial_projections.get('available_build_sqft'):
                    metrics.append(f"<b>Available Build Area:</b> {financial_projections['available_build_sqft']:,} sq ft")
                if financial_projections.get('meets_minimum') is not None:
                    meets = "Yes" if financial_projections['meets_minimum'] else "No"
                    metrics.append(f"<b>Meets Minimum Requirements:</b> {meets}")
                if financial_projections.get('disqualified') is not None:
                    disq = "Yes" if financial_projections['disqualified'] else "No"
                    metrics.append(f"<b>Disqualified:</b> {disq}")
                
                if metrics:
                    for metric in metrics:
                        content.append(Paragraph(metric, self.styles['BodyText']))
                    content.append(Spacer(1, 0.1*inch))
            
            content.append(Paragraph(
                "Detailed multi-story development scenarios with unit mix, IRR calculations, and cash flow projections "
                "will be generated upon completion of full feasibility analysis.",
                self.styles['BodyText']
            ))
        
        # Add Market Analysis if available
        content.append(Spacer(1, 0.2*inch))
        market_analysis = self._parse_json_field(assessment.market_analysis)
        if market_analysis and isinstance(market_analysis, dict):
            content.append(Paragraph("Market Analysis", self.styles['SubsectionHeader']))
            
            # Demographics
            demographics = market_analysis.get('demographics', {})
            if demographics:
                content.append(Paragraph("<b>Demographics:</b>", self.styles['BodyText']))
                demo_text = []
                if demographics.get('population'):
                    demo_text.append(f"Population: {demographics['population']:,}")
                if demographics.get('median_income'):
                    demo_text.append(f"Median Income: ${demographics['median_income']:,}")
                if demographics.get('median_age'):
                    demo_text.append(f"Median Age: {demographics['median_age']}")
                if demo_text:
                    content.append(Paragraph(" | ".join(demo_text), self.styles['BodyText']))
            
            # Demand indicators
            demand = market_analysis.get('demand_indicators', {})
            if demand:
                content.append(Paragraph("<b>Market Demand:</b>", self.styles['BodyText']))
                demand_text = []
                if demand.get('housing_demand'):
                    demand_text.append(f"Housing Demand: {demand['housing_demand']}")
                if demand.get('rent_growth'):
                    demand_text.append(f"Rent Growth: {demand['rent_growth']}")
                if demand_text:
                    content.append(Paragraph(" | ".join(demand_text), self.styles['BodyText']))
            
            # AMI Limits
            ami_limits = market_analysis.get('ami_limits', {})
            if ami_limits:
                content.append(Spacer(1, 0.1*inch))
                content.append(Paragraph("<b>Area Median Income (AMI) Limits:</b>", self.styles['BodyText']))
                
                ami_data = []
                if ami_limits.get('ami_50_percent_2person'):
                    ami_data.append([Paragraph('<b>50% AMI (2-person)</b>', table_cell_style), 
                                   Paragraph(f"${ami_limits['ami_50_percent_2person']:,}", table_cell_style)])
                if ami_limits.get('ami_60_percent_2person'):
                    ami_data.append([Paragraph('<b>60% AMI (2-person)</b>', table_cell_style), 
                                   Paragraph(f"${ami_limits['ami_60_percent_2person']:,}", table_cell_style)])
                if ami_limits.get('ami_80_percent_2person'):
                    ami_data.append([Paragraph('<b>80% AMI (2-person)</b>', table_cell_style), 
                                   Paragraph(f"${ami_limits['ami_80_percent_2person']:,}", table_cell_style)])
                if ami_limits.get('ami_100_percent_2person'):
                    ami_data.append([Paragraph('<b>100% AMI (2-person)</b>', table_cell_style), 
                                   Paragraph(f"${ami_limits['ami_100_percent_2person']:,}", table_cell_style)])
                
                if ami_data:
                    ami_table = Table(ami_data, colWidths=[2*inch, 1.5*inch])
                    ami_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                        ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    content.append(ami_table)
        
        # Add Environmental Factors (Flood Risk) if available
        property_data_sources = self._parse_json_field(assessment.property_obj.data_sources) if hasattr(assessment.property_obj, 'data_sources') else {}
        smarty_data = property_data_sources.get('smarty_data', {}).get('data', {}) if isinstance(property_data_sources, dict) else {}
        flood_data = smarty_data.get('flood', {})
        
        if flood_data:
            content.append(Spacer(1, 0.2*inch))
            content.append(Paragraph("Environmental Factors - Flood Risk", self.styles['SubsectionHeader']))
            
            flood_zone = flood_data.get('flood_zone', 'N/A')
            risk_level = flood_data.get('risk_level', 'N/A')
            insurance_required = flood_data.get('insurance_required', False)
            
            # Determine risk color
            if risk_level in ['low', 'minimal']:
                risk_color = colors.green
                bg_color = colors.lightgreen
            elif risk_level == 'moderate':
                risk_color = colors.orange
                bg_color = colors.lightyellow
            else:
                risk_color = colors.red
                bg_color = colors.mistyrose
            
            flood_data_table = [
                [Paragraph('<b>Flood Zone</b>', table_cell_style), 
                 Paragraph(f"{flood_zone}", table_cell_style)],
                [Paragraph('<b>Risk Level</b>', table_cell_style), 
                 Paragraph(f"{risk_level.title() if risk_level != 'N/A' else 'N/A'}", table_cell_style)],
                [Paragraph('<b>Insurance Required</b>', table_cell_style), 
                 Paragraph("Yes" if insurance_required else "No", table_cell_style)],
            ]
            
            flood_table = Table(flood_data_table, colWidths=[2*inch, 2*inch])
            flood_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.bg_gray),
                ('BACKGROUND', (1, 1), (1, 1), bg_color),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                ('TEXTCOLOR', (1, 1), (1, 1), risk_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(flood_table)
        
        # Add Risk Factors if available
        risk_factors = self._parse_json_field(assessment.risk_factors)
        if risk_factors and isinstance(risk_factors, dict):
            content.append(Spacer(1, 0.2*inch))
            content.append(Paragraph("Risk Assessment", self.styles['SubsectionHeader']))
            
            risks = risk_factors.get('identified_risks', [])
            if isinstance(risks, list) and len(risks) > 0:
                for i, risk in enumerate(risks[:5]):  # Show top 5 risks
                    if isinstance(risk, dict):
                        risk_level = risk.get('level', 'Unknown')
                        risk_desc = risk.get('description', 'No description')
                        mitigation = risk.get('mitigation', 'Under review')
                        content.append(Paragraph(
                            f"<b>{i+1}. {risk_level} Risk:</b> {risk_desc[:150]}",
                            self.styles['BodyText']
                        ))
                        content.append(Paragraph(
                            f"   <i>Mitigation:</i> {mitigation[:150]}",
                            self.styles['BodyText']
                        ))
            elif isinstance(risk_factors, dict):
                # If risk_factors is directly a dict with risk info
                content.append(Paragraph(
                    f"Risk assessment completed. Overall risk score: {assessment.risk_score or 'N/A'}/100",
                    self.styles['BodyText']
                ))
        
        # Footer
        content.append(Spacer(1, 0.3*inch))
        content.append(Paragraph(
            "<i>Note: All projections are based on current market conditions and standard development assumptions. "
            "Actual results may vary. This analysis assumes 65% site coverage and 425 sqft efficiency planning factor.</i>",
            ParagraphStyle(
                'FooterNote',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=self.light_gray,
                alignment=TA_JUSTIFY,
                fontName='Helvetica-Oblique',
                leading=10
            )
        ))
        
        return content

    def _format_lot_size(self, property_obj):
        """Format lot size with both sqft and acres"""
        sqft = property_obj.lot_size_sqft
        acres = property_obj.lot_size_acres
        
        if sqft and acres:
            return f"{sqft:,} sqft ({acres:.2f} acres)"
        elif sqft:
            return f"{sqft:,} sqft"
        elif acres:
            return f"{acres:.2f} acres"
        else:
            return "N/A"
