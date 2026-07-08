#!/usr/bin/env python3
"""
generate_dossier.py — Phase 6 PDF dossier generator.

Takes a JSON analysis file (produced by the IP Detector skill workflow)
and emits a brutal PDF dossier using ReportLab.

The dossier structure:
  1. Cover page — concept name, input type, date, verdict in 60pt bold caps
  2. Executive summary — verdict, Gold Index, 5 dimension scores, 10-yr cost, capture, ROI
  3. Input & IP classification
  4. Prior-art matrix
  5. Market projection
  6. Filing & maintenance cost
  7. Scoring breakdown
  8. Verdict section (varies by verdict: rock-not-gold / conditions / roadmap)
  9. Disclaimer footer

Usage:
    python generate_dossier.py --data <path-to-analysis.json> --output <output.pdf>

JSON schema (see top of file for full structure): see the example in
skills/ip-detector/assets/example_analysis.json.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)


# ---------- Font registration ----------

def register_fonts():
    """Register English-friendly fonts. Fall back to Helvetica if not available."""
    font_pairs = [
        # (registered name, file path)
        ('Tinos', '/usr/share/fonts/truetype/english/Tinos-Regular.ttf'),
        ('Tinos-Bold', '/usr/share/fonts/truetype/english/Tinos-Bold.ttf'),
        ('Tinos-Italic', '/usr/share/fonts/truetype/english/Tinos-Italic.ttf'),
        ('Tinos-BoldItalic', '/usr/share/fonts/truetype/english/Tinos-BoldItalic.ttf'),
        ('Carlito', '/usr/share/fonts/truetype/english/Carlito-Regular.ttf'),
        ('Carlito-Bold', '/usr/share/fonts/truetype/english/Carlito-Bold.ttf'),
        ('Carlito-Italic', '/usr/share/fonts/truetype/english/Carlito-Italic.ttf'),
    ]
    registered = {}
    for name, path in font_pairs:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = path
            except Exception:
                pass

    # Fall back paths (DejaVu / Liberation)
    fallback_pairs = [
        ('Tinos', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'),
        ('Tinos-Bold', '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'),
        ('Tinos-Italic', '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'),
        ('Tinos-BoldItalic', '/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'),
        ('Carlito', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'),
        ('Carlito-Bold', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
        ('Carlito-Italic', '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'),
    ]
    for name, path in fallback_pairs:
        if name not in registered and os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = path
            except Exception:
                pass

    # Map font families for bold/italic resolution
    if 'Tinos' in registered and 'Tinos-Bold' in registered:
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        registerFontFamily('Tinos', normal='Tinos', bold='Tinos-Bold',
                           italic='Tinos-Italic', boldItalic='Tinos-BoldItalic')
    if 'Carlito' in registered and 'Carlito-Bold' in registered:
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        registerFontFamily('Carlito', normal='Carlito', bold='Carlito-Bold',
                           italic='Carlito-Italic', boldItalic='Carlito-Bold')

    body_font = 'Tinos' if 'Tinos' in registered else 'Times-Roman'
    heading_font = 'Carlito' if 'Carlito' in registered else 'Helvetica-Bold'
    return body_font, heading_font


# ---------- Styles ----------

def make_styles(body_font: str, heading_font: str):
    """Build the stylesheet hierarchy."""
    base = getSampleStyleSheet()

    # Verdict color depends on verdict — set later
    styles = {
        # Cover page
        'cover_concept_name': ParagraphStyle(
            'CoverConceptName', parent=base['Normal'],
            fontName=heading_font, fontSize=28, leading=34,
            alignment=TA_CENTER, spaceAfter=24, textColor=colors.HexColor('#1a1a1a')
        ),
        'cover_meta': ParagraphStyle(
            'CoverMeta', parent=base['Normal'],
            fontName=body_font, fontSize=11, leading=14,
            alignment=TA_CENTER, spaceAfter=6, textColor=colors.HexColor('#555555')
        ),
        'verdict_file': ParagraphStyle(
            'VerdictFile', parent=base['Normal'],
            fontName=heading_font, fontSize=60, leading=68,
            alignment=TA_CENTER, spaceBefore=80, spaceAfter=40,
            textColor=colors.HexColor('#0a7a3b')  # green
        ),
        'verdict_borderline': ParagraphStyle(
            'VerdictBorderline', parent=base['Normal'],
            fontName=heading_font, fontSize=60, leading=68,
            alignment=TA_CENTER, spaceBefore=80, spaceAfter=40,
            textColor=colors.HexColor('#b8860b')  # dark goldenrod
        ),
        'verdict_donotfile': ParagraphStyle(
            'VerdictDoNotFile', parent=base['Normal'],
            fontName=heading_font, fontSize=60, leading=68,
            alignment=TA_CENTER, spaceBefore=80, spaceAfter=40,
            textColor=colors.HexColor('#8b0000')  # dark red
        ),
        'verdict_label': ParagraphStyle(
            'VerdictLabel', parent=base['Normal'],
            fontName=heading_font, fontSize=12, leading=14,
            alignment=TA_CENTER, spaceBefore=40, spaceAfter=12,
            textColor=colors.HexColor('#555555')
        ),
        'cover_gold_index': ParagraphStyle(
            'CoverGoldIndex', parent=base['Normal'],
            fontName=heading_font, fontSize=24, leading=28,
            alignment=TA_CENTER, spaceAfter=8,
            textColor=colors.HexColor('#1a1a1a')
        ),

        # Body
        'body': ParagraphStyle(
            'Body', parent=base['Normal'],
            fontName=body_font, fontSize=10.5, leading=14,
            alignment=TA_LEFT, spaceAfter=8, textColor=colors.HexColor('#1a1a1a')
        ),
        'body_justified': ParagraphStyle(
            'BodyJustified', parent=base['Normal'],
            fontName=body_font, fontSize=10.5, leading=14,
            alignment=TA_LEFT, spaceAfter=8, textColor=colors.HexColor('#1a1a1a')
        ),
        'h1': ParagraphStyle(
            'H1', parent=base['Heading1'],
            fontName=heading_font, fontSize=18, leading=22,
            alignment=TA_LEFT, spaceBefore=18, spaceAfter=10,
            textColor=colors.HexColor('#0a0a0a')
        ),
        'h2': ParagraphStyle(
            'H2', parent=base['Heading2'],
            fontName=heading_font, fontSize=13, leading=16,
            alignment=TA_LEFT, spaceBefore=12, spaceAfter=6,
            textColor=colors.HexColor('#1a1a1a')
        ),
        'h3': ParagraphStyle(
            'H3', parent=base['Heading3'],
            fontName=heading_font, fontSize=11, leading=14,
            alignment=TA_LEFT, spaceBefore=8, spaceAfter=4,
            textColor=colors.HexColor('#333333')
        ),
        'small': ParagraphStyle(
            'Small', parent=base['Normal'],
            fontName=body_font, fontSize=9, leading=11,
            alignment=TA_LEFT, spaceAfter=4, textColor=colors.HexColor('#444444')
        ),
        'caption': ParagraphStyle(
            'Caption', parent=base['Normal'],
            fontName=body_font, fontSize=8.5, leading=10.5,
            alignment=TA_LEFT, spaceAfter=2, textColor=colors.HexColor('#666666')
        ),
        'disclaimer': ParagraphStyle(
            'Disclaimer', parent=base['Normal'],
            fontName=body_font, fontSize=8.5, leading=11,
            alignment=TA_LEFT, spaceBefore=24, spaceAfter=4,
            textColor=colors.HexColor('#666666')
        ),
        'verdict_section_title_rock': ParagraphStyle(
            'VerdictRockTitle', parent=base['Heading1'],
            fontName=heading_font, fontSize=18, leading=22,
            alignment=TA_LEFT, spaceBefore=18, spaceAfter=10,
            textColor=colors.HexColor('#8b0000')
        ),
        'verdict_section_title_borderline': ParagraphStyle(
            'VerdictBorderlineTitle', parent=base['Heading1'],
            fontName=heading_font, fontSize=18, leading=22,
            alignment=TA_LEFT, spaceBefore=18, spaceAfter=10,
            textColor=colors.HexColor('#b8860b')
        ),
        'verdict_section_title_file': ParagraphStyle(
            'VerdictFileTitle', parent=base['Heading1'],
            fontName=heading_font, fontSize=18, leading=22,
            alignment=TA_LEFT, spaceBefore=18, spaceAfter=10,
            textColor=colors.HexColor('#0a7a3b')
        ),
    }
    return styles


# ---------- Number formatting ----------

def fmt_usd(value: Optional[int]) -> str:
    """Format USD value with $ and commas. Returns 'N/A' for None."""
    if value is None:
        return 'N/A'
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value/1_000:.1f}k"
    return f"${value}"


def fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return 'N/A'
    return f"{value*100:.1f}%"


# ---------- Section builders ----------

def build_cover_page(data: Dict, styles: Dict) -> List:
    """Build the cover page flowables."""
    flow = []
    flow.append(Spacer(1, 1.5*inch))

    # IP DETECTOR label
    flow.append(Paragraph('IP DETECTOR DOSSIER', styles['cover_meta']))
    flow.append(Spacer(1, 0.4*inch))

    # Concept name
    flow.append(Paragraph(data.get('concept_name', 'UNNAMED CONCEPT'), styles['cover_concept_name']))

    # Input type & date
    input_type = data.get('input_type', 'unknown').upper()
    analysis_date = data.get('analysis_date', datetime.now().strftime('%Y-%m-%d'))
    flow.append(Paragraph(f"Input type: {input_type}", styles['cover_meta']))
    flow.append(Paragraph(f"Analysis date: {analysis_date}", styles['cover_meta']))

    flow.append(Spacer(1, 0.6*inch))

    # Verdict label
    flow.append(Paragraph('VERDICT', styles['verdict_label']))

    # Verdict in huge font
    verdict = data.get('verdict', 'DO NOT FILE').upper()
    if verdict == 'FILE':
        verdict_style = styles['verdict_file']
    elif verdict == 'BORDERLINE':
        verdict_style = styles['verdict_borderline']
    else:  # DO NOT FILE
        verdict_style = styles['verdict_donotfile']
        verdict = 'DO NOT FILE'

    flow.append(Paragraph(verdict, verdict_style))

    # Gold Index
    gold_index = data.get('gold_index', 0)
    flow.append(Spacer(1, 0.3*inch))
    flow.append(Paragraph(f"GOLD INDEX: {gold_index:.1f} / 100", styles['cover_gold_index']))

    # Score bar visualization (simple text)
    scores = data.get('scoring', {})
    score_line = ' / '.join([
        f"Novelty {scores.get('novelty', {}).get('score', 0)}",
        f"Non-Obv {scores.get('non_obviousness', {}).get('score', 0)}",
        f"Industrial {scores.get('industrial_applicability', {}).get('score', 0)}",
        f"Defensibility {scores.get('defensibility', {}).get('score', 0)}",
        f"Market {scores.get('market_value', {}).get('score', 0)}",
    ])
    flow.append(Paragraph(score_line, styles['cover_meta']))

    flow.append(PageBreak())
    return flow


def build_executive_summary(data: Dict, styles: Dict) -> List:
    """Build the one-page executive summary."""
    flow = []
    flow.append(Paragraph('Executive Summary', styles['h1']))

    # Verdict line
    verdict = data.get('verdict', 'DO NOT FILE').upper()
    if verdict != 'FILE' and verdict != 'BORDERLINE':
        verdict = 'DO NOT FILE'
    gold_index = data.get('gold_index', 0)
    flow.append(Paragraph(
        f"<b>Verdict:</b> {verdict} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Gold Index:</b> {gold_index:.1f} / 100",
        styles['body']
    ))

    # Cost & capture
    filing = data.get('filing_cost', {})
    market = data.get('market_projection', {})
    ten_year_cost = filing.get('ten_year_total_usd', 0)
    projected_capture = market.get('projected_capture_usd', 0)
    roi = projected_capture - ten_year_cost

    flow.append(Paragraph(
        f"<b>10-year filing + maintenance cost:</b> {fmt_usd(ten_year_cost)}",
        styles['body']
    ))
    flow.append(Paragraph(
        f"<b>10-year projected capture:</b> {fmt_usd(projected_capture)}",
        styles['body']
    ))
    roi_color = '#0a7a3b' if roi > 0 else '#8b0000'
    flow.append(Paragraph(
        f"<b>10-year net ROI:</b> <font color='{roi_color}'>{fmt_usd(roi)}</font>",
        styles['body']
    ))

    flow.append(Spacer(1, 0.15*inch))

    # Score table
    scores = data.get('scoring', {})
    score_data = [
        ['Dimension', 'Score (0-100)', 'Weight', 'Key evidence'],
    ]
    dimensions = [
        ('Novelty', 'novelty', '25%'),
        ('Non-obviousness', 'non_obviousness', '20%'),
        ('Industrial Applicability', 'industrial_applicability', '10%'),
        ('Defensibility', 'defensibility', '20%'),
        ('Market Value', 'market_value', '25%'),
    ]
    for label, key, weight in dimensions:
        dim_data = scores.get(key, {})
        score = dim_data.get('score', 0)
        evidence = dim_data.get('evidence', 'No evidence recorded.')[:120]
        score_data.append([label, str(score), weight, evidence])

    score_table = Table(score_data, colWidths=[1.6*inch, 1.0*inch, 0.7*inch, 3.3*inch])
    score_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), styles['h3'].fontName, 9),
        ('FONT', (0, 1), (-1, -1), styles['body'].fontName, 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    flow.append(score_table)
    flow.append(Spacer(1, 0.15*inch))

    # Verdict drivers
    drivers = data.get('verdict_drivers', [])
    if drivers:
        flow.append(Paragraph('<b>Verdict drivers:</b>', styles['body']))
        for i, driver in enumerate(drivers, 1):
            flow.append(Paragraph(f"{i}. {driver}", styles['body']))

    return flow


def build_input_classification(data: Dict, styles: Dict) -> List:
    flow = []
    flow.append(Paragraph('1. Input & IP Classification', styles['h1']))

    # Input summary
    flow.append(Paragraph('<b>Input type:</b> ' + data.get('input_type', 'unknown'), styles['body']))
    flow.append(Paragraph('<b>Input summary:</b> ' + data.get('input_summary', 'No summary recorded.'), styles['body']))
    flow.append(Paragraph('<b>User framing (the user\'s own hypothesis, recorded for context only — does not influence scoring):</b> ' + data.get('user_framing', 'Not recorded.'), styles['body']))

    # IP classification
    ip_class = data.get('ip_classification', {})
    flow.append(Paragraph('<b>Primary IP regime:</b> ' + ip_class.get('primary_regime', 'unclassified').replace('_', ' ').title(), styles['body']))
    secondary = ip_class.get('secondary_regimes', [])
    if secondary:
        flow.append(Paragraph('<b>Secondary regimes:</b> ' + ', '.join(r.replace('_', ' ').title() for r in secondary), styles['body']))

    flow.append(Paragraph('<b>Subject-matter eligibility (patent route):</b> ' +
                         ('Eligible' if ip_class.get('subject_matter_eligible') else 'NOT ELIGIBLE'),
                         styles['body']))
    flow.append(Paragraph('<b>Eligibility analysis:</b> ' + ip_class.get('eligibility_analysis', 'Not analyzed.'), styles['body']))
    flow.append(Paragraph('<b>Recommended regime:</b> ' + ip_class.get('recommended_regime', 'No recommendation recorded.'), styles['body']))

    return flow


def build_prior_art(data: Dict, styles: Dict) -> List:
    flow = []
    flow.append(Paragraph('2. Prior-Art Matrix', styles['h1']))

    pa = data.get('prior_art', {})

    flow.append(Paragraph('<b>CPC class:</b> ' + pa.get('cpc_class', 'Not identified'), styles['body']))

    # Keyword pool
    keywords = pa.get('keyword_pool', [])
    if keywords:
        flow.append(Paragraph('<b>Keyword pool used for searches:</b>', styles['body']))
        flow.append(Paragraph(', '.join(keywords), styles['small']))

    # Searches run
    searches = pa.get('searches_run', [])
    if searches:
        flow.append(Paragraph('<b>Searches run:</b>', styles['h3']))
        search_data = [['Source', 'Query', 'Hit count']]
        for s in searches:
            search_data.append([s.get('source', ''), s.get('query', '')[:80], str(s.get('hit_count', ''))])
        search_table = Table(search_data, colWidths=[1.2*inch, 4.5*inch, 0.8*inch])
        search_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), styles['h3'].fontName, 9),
            ('FONT', (0, 1), (-1, -1), styles['body'].fontName, 8.5),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        flow.append(search_table)

    # Top hits
    hits = pa.get('top_hits', [])
    if hits:
        flow.append(Paragraph('<b>Top prior-art hits (sorted by relevance):</b>', styles['h3']))
        for i, hit in enumerate(hits, 1):
            title = hit.get('title', 'Untitled')
            author = hit.get('author_or_assignee', 'Unknown')
            date = hit.get('date', 'No date')
            url = hit.get('url', '')
            note = hit.get('relevance_note', '')
            score = hit.get('relevance_score', 0)
            score_color = '#8b0000' if score >= 70 else ('#b8860b' if score >= 50 else '#555555')
            block = (
                f"<b>{i}. [{score}]</b> <font color='{score_color}'><b>{title}</b></font><br/>"
                f"{author} &middot; {date}<br/>"
                f"<font color='#0066cc'>{url}</font><br/>"
                f"<i>{note}</i>"
            )
            flow.append(Paragraph(block, styles['body']))

    # Counts
    high = pa.get('high_relevance_count', 0)
    mod = pa.get('moderate_relevance_count', 0)
    flow.append(Paragraph(f"<b>High-relevance hits (&ge;70):</b> {high} &nbsp;&nbsp; <b>Moderate-relevance hits (50-69):</b> {mod}", styles['body']))

    summary = pa.get('summary', '')
    if summary:
        flow.append(Paragraph('<b>Summary:</b> ' + summary, styles['body']))

    return flow


def build_market_projection(data: Dict, styles: Dict) -> List:
    flow = []
    flow.append(Paragraph('3. Market Projection', styles['h1']))

    mkt = data.get('market_projection', {})
    flow.append(Paragraph('<b>Relevant market segment:</b> ' + mkt.get('segment', 'Not identified'), styles['body']))

    # Sources
    sources = mkt.get('sources_cited', [])
    if sources:
        flow.append(Paragraph('<b>Market-research sources cited:</b>', styles['h3']))
        for src in sources:
            firm = src.get('firm', '')
            title = src.get('report_title', '')
            year = src.get('year', '')
            url = src.get('url', '')
            flow.append(Paragraph(
                f"&bull; {firm} ({year}). <i>{title}</i>. <font color='#0066cc'>{url}</font>",
                styles['small']
            ))

    # Market size table
    flow.append(Paragraph('<b>Market size trajectory (USD):</b>', styles['h3']))
    market_data = [
        ['Metric', 'Year 0', 'Year 5', 'Year 10'],
        ['TAM', fmt_usd(mkt.get('tam_year_0_usd')),
         fmt_usd(int(mkt.get('tam_year_0_usd', 0) * (1 + mkt.get('cagr', 0))**5)) if mkt.get('tam_year_0_usd') else 'N/A',
         fmt_usd(int(mkt.get('tam_year_0_usd', 0) * (1 + mkt.get('cagr', 0))**10 * mkt.get('disruption_discount_applied', 1))) if mkt.get('tam_year_0_usd') else 'N/A'],
        ['SAM', fmt_usd(mkt.get('sam_year_0_usd')),
         fmt_usd(int(mkt.get('sam_year_0_usd', 0) * (1 + mkt.get('cagr', 0))**5)) if mkt.get('sam_year_0_usd') else 'N/A',
         fmt_usd(int(mkt.get('sam_year_0_usd', 0) * (1 + mkt.get('cagr', 0))**10 * mkt.get('disruption_discount_applied', 1))) if mkt.get('sam_year_0_usd') else 'N/A'],
        ['SOM', fmt_usd(mkt.get('som_year_0_usd')),
         fmt_usd(mkt.get('som_year_5_usd')),
         fmt_usd(mkt.get('som_year_10_usd'))],
    ]
    mkt_table = Table(market_data, colWidths=[1.0*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    mkt_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), styles['h3'].fontName, 9),
        ('FONT', (0, 1), (-1, -1), styles['body'].fontName, 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    flow.append(mkt_table)
    flow.append(Spacer(1, 0.1*inch))

    flow.append(Paragraph(f"<b>CAGR:</b> {fmt_pct(mkt.get('cagr'))} (source: {mkt.get('cagr_source', 'Not cited')})", styles['body']))
    flow.append(Paragraph(f"<b>Disruption discount applied:</b> {mkt.get('disruption_discount_applied', 1):.2f}", styles['body']))
    flow.append(Paragraph(f"<b>Rationale:</b> {mkt.get('disruption_discount_rationale', 'Not provided')}", styles['body']))
    flow.append(Paragraph(f"<b>Capture rate:</b> {fmt_pct(mkt.get('capture_rate'))}", styles['body']))
    flow.append(Paragraph(f"<b>Enforcement probability:</b> {fmt_pct(mkt.get('enforcement_probability'))}", styles['body']))
    flow.append(Paragraph(f"<b>Projected 10-year capture:</b> {fmt_usd(mkt.get('projected_capture_usd'))}", styles['body']))

    confidence = mkt.get('confidence', 'unknown')
    conf_color = {'high': '#0a7a3b', 'medium': '#b8860b', 'low': '#8b0000',
                  'single_source': '#b8860b', 'none': '#8b0000'}.get(confidence, '#555555')
    flow.append(Paragraph(f"<b>Confidence:</b> <font color='{conf_color}'>{confidence.replace('_', ' ').upper()}</font>", styles['body']))

    return flow


def build_filing_cost(data: Dict, styles: Dict) -> List:
    flow = []
    flow.append(Paragraph('4. Filing & Maintenance Cost (10-Year)', styles['h1']))

    fc = data.get('filing_cost', {})
    jurisdictions = fc.get('jurisdictions', [])
    flow.append(Paragraph('<b>Jurisdictions modeled:</b> ' + ', '.join(jurisdictions), styles['body']))

    table_data = fc.get('year_by_year_table', [])
    if table_data:
        # Build header from first row keys (excluding 'year')
        first = table_data[0]
        cols = [k for k in first.keys() if k != 'year']
        header = ['Year'] + [c.upper() for c in cols]
        rows = [header]
        for entry in table_data:
            row = [str(entry.get('year', ''))]
            for c in cols:
                v = entry.get(c, 0)
                row.append(fmt_usd(v) if isinstance(v, (int, float)) else str(v))
            rows.append(row)

        # Add total row
        total_row = ['TOTAL']
        for c in cols:
            total = sum(entry.get(c, 0) for entry in table_data if isinstance(entry.get(c, 0), (int, float)))
            total_row.append(fmt_usd(total))
        rows.append(total_row)

        cost_table = Table(rows, colWidths=[0.6*inch] + [1.0*inch] * len(cols))
        cost_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), styles['h3'].fontName, 9),
            ('FONT', (0, 1), (-1, -2), styles['body'].fontName, 8.5),
            ('FONT', (0, -1), (-1, -1), styles['h3'].fontName, 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        flow.append(cost_table)

    flow.append(Paragraph(f"<b>10-year total cost of ownership:</b> {fmt_usd(fc.get('ten_year_total_usd'))}", styles['body']))

    notes = fc.get('notes', '')
    if notes:
        flow.append(Paragraph(f"<b>Notes:</b> {notes}", styles['small']))

    return flow


def build_scoring_breakdown(data: Dict, styles: Dict) -> List:
    flow = []
    flow.append(Paragraph('5. Scoring Breakdown', styles['h1']))

    scores = data.get('scoring', {})
    dimensions = [
        ('Novelty', 'novelty', '25%'),
        ('Non-obviousness', 'non_obviousness', '20%'),
        ('Industrial Applicability', 'industrial_applicability', '10%'),
        ('Defensibility', 'defensibility', '20%'),
        ('Market Value', 'market_value', '25%'),
    ]

    for label, key, weight in dimensions:
        dim = scores.get(key, {})
        score = dim.get('score', 0)
        evidence = dim.get('evidence', 'No evidence recorded.')
        flow.append(Paragraph(f"<b>{label}</b> — Score: {score}/100 (weight {weight})", styles['h2']))

        # Add dimension-specific fields
        if key == 'novelty':
            hits = dim.get('prior_art_hits', 0)
            flow.append(Paragraph(f"<b>Prior-art hits (relevance &ge;70):</b> {hits}", styles['small']))
        if key == 'market_value':
            net = dim.get('net_value_usd', 0)
            color = '#0a7a3b' if net > 0 else '#8b0000'
            flow.append(Paragraph(f"<b>Net value (capture - cost):</b> <font color='{color}'>{fmt_usd(net)}</font>", styles['small']))

        flow.append(Paragraph(f"<b>Evidence:</b> {evidence}", styles['body']))

    # Gold Index computation
    gold_index = data.get('gold_index', 0)
    flow.append(Paragraph(f"<b>Gold Index = 0.25*Novelty + 0.20*Non-obv + 0.10*Industrial + 0.20*Defensibility + 0.25*Market = {gold_index:.1f} / 100</b>", styles['h2']))

    return flow


def build_verdict_section(data: Dict, styles: Dict) -> List:
    flow = []
    verdict = data.get('verdict', 'DO NOT FILE').upper()
    if verdict not in ('FILE', 'BORDERLINE'):
        verdict = 'DO NOT FILE'

    title = data.get('verdict_section_title', '')
    body_items = data.get('verdict_section_body', [])

    if not title:
        if verdict == 'DO NOT FILE':
            title = 'Why this is a rock, not gold'
        elif verdict == 'BORDERLINE':
            title = 'Conditions that would change this to FILE'
        else:
            title = 'Filing roadmap'

    if verdict == 'DO NOT FILE':
        title_style = styles['verdict_section_title_rock']
    elif verdict == 'BORDERLINE':
        title_style = styles['verdict_section_title_borderline']
    else:
        title_style = styles['verdict_section_title_file']

    flow.append(Paragraph(title, title_style))

    if body_items:
        for i, item in enumerate(body_items, 1):
            flow.append(Paragraph(f"{i}. {item}", styles['body']))
    else:
        # Auto-generate based on verdict drivers
        drivers = data.get('verdict_drivers', [])
        for i, d in enumerate(drivers, 1):
            flow.append(Paragraph(f"{i}. {d}", styles['body']))

    return flow


def build_disclaimer(data: Dict, styles: Dict) -> List:
    flow = []
    flow.append(Spacer(1, 0.3*inch))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    disclaimer = data.get('disclaimer',
        'This dossier is a research artifact produced by an automated analysis workflow. '
        'It is not legal advice. Patent eligibility, novelty, non-obviousness, and infringement '
        'are legal determinations that can only be made by a registered patent attorney after a '
        'full review of the specific facts. Consult qualified counsel before any filing decision.'
    )
    flow.append(Paragraph(disclaimer, styles['disclaimer']))
    return flow


# ---------- Page header/footer ----------

def make_page_decorator(concept_name: str, verdict: str):
    """Return a function that draws the header/footer on each page (except cover)."""
    def decorate(canvas, doc):
        canvas.saveState()
        # Footer: page number + verdict stamp
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(0.75*inch, 0.5*inch, f"IP Detector Dossier - {concept_name[:60]}")
        canvas.drawRightString(letter[0] - 0.75*inch, 0.5*inch, f"Page {doc.page}")
        # Verdict stamp in top-right
        if doc.page > 1:
            canvas.setFont('Helvetica-Bold', 8)
            color_map = {'FILE': colors.HexColor('#0a7a3b'),
                         'BORDERLINE': colors.HexColor('#b8860b'),
                         'DO NOT FILE': colors.HexColor('#8b0000')}
            canvas.setFillColor(color_map.get(verdict, colors.HexColor('#8b0000')))
            canvas.drawRightString(letter[0] - 0.75*inch, letter[1] - 0.5*inch, verdict)
        canvas.restoreState()
    return decorate


# ---------- Main ----------

def build_pdf(data: Dict, output_path: str):
    """Build the PDF dossier from the analysis data."""
    body_font, heading_font = register_fonts()
    styles = make_styles(body_font, heading_font)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        title=f"IP Detector Dossier - {data.get('concept_name', 'Concept')}",
        author='IP Detector Skill',
    )

    story = []

    # Cover page (no header/footer)
    story.extend(build_cover_page(data, styles))

    # Body sections (with header/footer)
    story.extend(build_executive_summary(data, styles))
    story.extend(build_input_classification(data, styles))
    story.extend(build_prior_art(data, styles))
    story.extend(build_market_projection(data, styles))
    story.extend(build_filing_cost(data, styles))
    story.extend(build_scoring_breakdown(data, styles))
    story.extend(build_verdict_section(data, styles))
    story.extend(build_disclaimer(data, styles))

    verdict = data.get('verdict', 'DO NOT FILE').upper()
    if verdict not in ('FILE', 'BORDERLINE'):
        verdict = 'DO NOT FILE'

    doc.build(
        story,
        onFirstPage=lambda c, d: None,  # no decoration on cover
        onLaterPages=make_page_decorator(data.get('concept_name', ''), verdict)
    )


def main():
    parser = argparse.ArgumentParser(description='Generate an IP Detector PDF dossier from analysis JSON.')
    parser.add_argument('--data', required=True, help='Path to analysis JSON file')
    parser.add_argument('--output', required=True, help='Output PDF path')
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"ERROR: input file {args.data} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(args.data) as f:
        data = json.load(f)

    # Validate minimum required fields
    required = ['concept_name', 'verdict', 'gold_index']
    for field in required:
        if field not in data:
            print(f"WARNING: required field '{field}' missing from analysis JSON", file=sys.stderr)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    build_pdf(data, args.output)
    print(f"Wrote dossier to {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
