"""
Report Generator V3 - Clean Implementation
Matches the assessment web page structure exactly

Structure:
Page 1: Financial Analysis & Projections
Page 2: Executive Summary & Property Details  
Page 3: Ownership & Requirements
"""

import json
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

logger = logging.getLogger(__name__)

class ReportGeneratorV3:
    """Generate PDF assessment reports matching the web page structure"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_colors()
        self._setup_custom_styles()

    def _setup_colors(self):
        """Define color palette"""
        self.gold_start = colors.HexColor('#D4AF37')  # Gold
        self.gold_end = colors.HexColor('#FFD700')
        self.dark_gray = colors.HexColor('#2C3E50')
        self.light_gray = colors.HexColor('#BDC3C7')
        self.bg_gray = colors.HexColor('#F8F9FA')
        self.green = colors.HexColor('#27AE60')
        self.red = colors.HexColor('#E74C3C')
        self.blue = colors.HexColor('#3498DB')
        self.black = colors.HexColor('#000000')

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Page title
        self.styles.add(ParagraphStyle(
            'PageTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.dark_gray,
            spaceAfter=20,
            alignment=1  # Center
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.dark_gray,
            spaceAfter=8,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        ))

        # Section header with gold background
        self.styles.add(ParagraphStyle(
            'SectionHeaderGold',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.black,
            backColor=self.gold_start,
            spaceBefore=10,
            spaceAfter=8,
            leading=18,
            fontName='Helvetica-Bold',
            alignment=0,
            leftIndent=0,
            rightIndent=0,
            borderPadding=6,
        ))

        # Subsection
        self.styles.add(ParagraphStyle(
            'Subsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.dark_gray,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        # Address lines (for header)
        self.styles.add(ParagraphStyle(
            'AddressLinePrimary',
            parent=self.styles['Heading2'],
            fontSize=18,
            leading=20,
            textColor=self.dark_gray,
            spaceBefore=0,
            spaceAfter=0,
            alignment=1,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            'AddressLineSecondary',
            parent=self.styles['Heading3'],
            fontSize=14,
            leading=16,
            textColor=self.dark_gray,
            spaceBefore=2,
            spaceAfter=6,
            alignment=1,
            fontName='Helvetica'
        ))

        # Body text (check if exists first to avoid duplicate)
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                'BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=self.black
            ))

        # Small text
        self.styles.add(ParagraphStyle(
            'SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.black
        ))

        # Scenario card text
        self.styles.add(ParagraphStyle(
            'ScenarioCardText',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=9,
            textColor=self.dark_gray
        ))

    def _add_watermark(self, canvas_obj, doc):
        """Add CONFIDENTIAL watermark to first page only"""
        if canvas_obj.getPageNumber() == 1:
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica-Bold', 60)
            canvas_obj.setFillColor(colors.HexColor('#E0E0E0'))
            canvas_obj.setFillAlpha(0.3)
            canvas_obj.translate(letter[0] / 2, letter[1] / 2)
            canvas_obj.rotate(45)
            canvas_obj.drawCentredString(0, 0, 'CONFIDENTIAL')
            canvas_obj.restoreState()

    def _parse_json_field(self, field_value):
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
    def _get_numeric_metric(self, data: Dict, keys: Sequence[str], default: float = 0.0) -> float:
        """Return the first numeric metric found for the provided keys."""
        for key in keys:
            value = data.get(key)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    sanitized = value.replace('%', '').replace(',', '')
                    return float(sanitized)
                except (ValueError, AttributeError):
                    continue
        return default

    def _get_text_value(self, data: Dict, keys: Sequence[str]) -> str:
        """Return the first non-empty string value for the provided keys."""
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return ""

    def _get_currency_value(self, data: Dict, keys: Sequence[str]) -> str:
        """Return a currency-formatted string using the first matching key."""
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
            if isinstance(value, (int, float)):
                return f"${value:,.0f}"
        return "N/A"

    def _get_percentage_value(self, data: Dict, keys: Sequence[str], decimals: int = 1) -> str:
        """Return a percentage string using the first matching key."""
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
            if isinstance(value, (int, float)):
                return f"{value:.{decimals}f}%"
        return "N/A"

    def _get_multi_story_bundle(self, assessment):
        """Parse multi-story scenario data and return (scenarios, recommended_key, reason)."""
        financials = self._parse_json_field(getattr(assessment, 'financial_projections', {}))
        if not isinstance(financials, dict):
            return {}, None, ""

        multi_story = self._parse_json_field(financials.get('multi_story_scenarios'))
        if not isinstance(multi_story, dict):
            return {}, None, ""

        scenarios_raw = self._parse_json_field(multi_story.get('scenarios', {}))
        scenarios: Dict[str, Dict] = {}
        if isinstance(scenarios_raw, dict):
            for scenario_key, scenario_value in scenarios_raw.items():
                parsed = self._parse_json_field(scenario_value)
                if isinstance(parsed, dict):
                    scenarios[scenario_key] = parsed

        recommended_key = multi_story.get('recommended')
        if recommended_key not in scenarios:
            recommended_key = None

        reason = multi_story.get('recommended_reason') or multi_story.get('recommendation_reason') or ""
        return scenarios, recommended_key, reason

    def _get_parsed_scenarios(self, assessment):
        """Backwards-compatible helper returning only parsed scenarios."""
        scenarios, _, _ = self._get_multi_story_bundle(assessment)
        return scenarios

    def _get_logo_flowable(self):
        """Return a ReportLab Image for the LOGOS logo if available."""
        potential_paths = [
            Path(__file__).resolve().parents[2] / 'static' / 'home-logos.png',  # Backend/static (production)
            Path(__file__).resolve().parents[3] / 'frontend' / 'public' / 'home-logos.png',  # Dev environment
        ]

        for path in potential_paths:
            logger.info(f"Checking logo path: {path}")
            if path.exists():
                try:
                    image_reader = ImageReader(str(path))
                    original_width, original_height = image_reader.getSize()
                    aspect_ratio = (original_height / original_width) if original_width else 1

                    target_width = 1.8 * inch
                    target_height = target_width * aspect_ratio

                    img = Image(str(path), width=target_width, height=target_height, mask='auto')
                    img.hAlign = 'CENTER'

                    logger.info(
                        "Loaded LOGOS logo from: %s (original: %dx%d px, rendered: %.2fx%.2f in)",
                        path,
                        original_width,
                        original_height,
                        target_width / inch,
                        target_height / inch,
                    )
                    return img
                except Exception as exc:
                    logger.warning(f"Failed to load logo image at {path}: {exc}")
        logger.warning("LOGOS header image not found; falling back to text header.")
        return None

    def generate_report(
        self,
        assessment,
        property_obj,
        church,
        output_path: Optional[str] = None
    ) -> BytesIO:
        """
        Generate complete PDF report
        
        Args:
            assessment: Assessment model instance
            property_obj: Property model instance
            church: Church model instance
            output_path: Optional file path to save PDF
            
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Build content
        content = []
        
        # Page 1: Financial Analysis
        content.extend(self._create_page1_financial(assessment, property_obj, church))
        content.append(PageBreak())
        
        # Page 2: Executive Summary & Property Details
        content.extend(self._create_page2_property(assessment, property_obj, church))
        content.append(PageBreak())
        
        # Page 3: Ownership & Requirements
        content.extend(self._create_page3_ownership(assessment, property_obj, church))

        # Build PDF with watermark
        doc.build(content, onFirstPage=self._add_watermark, onLaterPages=lambda c, d: None)

        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())

        buffer.seek(0)
        return buffer

    def _create_page1_financial(self, assessment, property_obj, church):
        """Create Page 1: Financial Analysis & Projections"""
        content = []

        # Header: LOGOS logo image (fallback to text)
        logo = self._get_logo_flowable()
        if logo:
            content.append(logo)
            content.append(Spacer(1, 0.05*inch))
        else:
            content.append(Paragraph(
                "<font size=24 color='#D4AF37'><b>LOGOS</b></font>",
                self.styles['PageTitle']
            ))
            content.append(Spacer(1, 0.1*inch))

        # Property Address
        address = property_obj.street_address if property_obj else "N/A"
        city = property_obj.city if property_obj and property_obj.city else ""
        state = property_obj.state if property_obj and property_obj.state else ""
        zip_code = property_obj.zip_code if property_obj and property_obj.zip_code else ""
        
        logger.info(f"🔍 RENDERING ADDRESS: street={address}, city={city}, state={state}, zip={zip_code}")
        
        content.append(Paragraph(address, self.styles['AddressLinePrimary']))
        
        # City, State, ZIP on second line
        if city or state or zip_code:
            city_state_zip = f"{city}, {state} {zip_code}".strip()
            logger.info(f"✅ ADDING CITY LINE: {city_state_zip}")
            content.append(Paragraph(city_state_zip, self.styles['AddressLineSecondary']))
        else:
            logger.warning("⚠️ NO CITY/STATE/ZIP DATA - skipping second line")
        
        content.append(Spacer(1, 0.08*inch))

        # Applicant Contact Information
        content.append(Paragraph("<b>Applicant Information</b>", self.styles['Subsection']))
        applicant_info = [
            [Paragraph("<b>Church Name</b>", self.styles['SmallText']), Paragraph(church.name if church else "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Contact Email</b>", self.styles['SmallText']), Paragraph(church.primary_email if church and hasattr(church, 'primary_email') else "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Contact Phone</b>", self.styles['SmallText']), Paragraph(church.primary_phone if church and hasattr(church, 'primary_phone') else "N/A", self.styles['SmallText'])],
        ]
        applicant_table = Table(applicant_info, colWidths=[2*inch, 4*inch])
        applicant_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(applicant_table)
        content.append(Spacer(1, 0.08*inch))

        # Overall Score Badge
        score = assessment.overall_score or 0
        grade = self._get_grade(score)
        content.append(Paragraph(
            f"<font size=14><b>Overall Score:</b> {score:.1f}/100 (Grade {grade})</font>",
            self.styles['BodyText']
        ))
        content.append(Spacer(1, 0.08*inch))

        # Financial Projections & Analysis
        content.append(Paragraph(
            "<b>Financial Projections & Analysis</b>",
            self.styles['SectionHeaderGold']
        ))
        
        # IRR & Investment Returns
        content.extend(self._create_irr_section(assessment))
        
        # Development Scenarios Analysis
        content.extend(self._create_scenarios_table(assessment))

        return content

    def _create_page2_property(self, assessment, property_obj, church):
        """Create Page 2: Executive Summary & Property Details"""
        content = []
        # Unit Capacity Analysis (restored under scenarios table)
        content.extend(self._create_unit_capacity(assessment))

        # Revenue & Operating Performance (moved from Page 1)
        content.extend(self._create_revenue_performance(assessment))

        # Development Scenarios (Detailed)
        content.extend(self._create_detailed_scenarios(assessment))

        # Executive Summary
        content.append(Paragraph("<b>Executive Summary</b>", self.styles['SectionHeaderGold']))
        
        # Overall Assessment
        content.append(Paragraph("<b>Overall Assessment</b>", self.styles['Subsection']))
        score = assessment.overall_score or 0
        grade = self._get_grade(score)
        content.append(Paragraph(
            f"This property scores {score:.1f}/100 (Grade {grade}), placing it in the "
            f"{'top tier' if score >= 90 else 'strong candidate' if score >= 80 else 'viable'} "
            f"of Logos development opportunities.",
            self.styles['BodyText']
        ))
        content.append(Spacer(1, 0.08*inch))

        # Property Details
        content.append(Paragraph("<b>Property Details</b>", self.styles['Subsection']))
        lot_size = property_obj.lot_size_sqft if property_obj and property_obj.lot_size_sqft else 0
        building_size = property_obj.building_sqft if property_obj and property_obj.building_sqft else 0
        demolish = property_obj.demolish_all_structures if property_obj else False
        
        content.append(Paragraph(
            f"• {property_obj.street_address if property_obj else 'N/A'} - "
            f"Lot: {lot_size:,.0f} sq ft, Building: {building_size:,.0f} sq ft",
            self.styles['BodyText']
        ))
        if demolish:
            content.append(Paragraph(
                "• <b>Full Demolition Planned</b> - Existing structures to be removed for new development",
                self.styles['BodyText']
            ))
        content.append(Spacer(1, 0.08*inch))

        # Recommendation
        content.append(Paragraph("<b>Recommendation</b>", self.styles['Subsection']))
        recommendation = self._get_recommendation_text(score)
        content.append(Paragraph(recommendation, self.styles['BodyText']))
        content.append(Spacer(1, 0.12*inch))

        return content

    def _create_page3_ownership(self, assessment, property_obj, church):
        """Create Page 3: Ownership & Requirements"""
        content = []

        # Property Overview
        content.extend(self._create_property_overview(property_obj))

        # Available Build Space
        content.extend(self._create_build_space(assessment, property_obj))

        # Ownership & Financial Status
        content.extend(self._create_financial_status_section(assessment, property_obj))

        # Zoning & Land Use
        content.extend(self._create_zoning_section(property_obj))

        # Property Improvement Needs (NEW)
        if assessment.property_improvement_needs:
            content.extend(self._create_improvement_needs(assessment))

        # Capital Financing Need (NEW)
        if assessment.capital_financing_need:
            content.extend(self._create_financing_need(assessment))

        # Special Requirements (NEW)
        if assessment.special_requirements:
            content.extend(self._create_special_requirements(assessment))

        return content

    def _create_irr_section(self, assessment):
        """Create IRR & Investment Returns section"""
        content = []
        
        content.append(Paragraph("<b>IRR & Investment Returns (7-Year)</b>", self.styles['Subsection']))
        
        scenarios, recommended_key, recommended_reason = self._get_multi_story_bundle(assessment)
        if not scenarios:
            content.append(Paragraph("Financial projections are not available for this assessment.", self.styles['SmallText']))
            content.append(Spacer(1, 0.12*inch))
            return content

        recommended = scenarios.get(recommended_key) if recommended_key else None
        if not recommended:
            # Fallback to scenario with highest IRR
            best_key = None
            best_value = 0.0
            for key, scenario in scenarios.items():
                irr_value = self._get_numeric_metric(scenario, ['irr_percent', 'irr_7yr', 'irr'])
                if irr_value > best_value:
                    best_value = irr_value
                    best_key = key
            recommended = scenarios.get(best_key) if best_key else None
            recommended_key = best_key

        if not recommended:
            content.append(Paragraph("Financial projections data is incomplete.", self.styles['SmallText']))
            content.append(Spacer(1, 0.12*inch))
            return content

        irr_value = self._get_numeric_metric(recommended, ['irr_percent', 'irr_7yr', 'irr'])
        irr_display = self._get_percentage_value(recommended, ['irr_percent', 'irr_7yr', 'irr'])
        meets_target = irr_value >= 20

        display_name = recommended_key.replace('_', '-').title() if recommended_key else recommended.get('scenario_name', 'Recommended Scenario')

        content.append(Paragraph(
            f"<font size=14><b>{irr_display}</b></font> "
            f"{display_name} – {'✓ MEETS 20% TARGET' if meets_target else '⚠ BELOW 20% TARGET'}",
            self.styles['BodyText']
        ))
        content.append(Spacer(1, 0.08*inch))

        content.append(Paragraph("<b>Key Highlights</b>", self.styles['SmallText']))

        highlights = [
            f"• Equity required: {self._get_currency_value(recommended, ['equity_required_formatted', 'equity_required'])}",
            f"• Debt financing: {self._get_currency_value(recommended, ['debt_financing_formatted', 'permanent_loan_formatted', 'debt_financing', 'permanent_loan'])}",
            f"• First year NOI: {self._get_currency_value(recommended, ['noi_formatted', 'first_year_noi_formatted', 'first_year_noi'])}",
            f"• Total development cost: {self._get_currency_value(recommended, ['total_development_cost_formatted', 'total_development_cost'])}",
            f"• Units delivered: {int(recommended.get('units', 0)) if recommended.get('units') else 'N/A'}",
            f"• IRR: {irr_display}",
        ]

        if recommended_reason:
            highlights.append(f"• Recommendation rationale: {recommended_reason}")

        for item in highlights:
            content.append(Paragraph(item, self.styles['SmallText']))

        content.append(Spacer(1, 0.08*inch))
        return content

    def _create_scenarios_table(self, assessment):
        """Create Development Scenarios Analysis table"""
        content = []
        
        content.append(Paragraph("<b>Development Scenarios Analysis</b>", self.styles['Subsection']))
        content.append(Paragraph(
            "Construction cost: 3-story $275K, 4-story $325K, 5-story $415K, 425 sqft planning factor, 20% equity / 80% debt",
            self.styles['SmallText']
        ))
        content.append(Spacer(1, 0.06*inch))
        
        scenarios, recommended_key, recommended_reason = self._get_multi_story_bundle(assessment)
        if not scenarios:
            content.append(Paragraph("Financial projections are not available for this assessment.", self.styles['SmallText']))
            content.append(Spacer(1, 0.08*inch))
            return content
        
        # Table headers
        headers = [
            Paragraph('<b>Scenario</b>', self.styles['SmallText']),
            Paragraph('<b>Units</b>', self.styles['SmallText']),
            Paragraph('<b>IRR</b>', self.styles['SmallText']),
            Paragraph('<b>Year 1 NOI</b>', self.styles['SmallText']),
            Paragraph('<b>Total Cost</b>', self.styles['SmallText']),
            Paragraph('<b>Equity</b>', self.styles['SmallText']),
            Paragraph('<b>Debt</b>', self.styles['SmallText']),
        ]
        
        table_data = [headers]
        
        # Add scenario rows
        for scenario_name in ['3_story', '4_story', '5_story']:
            scenario = scenarios.get(scenario_name, {})
            if isinstance(scenario, dict) and scenario:
                display_name = scenario_name.replace('_', '-').title()
                is_recommended = scenario_name == recommended_key or bool(scenario.get('is_recommended'))
                units = scenario.get('units')
                irr_display = self._get_percentage_value(scenario, ['irr_percent', 'irr_7yr', 'irr'])
                noi_display = self._get_currency_value(scenario, ['noi_formatted', 'first_year_noi_formatted', 'first_year_noi'])
                total_cost = self._get_currency_value(scenario, ['total_development_cost_formatted', 'total_development_cost'])
                equity = self._get_currency_value(scenario, ['equity_required_formatted', 'equity_required'])
                debt = self._get_currency_value(scenario, ['debt_financing_formatted', 'debt_financing', 'permanent_loan'])

                row = [
                    Paragraph(
                        f"<b>{display_name}</b>{'<br/>Recommended' if is_recommended else ''}",
                        self.styles['SmallText']
                    ),
                    Paragraph(str(int(units)) if isinstance(units, (int, float)) else 'N/A', self.styles['SmallText']),
                    Paragraph(irr_display, self.styles['SmallText']),
                    Paragraph(noi_display, self.styles['SmallText']),
                    Paragraph(total_cost, self.styles['SmallText']),
                    Paragraph(equity, self.styles['SmallText']),
                    Paragraph(debt, self.styles['SmallText']),
                ]
                table_data.append(row)
        
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[1*inch, 0.6*inch, 0.6*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.gold_start),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.light_gray),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_gray]),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            content.append(table)

        if recommended_reason:
            content.append(Spacer(1, 0.04*inch))
            content.append(Paragraph(f"<b>Recommendation:</b> {recommended_reason}", self.styles['SmallText']))
        
        content.append(Spacer(1, 0.08*inch))
        return content

    def _create_unit_capacity(self, assessment):
        """Create Unit Capacity Analysis section"""
        content = []
        
        content.append(Paragraph("<b>Unit Capacity Analysis</b>", self.styles['Subsection']))
        
        scenarios, _, _ = self._get_multi_story_bundle(assessment)

        if not scenarios:
            content.append(Paragraph("Unit capacity analysis is not available due to missing projections.", self.styles['SmallText']))
            content.append(Spacer(1, 0.12*inch))
            return content

        # Build columns for side-by-side display
        column_data = []
        
        for scenario_name in ['3_story', '4_story', '5_story']:
            scenario = scenarios.get(scenario_name, {})
            if isinstance(scenario, dict) and scenario:
                display_name = scenario_name.replace('_', '-').title()
                units = scenario.get('units')
                total_units_text = str(int(units)) if isinstance(units, (int, float)) else 'N/A'

                # Build column content as list of paragraphs
                col_items = []
                col_items.append(Paragraph(f"<b>{display_name}</b>", self.styles['SmallText']))
                col_items.append(Paragraph(f"Total Units: {total_units_text}", self.styles['SmallText']))

                unit_mix_raw = self._parse_json_field(scenario.get('unit_mix', {}))
                if isinstance(unit_mix_raw, dict) and unit_mix_raw:
                    for unit_type, unit_info in unit_mix_raw.items():
                        unit_details = self._parse_json_field(unit_info)
                        count = unit_details.get('count')
                        avg_size = unit_details.get('avg_size') or unit_details.get('average_size')
                        percent = unit_details.get('percent') or unit_details.get('percentage')

                        count_text = str(int(count)) if isinstance(count, (int, float)) else 'N/A'
                        size_text = f"{avg_size:,.0f}" if isinstance(avg_size, (int, float)) else (avg_size or 'N/A')
                        if isinstance(percent, (int, float)):
                            percent_text = f"{percent:.0f}%"
                        elif isinstance(percent, str) and percent.strip():
                            percent_text = percent
                        else:
                            percent_text = ""

                        mix_line = f"• {unit_type.replace('_', ' ').title()} ({size_text} sf): {count_text}"
                        if percent_text:
                            mix_line += f" ({percent_text})"
                        col_items.append(Paragraph(mix_line, self.styles['SmallText']))
                else:
                    # Fallback to default mix if detailed mix not provided
                    if isinstance(units, (int, float)) and units:
                        studio = int(units * 0.2)
                        one_br = int(units * 0.5)
                        two_br = max(int(units) - studio - one_br, 0)
                        col_items.append(Paragraph(
                            f"• Studio (325 sf): {studio} (~20%)",
                            self.styles['SmallText']
                        ))
                        col_items.append(Paragraph(
                            f"• 1-Bedroom (450 sf): {one_br} (~50%)",
                            self.styles['SmallText']
                        ))
                        col_items.append(Paragraph(
                            f"• 2-Bedroom (675 sf): {two_br} (~30%)",
                            self.styles['SmallText']
                        ))

                column_data.append(col_items)

        # Create 3-column table with the scenarios
        if column_data:
            scenario_table = Table([column_data], colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
            scenario_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            content.append(scenario_table)

        content.append(Spacer(1, 0.08*inch))
        return content

    def _create_revenue_performance(self, assessment):
        """Create Revenue & Operating Performance section"""
        content = []
        
        content.append(Paragraph("<b>Revenue & Operating Performance</b>", self.styles['Subsection']))
        
        scenarios, recommended_key, _ = self._get_multi_story_bundle(assessment)
        financials = self._parse_json_field(getattr(assessment, 'financial_projections', {}))
        revenue_projections = self._parse_json_field(financials.get('revenue_projections', {})) if isinstance(financials, dict) else {}

        if not revenue_projections and not scenarios:
            content.append(Paragraph("Revenue projections are not available for this assessment.", self.styles['SmallText']))
            content.append(Spacer(1, 0.12*inch))
            return content

        if isinstance(revenue_projections, dict) and revenue_projections:
            annual_revenue = self._get_currency_value(revenue_projections, ['total_annual_revenue_formatted', 'total_annual_revenue'])
            operating_expenses_val = self._get_currency_value(revenue_projections, ['operating_expenses_formatted', 'operating_expenses'])
            noi_val = self._get_currency_value(revenue_projections, ['net_operating_income_formatted', 'net_operating_income'])
            expense_ratio = self._get_text_value(revenue_projections, ['operating_expense_ratio']) or '—'
            yield_val = self._get_percentage_value(revenue_projections, ['yield_on_cost', 'cap_rate'])
        else:
            recommended = scenarios.get(recommended_key) if recommended_key else next(iter(scenarios.values()), {})
            recommended = recommended if isinstance(recommended, dict) else {}
            annual_revenue = self._get_currency_value(recommended, ['annual_revenue_formatted', 'annual_revenue'])
            operating_expenses_val = self._get_currency_value(recommended, ['operating_expenses_formatted', 'operating_expenses'])
            noi_val = self._get_currency_value(recommended, ['noi_formatted', 'first_year_noi_formatted', 'first_year_noi'])
            expense_ratio = self._get_text_value(recommended, ['operating_expense_ratio']) or '—'
            yield_val = self._get_percentage_value(recommended, ['yield_on_cost', 'cap_rate'])

        perf_data = [
            [Paragraph("<b>Annual Revenue</b>", self.styles['SmallText']), Paragraph(annual_revenue, self.styles['SmallText'])],
            [Paragraph("<b>Operating Expenses</b>", self.styles['SmallText']), Paragraph(f"{operating_expenses_val}{f' ({expense_ratio})' if expense_ratio not in ('', '—') else ''}", self.styles['SmallText'])],
            [Paragraph("<b>Net Operating Income</b>", self.styles['SmallText']), Paragraph(noi_val, self.styles['SmallText'])],
            [Paragraph("<b>Yield on Cost</b>", self.styles['SmallText']), Paragraph(f"{yield_val} (Target: 7%)" if yield_val != 'N/A' else yield_val, self.styles['SmallText'])],
        ]

        perf_table = Table(perf_data, colWidths=[2.5*inch, 2.5*inch])
        perf_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(perf_table)

        assumptions = []
        if isinstance(revenue_projections, dict):
            assumptions = self._parse_json_field(revenue_projections.get('assumptions', []))
        if not assumptions:
            assumptions = [
                "• 10% studios, 80% 1BR, 10% 2BR unit mix",
                "• 30% operating expense ratio",
                "• 100% occupancy (conservative for Section 8)",
                "• 20% equity / 65% permanent loan",
                "• Tiered construction costs: 3-story $275K, 4-story $325K, 5-story $415K",
                "• 425 sqft average unit size",
            ]

        if assumptions:
            content.append(Spacer(1, 0.08*inch))
            content.append(Paragraph("<b>Key Assumptions:</b>", self.styles['SmallText']))
            for assumption in assumptions:
                content.append(Paragraph(str(assumption), self.styles['SmallText']))
        
        # Reduced spacer to minimize gap before page break
        logger.info("🔧 ADDING SPACER: Using 0.04 inch (reduced from 0.12) to minimize gap")
        content.append(Spacer(1, 0.04*inch))
        return content

    def _create_detailed_scenarios(self, assessment):
        """Create detailed Development Scenarios cards"""
        content = []
        
        content.append(Paragraph("<b>Development Scenarios (3/4/5 Stories)</b>", self.styles['SectionHeaderGold']))
        
        scenarios, recommended_key, recommended_reason = self._get_multi_story_bundle(assessment)

        if not scenarios:
            content.append(Paragraph("No development scenarios are available.", self.styles['SmallText']))
            return content

        card_cells = []
        recommended_index = None

        for idx, scenario_name in enumerate(['3_story', '4_story', '5_story']):
            scenario = scenarios.get(scenario_name, {})
            if not isinstance(scenario, dict) or not scenario:
                continue

            display_name = scenario_name.replace('_', '-').title()
            irr_value = self._get_numeric_metric(scenario, ['irr_percent', 'irr_7yr', 'irr'])
            meets_target = irr_value >= 20 if irr_value is not None else False
            is_recommended = scenario_name == recommended_key or bool(scenario.get('is_recommended'))

            header_text = f"<b>{display_name}</b>"
            if is_recommended:
                header_text += " ✓ Recommended"
            elif irr_value and irr_value < 10:
                header_text += " ⚠️ Not Recommended (IRR < 10%)"
            elif not meets_target:
                header_text += " ⚠️ Does Not Meet 20% Target"

            cost_per_unit = self._get_currency_value(scenario, ['cost_per_unit_formatted', 'cost_per_unit'])
            total_cost = self._get_currency_value(scenario, ['total_development_cost_formatted', 'total_development_cost'])
            annual_revenue = self._get_currency_value(scenario, ['annual_revenue_formatted', 'annual_revenue'])
            noi_value = self._get_currency_value(scenario, ['noi_formatted', 'first_year_noi_formatted', 'first_year_noi'])
            irr_display = self._get_percentage_value(scenario, ['irr_percent', 'irr_7yr', 'irr'])
            construction_duration = self._get_text_value(scenario, ['construction_duration', 'construction_timeline']) or "24 months"
            units_text = str(int(scenario.get('units'))) if isinstance(scenario.get('units'), (int, float)) else 'N/A'

            lines = [
                header_text,
                f"Units: {units_text}",
                f"Cost/Unit: {cost_per_unit}",
                f"Total Cost: {total_cost}",
                f"Construction: {construction_duration}",
                f"Annual Revenue: {annual_revenue}",
                f"NOI: {noi_value}",
                f"IRR: {irr_display}",
                f"Meets 20% Target: {'Yes' if meets_target else 'No'}"
            ]

            card_cells.append(Paragraph("<br/>".join(lines), self.styles['ScenarioCardText']))

            if is_recommended:
                recommended_index = len(card_cells) - 1

        if card_cells:
            col_count = len(card_cells)
            col_width = (6.9 * inch) / col_count if col_count else 2.3 * inch
            cards_table = Table([card_cells], colWidths=[col_width] * col_count)
            table_style = [
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('INNERGRID', (0, 0), (-1, -1), 0.3, self.light_gray),
                ('BOX', (0, 0), (-1, -1), 0.4, self.light_gray),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ]
            if recommended_index is not None:
                table_style.append(('BACKGROUND', (recommended_index, 0), (recommended_index, 0), self.bg_gray))

            cards_table.setStyle(TableStyle(table_style))
            content.append(cards_table)
            content.append(Spacer(1, 0.08*inch))

        if recommended_reason:
            content.append(Paragraph(f"<b>Why Recommended:</b> {recommended_reason}", self.styles['SmallText']))
        
        return content

    def _create_property_overview(self, property_obj):
        """Create Property Overview section"""
        content = []
        
        content.append(Paragraph("<b>Property Overview</b>", self.styles['SectionHeaderGold']))
        
        if not property_obj:
            content.append(Paragraph("Property information not available", self.styles['BodyText']))
            return content
        
        overview_data = [
            [Paragraph("<b>Street Address</b>", self.styles['SmallText']), Paragraph(property_obj.street_address or "N/A", self.styles['SmallText'])],
            [Paragraph("<b>City, State, ZIP</b>", self.styles['SmallText']), Paragraph(f"{property_obj.city}, {property_obj.state}, {property_obj.zip_code}" if property_obj.city else "N/A", self.styles['SmallText'])],
            [Paragraph("<b>County</b>", self.styles['SmallText']), Paragraph(property_obj.county or "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Year Built</b>", self.styles['SmallText']), Paragraph(str(property_obj.year_built) if property_obj.year_built else "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Assessed Value</b>", self.styles['SmallText']), Paragraph(f"${property_obj.assessed_value:,.0f}" if property_obj.assessed_value else "N/A", self.styles['SmallText'])],
        ]
        
        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(overview_table)
        
        # Parcel Details
        if property_obj.parcel_id:
            content.append(Spacer(1, 0.08*inch))
            content.append(Paragraph("<b>Primary Parcel</b>", self.styles['Subsection']))
            
            parcel_data = [
                [Paragraph("<b>Lot Size</b>", self.styles['SmallText']), Paragraph(f"{property_obj.lot_size_sqft:,.0f} sq ft ({property_obj.lot_size_acres:.2f} acres)" if property_obj.lot_size_sqft else "N/A", self.styles['SmallText'])],
                [Paragraph("<b>Building Size</b>", self.styles['SmallText']), Paragraph(f"{property_obj.building_sqft:,.0f} sq ft" if property_obj.building_sqft else "N/A", self.styles['SmallText'])],
                [Paragraph("<b>Parcel Number</b>", self.styles['SmallText']), Paragraph(property_obj.parcel_id, self.styles['SmallText'])],
                [Paragraph("<b>Assessed Value</b>", self.styles['SmallText']), Paragraph(f"${property_obj.assessed_value:,.0f}" if property_obj.assessed_value else "N/A", self.styles['SmallText'])],
            ]
            
            parcel_table = Table(parcel_data, colWidths=[2*inch, 4*inch])
            parcel_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            content.append(parcel_table)
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_build_space(self, assessment, property_obj):
        """Create Available Build Space - LOGOS Qualification section"""
        content = []
        
        content.append(Paragraph("<b>Available Build Space - LOGOS Qualification</b>", self.styles['SectionHeaderGold']))
        
        # Try assessment field first, fallback to property lot_size_sqft
        available_sqft = assessment.available_build_sqft if assessment.available_build_sqft else (property_obj.lot_size_sqft if property_obj and property_obj.lot_size_sqft else 0)
        available_acres = assessment.available_build_acres if assessment.available_build_acres else (property_obj.lot_size_acres if property_obj and property_obj.lot_size_acres else 0)
        qualifies = available_sqft >= 5000
        
        status = "✓ QUALIFIES FOR LOGOS" if qualifies else "✗ DOES NOT QUALIFY"
        content.append(Paragraph(
            f"<b>{status}</b><br/>"
            f"{available_sqft:,.0f} sqft available (Min: 5,000 sqft)",
            self.styles['BodyText']
        ))
        
        if property_obj and property_obj.demolish_all_structures:
            content.append(Spacer(1, 0.08*inch))
            content.append(Paragraph(
                "<b>Full Demolition:</b> Existing structures will be removed, maximizing available build space",
                self.styles['BodyText']
            ))
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_ownership_section(self, property_obj):
        """Create Ownership & Financial Status section"""
        content = []
        
        content.append(Paragraph("<b>Ownership & Financial Status</b>", self.styles['SectionHeaderGold']))
        
        if not property_obj:
            content.append(Paragraph("Ownership information not available", self.styles['BodyText']))
            return content
        
        # Parse data sources for owner info from Smarty
        owner_name = "N/A"
        purchase_date = "N/A"
        purchase_price = "N/A"
        
        if property_obj.data_sources:
            import json
            try:
                data = json.loads(property_obj.data_sources) if isinstance(property_obj.data_sources, str) else property_obj.data_sources
                smarty_data = data.get('smarty_data', {}).get('data', {})
                if smarty_data:
                    owner_info = smarty_data.get('owner', {})
                    owner_name = owner_info.get('name', 'N/A')
                    purchase_date = owner_info.get('last_sale_date', 'N/A')
                    purchase_price = owner_info.get('last_sale_price', 'N/A')
            except:
                pass
        
        content.append(Paragraph("<b>Current Owner</b>", self.styles['Subsection']))
        owner_data = [
            [Paragraph("<b>Owner Name</b>", self.styles['SmallText']), Paragraph(owner_name, self.styles['SmallText'])],
            [Paragraph("<b>Purchase Date</b>", self.styles['SmallText']), Paragraph(purchase_date, self.styles['SmallText'])],
            [Paragraph("<b>Purchase Price</b>", self.styles['SmallText']), Paragraph(f"${purchase_price:,.0f}" if isinstance(purchase_price, (int, float)) else purchase_price, self.styles['SmallText'])],
        ]
        
        owner_table = Table(owner_data, colWidths=[2*inch, 4*inch])
        owner_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(owner_table)
        
        content.append(Spacer(1, 0.08*inch))
        content.append(Paragraph(
            "<b>Owned Free & Clear</b><br/>"
            "No active mortgages or liens detected. Property appears to be owned outright.",
            self.styles['BodyText']
        ))
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_zoning_section(self, property_obj):
        """Create Zoning & Land Use Classification section"""
        content = []
        
        content.append(Paragraph("<b>Zoning & Land Use Classification</b>", self.styles['SectionHeaderGold']))
        
        if not property_obj:
            content.append(Paragraph("Zoning information not available", self.styles['BodyText']))
            return content
        
        zoning_data = [
            [Paragraph("<b>Zoning Code</b>", self.styles['SmallText']), Paragraph(property_obj.zoning_classification or "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Classification</b>", self.styles['SmallText']), Paragraph(property_obj.zoning_description or "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Land Use</b>", self.styles['SmallText']), Paragraph(property_obj.current_usage or "N/A", self.styles['SmallText'])],
        ]
        
        zoning_table = Table(zoning_data, colWidths=[2*inch, 4*inch])
        zoning_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(zoning_table)
        
        # Parcel Details
        if property_obj.parcel_id:
            content.append(Spacer(1, 0.08*inch))
            content.append(Paragraph("<b>Parcel Details</b>", self.styles['Subsection']))
            content.append(Paragraph(
                f"APN / Parcel Number: {property_obj.parcel_id}",
                self.styles['BodyText']
            ))
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_improvement_needs(self, assessment):
        """Create Property Improvement Needs section (NEW)"""
        content = []
        
        content.append(Paragraph("<b>Property Improvement Needs</b>", self.styles['SectionHeaderGold']))
        
        if isinstance(assessment.property_improvement_needs, list):
            needs = assessment.property_improvement_needs
        elif isinstance(assessment.property_improvement_needs, str):
            import json
            try:
                needs = json.loads(assessment.property_improvement_needs)
            except:
                needs = []
        else:
            needs = []
        
        if needs:
            for need in needs:
                content.append(Paragraph(f"• {need}", self.styles['BodyText']))
        else:
            content.append(Paragraph("No specific improvement needs identified", self.styles['BodyText']))
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_financing_need(self, assessment):
        """Create Capital Financing Need section (NEW)"""
        content = []
        
        content.append(Paragraph("<b>Capital Financing Need</b>", self.styles['SectionHeaderGold']))
        content.append(Paragraph(
            assessment.capital_financing_need or "Not specified",
            self.styles['BodyText']
        ))
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_financial_status_section(self, assessment, property_obj):
        """Create Ownership & Financial Status section"""
        content = []
        
        content.append(Paragraph("<b>Ownership & Financial Status</b>", self.styles['SectionHeaderGold']))
        
        # Owner Reported Value (from property market_value_estimate if user provided)
        owner_value = property_obj.market_value_estimate if property_obj and property_obj.market_value_estimate else None
        
        # Existing Debt Amount
        existing_debt = assessment.existing_debt_amount if assessment.existing_debt_amount else None
        
        financial_data = [
            [Paragraph("<b>Owner Reported Value</b>", self.styles['SmallText']), 
             Paragraph(f"${owner_value:,.0f}" if owner_value else "Not provided", self.styles['SmallText'])],
            [Paragraph("<b>Existing Debt Amount</b>", self.styles['SmallText']), 
             Paragraph(f"${existing_debt:,.0f}" if existing_debt else "None reported", self.styles['SmallText'])],
        ]
        
        financial_table = Table(financial_data, colWidths=[2*inch, 4*inch])
        financial_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(financial_table)
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_special_requirements(self, assessment):
        """Create Special Requirements section"""
        content = []
        
        content.append(Paragraph("<b>Special Requirements</b>", self.styles['SectionHeader']))
        content.append(Paragraph(
            assessment.special_requirements or "None specified",
            self.styles['BodyText']
        ))
        
        content.append(Spacer(1, 0.12*inch))
        return content

    def _create_development_preferences(self, assessment):
        """Create Development Preferences section"""
        content = []
        
        content.append(Paragraph("<b>Development Preferences</b>", self.styles['SectionHeader']))
        
        prefs = [
            [Paragraph("<b>Parking Required</b>", self.styles['SmallText']), Paragraph(str(assessment.parking_spaces_needed_after) if assessment.parking_spaces_needed_after else "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Timeline Preference</b>", self.styles['SmallText']), Paragraph(assessment.timeline_readiness or "N/A", self.styles['SmallText'])],
            [Paragraph("<b>Revenue Sharing</b>", self.styles['SmallText']), Paragraph(assessment.revenue_sharing_preference or "N/A", self.styles['SmallText'])],
        ]
        
        prefs_table = Table(prefs, colWidths=[2*inch, 4*inch])
        prefs_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(prefs_table)
        
        if assessment.special_requirements:
            content.append(Spacer(1, 0.08*inch))
            content.append(Paragraph("<b>Special Requirements</b>", self.styles['Subsection']))
            content.append(Paragraph(assessment.special_requirements, self.styles['BodyText']))
        
        return content

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 97: return 'A+'
        if score >= 93: return 'A'
        if score >= 90: return 'A-'
        if score >= 87: return 'B+'
        if score >= 83: return 'B'
        if score >= 80: return 'B-'
        if score >= 77: return 'C+'
        if score >= 73: return 'C'
        if score >= 70: return 'C-'
        if score >= 67: return 'D+'
        if score >= 63: return 'D'
        if score >= 60: return 'D-'
        return 'F'

    def _get_recommendation_text(self, score: float) -> str:
        """Get recommendation text based on score"""
        if score >= 90:
            return ("STRONGLY RECOMMENDED FOR DEVELOPMENT - This property scores highly across all key "
                   "metrics and represents an excellent development opportunity. Proceed with full due "
                   "diligence and site planning.")
        elif score >= 80:
            return ("RECOMMENDED FOR DEVELOPMENT - This property shows strong potential for development "
                   "with solid financial projections and good market conditions. Proceed with due diligence.")
        elif score >= 70:
            return ("CONSIDER FOR DEVELOPMENT - This property has viable development potential but may "
                   "require additional analysis of specific risk factors or market conditions.")
        else:
            return ("NOT RECOMMENDED AT THIS TIME - This property faces significant challenges that may "
                   "impact development viability. Additional evaluation or site improvements may be needed.")
