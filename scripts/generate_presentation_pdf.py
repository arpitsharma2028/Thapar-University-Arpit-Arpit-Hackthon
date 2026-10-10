"""
FinSight AI — Presentation Deck Generator
Generates a polished, professional 7-slide presentation in docs/presentation.pdf
using ReportLab, styled consistently with the FinSight AI terminal theme.
"""

import os
import sys
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Ensure UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
PDF_PATH = os.path.join(DOCS_DIR, "presentation.pdf")
ARCH_PNG = os.path.join(DOCS_DIR, "architecture.png")

# Page Dimensions (Landscape Letter: 11 x 8.5 inches = 792 x 612 pt)
PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to add headers, footers, slide numbers, and dark branding background.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        # Background
        self.setFillColor(colors.HexColor('#0a0e17'))
        self.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

        # Header accent line (slides > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor('#223048'))
            self.setLineWidth(1)
            self.line(40, PAGE_HEIGHT - 45, PAGE_WIDTH - 40, PAGE_HEIGHT - 45)

            # Header watermark text
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor('#38bdf8'))
            self.drawString(40, PAGE_HEIGHT - 35, "FINSIGHT AI — S&P GLOBAL & CRISIL CAMPUS HACKATHON 2026")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor('#94a3b8'))
            self.drawRightString(PAGE_WIDTH - 40, PAGE_HEIGHT - 35, "THAPAR INSTITUTE OF ENGINEERING & TECHNOLOGY")

        # Footer
        self.setStrokeColor(colors.HexColor('#223048'))
        self.setLineWidth(1)
        self.line(40, 35, PAGE_WIDTH - 40, 35)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(40, 22, "FINSIGHT AI • S&P GLOBAL & CRISIL CAMPUS HACKATHON 2026 SUBMISSION")
        self.drawRightString(PAGE_WIDTH - 40, 22, f"Slide {self._pageNumber} of {total_pages}")
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=55,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_hero = ParagraphStyle(
        'TitleHero',
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor('#ffffff'),
        alignment=0,
        spaceAfter=12
    )

    subtitle_hero = ParagraphStyle(
        'SubtitleHero',
        fontName='Helvetica',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#38bdf8'),
        spaceAfter=24
    )

    slide_title = ParagraphStyle(
        'SlideTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#ffffff'),
        spaceAfter=4
    )

    slide_subtitle = ParagraphStyle(
        'SlideSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#94a3b8'),
        spaceAfter=14
    )

    body_text = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#cbd5e1')
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#38bdf8')
    )

    story = []

    # =========================================================================
    # SLIDE 1 — TITLE SLIDE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("FinSight AI", title_hero))
    story.append(Paragraph("Market & Portfolio Risk Intelligence Platform", subtitle_hero))
    
    # Metadata Box
    meta_data = [
        [Paragraph("<b>Candidate Name:</b>", body_text), Paragraph("Arpit Sharma", body_text)],
        [Paragraph("<b>College Email ID:</b>", body_text), Paragraph("asharma32_be22@thapar.edu (GitHub: arpitsharma2028)", body_text)],
        [Paragraph("<b>College / Campus:</b>", body_text), Paragraph("Thapar Institute of Engineering and Technology (TIET)", body_text)],
        [Paragraph("<b>Hackathon:</b>", body_text), Paragraph("S&P Global & CRISIL Campus Hackathon 2026", body_text)],
        [Paragraph("<b>Core Modules:</b>", body_text), Paragraph("NLP Risk Engine • Module A Rebalancer • Module B Stress Testing • Monte Carlo", body_text)],
        [Paragraph("<b>Architecture:</b>", body_text), Paragraph("FastAPI • scikit-learn • yfinance • SQLite (WAL) • React/Vite Dashboard", body_text)]
    ]
    t1 = Table(meta_data, colWidths=[150, 450])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#151e32')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#223048')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1f293d')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t1)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2 — PROBLEM STATEMENT & APPROACH
    # =========================================================================
    story.append(Paragraph("Problem Statement & Solution Approach", slide_title))
    story.append(Paragraph("Navigating information latency and nonlinear risk cascades in quantitative risk management", slide_subtitle))

    p2_data = [
        [
            Paragraph("<b>The Business Problem</b>", bold_label),
            Paragraph("<b>Why Existing Approaches Fail</b>", bold_label),
            Paragraph("<b>The FinSight AI Approach</b>", bold_label)
        ],
        [
            Paragraph(
                "Financial institutions, wholesale banks, and index funds face rapid market regime shifts. "
                "Unstructured text from breaking financial wire news, regulatory filings, and social media momentum "
                "contains actionable risk signals hours before they reflect in historical volatility models.",
                body_text
            ),
            Paragraph(
                "• <b>Static Keyword Rules:</b> Fragile to financial slang, negations, and context.<br/>"
                "• <b>Siloed Risk Systems:</b> Text signals rarely connect to live algorithmic index weights.<br/>"
                "• <b>Compute Heavy LLMs:</b> Slow, expensive, uncalibrated for low-latency quantitative execution on Windows laptops.",
                body_text
            ),
            Paragraph(
                "• <b>Unified CPU-Optimized NLP Engine:</b> Multi-task continuous sentiment, 9-class event taxonomy, entity extraction, and calibrated impact.<br/>"
                "• <b>Module A — Tactical Rebalancer:</b> Clamped weight optimization formula.<br/>"
                "• <b>Module B — Wholesale Stress Testing:</b> Scenario shock propagation.",
                body_text
            )
        ]
    ]
    t2 = Table(p2_data, colWidths=[230, 240, 240])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#151e32')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#223048')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1f293d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3 — SYSTEM DESIGN & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("System Architecture & Data Pipeline", slide_title))
    story.append(Paragraph("End-to-end data pipeline from multi-source ingestion to interactive terminal execution", slide_subtitle))

    if os.path.exists(ARCH_PNG):
        story.append(Image(ARCH_PNG, width=700, height=360))
    else:
        story.append(Paragraph("Architecture Diagram (Generated in docs/architecture.png)", body_text))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4 — IMPLEMENTATION HIGHLIGHTS
    # =========================================================================
    story.append(Paragraph("Technical Implementation Highlights", slide_title))
    story.append(Paragraph("Core quantitative algorithms, machine learning pipelines, and software engineering", slide_subtitle))

    p4_data = [
        [
            Paragraph("<b>Unified NLP Risk Engine</b>", bold_label),
            Paragraph("<b>Module A: Dynamic Rebalancer</b>", bold_label)
        ],
        [
            Paragraph(
                "• <b>Sentiment Polarity:</b> Pretrained FinBERT (ProsusAI) + Loughran-McDonald financial lexicon with 3-token negation window in [-1.0, +1.0].<br/>"
                "• <b>Event Classification:</b> 9 classes (Geopolitical, Macro, Credit, Earnings, Regulatory, etc.) with evidence gating (no false Earnings labels).<br/>"
                "• <b>Impact Severity Scorer:</b> Active Ridge regression pipeline blended with structured category importance, strictly bounded in [1.0, 10.0].<br/>"
                "• <b>Entity Extraction:</b> Evidence-based cashtag and company extraction (never assigns SPY to arbitrary text).",
                body_text
            ),
            Paragraph(
                "• <b>Mark-to-Market Accounting:</b> Portfolio value evolves via realistic asset price returns rather than artificial multipliers.<br/>"
                "• <b>Bounded Simplex Projection:</b> Strictly guarantees &sum; w<sub>i</sub> &equiv; 100.0% with [1.0%, 25.0%] floors and ceilings.<br/>"
                "• <b>Quantitative Controls:</b> 15% turnover limit, 5 bps transaction costs, and equal-weight benchmark alpha comparison.<br/>"
                "• <b>Audit Trail:</b> Full regulatory transaction log with old weights, new weights, and deltas.",
                body_text
            )
        ],
        [
            Paragraph("<b>Module B: Wholesale Stress Testing</b>", bold_label),
            Paragraph("<b>Production-Grade Engineering</b>", bold_label)
        ],
        [
            Paragraph(
                "• <b>Multi-Asset Portfolio:</b> $50.0M wholesale banking book across Equities ($22.5M), Bonds ($15.0M), Derivatives ($7.5M), Cash ($5.0M).<br/>"
                "• <b>Explicit Trigger Logic:</b> Automatic scenario execution when NLP impact score &gt; 7.0 with deduplication protection.<br/>"
                "• <b>Asset-Specific Shocks:</b> Equity price shocks, duration-based bond yield shifts, derivative volatility skew, zero shock on cash.<br/>"
                "• <b>Reconciled Loss Settings:</b> -$4.69M (-9.38%) at 1.0x baseline, -$7.50M (-15.0%) at 1.6x amplified shock.",
                body_text
            ),
            Paragraph(
                "• <b>FastAPI Backend:</b> Clean architecture, OpenAPI /docs, strict CORS, rate limiting, and request correlation IDs.<br/>"
                "• <b>Public RSS Ingestion:</b> Live unauthenticated WSJ Markets RSS feed with offline synthetic replay fallback.<br/>"
                "• <b>React + Vite Frontend:</b> Liquid Glass dark UI with Recharts, interactive text analysis sandbox, and Monte Carlo forecasts.<br/>"
                "• <b>40 Pytest Tests:</b> 40 unit and integration tests passing cleanly with isolated temporary SQLite fixtures.",
                body_text
            )
        ]
    ]
    t4 = Table(p4_data, colWidths=[355, 355])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#151e32')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#223048')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1f293d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t4)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5 — KEY RESULTS & DEMO PERFORMANCE
    # =========================================================================
    story.append(Paragraph("Key Results & Empirical Validation", slide_title))
    story.append(Paragraph("Live benchmark performance, execution latency, and deterministic verification", slide_subtitle))

    p5_data = [
        [
            Paragraph("<b>Metric Dimension</b>", bold_label),
            Paragraph("<b>Target Requirement</b>", bold_label),
            Paragraph("<b>FinSight AI Verified Output</b>", bold_label),
            Paragraph("<b>Status</b>", bold_label)
        ],
        [
            Paragraph("NLP Pipeline Latency", body_text),
            Paragraph("< 200 ms on Windows laptop CPU", body_text),
            Paragraph("<b>29.0 ms median warm inference</b> (FinBERT + Loughran-McDonald, P95 46.2 ms)", body_text),
            Paragraph("<font color='#34d399'>EXCEEDED</font>", body_text)
        ],
        [
            Paragraph("Sentiment Benchmarks", body_text),
            Paragraph("Dual evaluation (In-domain + Generalization)", body_text),
            Paragraph("<b>PhraseBank: 89.0% Acc / 88.7% F1</b> • <b>Unseen News: 69.3% Acc / 68.6% F1</b> (vs 42.7% baseline)", body_text),
            Paragraph("<font color='#34d399'>VERIFIED</font>", body_text)
        ],
        [
            Paragraph("Index Rebalancing (Module A)", body_text),
            Paragraph("10–20 stock portfolio rebalance", body_text),
            Paragraph("<b>16 Public tickers</b>, mark-to-market, simplex bounded [1%, 25%], 15% turnover cap", body_text),
            Paragraph("<font color='#34d399'>VERIFIED</font>", body_text)
        ],
        [
            Paragraph("Stress Testing (Module B)", body_text),
            Paragraph("Wholesale portfolio shock &gt; 7.0", body_text),
            Paragraph("<b>$50M book</b>: -$4.69M (-9.38%) at 1.0x baseline, -$7.50M (-15.0%) at 1.6x shock", body_text),
            Paragraph("<font color='#34d399'>VERIFIED</font>", body_text)
        ],
        [
            Paragraph("Automated Test Suite", body_text),
            Paragraph("Unit and integration tests", body_text),
            Paragraph("<b>40 / 40 Pytest test cases passing</b> cleanly with isolated DB fixtures", body_text),
            Paragraph("<font color='#34d399'>100% PASS</font>", body_text)
        ],
        [
            Paragraph("Live Ingestion & Offline Core", body_text),
            Paragraph("Public data + offline reliability", body_text),
            Paragraph("<b>WSJ Markets RSS live ingestion</b> + deterministic offline fallback", body_text),
            Paragraph("<font color='#34d399'>VERIFIED</font>", body_text)
        ]
    ]
    t5 = Table(p5_data, colWidths=[160, 180, 270, 90])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#151e32')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#223048')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1f293d')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t5)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6 — DOMAIN IMPACT & BUSINESS VALUE
    # =========================================================================
    story.append(Paragraph("Domain Impact & Commercial Value for S&P Global & CRISIL", slide_title))
    story.append(Paragraph("Transforming real-time market text intelligence into institutional capital preservation", slide_subtitle))

    p6_data = [
        [
            Paragraph("<b>1. Quantitative Asset Management</b>", bold_label),
            Paragraph("<b>2. Wholesale Credit Surveillance</b>", bold_label)
        ],
        [
            Paragraph(
                "• Replaces slow manual news desk monitoring with continuous algorithmic signal synthesis.<br/>"
                "• Mitigates portfolio drawdown by dampening high-risk exposure before quarterly reports.<br/>"
                "• Provides clear audit trails for investment committees and risk compliance officers.",
                body_text
            ),
            Paragraph(
                "• Early warning indicator for commercial loan syndicates and corporate bond desks.<br/>"
                "• Automatically propagates debt default rumors and regulatory probes into portfolio VaR and capital buffers.<br/>"
                "• Aligns with CRISIL credit rating surveillance methodologies.",
                body_text
            )
        ],
        [
            Paragraph("<b>3. Macro & Geopolitical Stress Testing</b>", bold_label),
            Paragraph("<b>4. S&P Market Intelligence Integration</b>", bold_label)
        ],
        [
            Paragraph(
                "• Enhances regulatory stress test submissions (CCAR / EBA / Basel III guidelines).<br/>"
                "• Enables risk managers to simulate instantaneous maritime, tariff, or energy shocks and assess multi-asset loss distributions in seconds.",
                body_text
            ),
            Paragraph(
                "• Designed with a clean modular ingestion layer ready to connect to public S&P Global Market Intelligence API endpoints, Capital IQ, or live RSS feeds.<br/>"
                "• Demonstrates high-value enterprise workflow automation for Tier-1 investment banks.",
                body_text
            )
        ]
    ]
    t6 = Table(p6_data, colWidths=[355, 355])
    t6.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#151e32')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#223048')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1f293d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t6)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7 — LIMITATIONS & FUTURE ROADMAP
    # =========================================================================
    story.append(Paragraph("Prototype Limitations & Future Roadmap", slide_title))
    story.append(Paragraph("Honest engineering appraisal and scalable production evolutionary steps", slide_subtitle))

    p7_data = [
        [
            Paragraph("<b>Current Prototype Scope & Assumptions</b>", bold_label),
            Paragraph("<b>Production Roadmap & Enhancements</b>", bold_label)
        ],
        [
            Paragraph(
                "• <b>Synthetic & Public Demo Datasets:</b> Deterministic seed used to guarantee zero-configuration demo reliability without external API quotas.<br/>"
                "• <b>Market Impact Simulation:</b> Price adjustments use simplified beta and sentiment multiplier rather than a live order book matching engine.<br/>"
                "• <b>Transaction Costs:</b> Rebalance formula currently operates with zero slippage and flat transaction fees.<br/>"
                "• <b>Lightweight CPU NLP:</b> Tuned for high speed (<20ms) rather than deep multi-page regulatory PDF document summarization.",
                body_text
            ),
            Paragraph(
                "• <b>Live Feed Adapters:</b> Plug-and-play WebSocket connectors for Bloomberg B-PIPE, Refinitiv, and S&P Global real-time feeds.<br/>"
                "• <b>Quadratic Portfolio Optimization:</b> Integrate CVXPY Markowitz Mean-Variance optimizer with turnover constraints and transaction fee matrices.<br/>"
                "• <b>Quantized Local LLM Option:</b> Optional 4-bit quantized Mistral-7B / LLaMA-3 adapter for automated analyst commentary generation.<br/>"
                "• <b>Enterprise RBAC & SSO:</b> Multi-tenant compliance with role-based audit trail export to S3/Snowflake.",
                body_text
            )
        ]
    ]
    t7 = Table(p7_data, colWidths=[355, 355])
    t7.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#151e32')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#223048')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1f293d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t7)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated {PDF_PATH} successfully!")

if __name__ == "__main__":
    build_pdf()
