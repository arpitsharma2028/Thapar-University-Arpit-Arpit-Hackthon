"""
FinSight AI — Architecture Diagram Generator
Generates high-resolution architecture visualization for docs/architecture.png
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# UTF-8 stdout configuration
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)
OUT_PATH = os.path.join(DOCS_DIR, "architecture.png")

def create_diagram():
    fig, ax = plt.subplots(figsize=(16, 11), dpi=200)
    fig.patch.set_facecolor('#0a0e17')
    ax.set_facecolor('#0a0e17')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Title & Header
    ax.text(8, 10.4, "FinSight AI — Market & Portfolio Risk Intelligence Architecture", 
            ha='center', va='center', color='#ffffff', fontsize=18, fontweight='bold', fontfamily='sans-serif')
    ax.text(8, 9.95, "S&P Global & CRISIL Campus Hackathon 2026 • End-to-End System Blueprint", 
            ha='center', va='center', color='#38bdf8', fontsize=11, fontfamily='sans-serif')

    def draw_box(x, y, w, h, bg, border, title, subtitle=None, title_color='#ffffff', icon=""):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.25", 
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, ha='center', va='center', 
                    color=title_color, fontsize=10, fontweight='bold')
            ax.text(x + w/2, y + h*0.32, subtitle, ha='center', va='center', 
                    color='#94a3b8', fontsize=7.5)
        else:
            ax.text(x + w/2, y + h/2, title, ha='center', va='center', 
                    color=title_color, fontsize=9.5, fontweight='bold')

    def draw_arrow(x1, y1, x2, y2, color='#38bdf8', style='->'):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=2, mutation_scale=15))

    # Layer 1: Data Sources
    ax.text(1.2, 8.8, "1. INGESTION SOURCES", color='#94a3b8', fontsize=9, fontweight='bold')
    draw_box(0.5, 7.3, 3.2, 1.2, '#151e32', '#3b82f6', "Public Market News Wire", "WSJ Markets RSS (Live) & News (CSV)", '#60a5fa')
    draw_box(0.5, 5.8, 3.2, 1.2, '#151e32', '#8b5cf6', "Social Momentum Feeds", "Public Forum & Cashtag Stream (CSV)", '#c084fc')

    # Ingestion & Preprocessing
    draw_arrow(3.7, 7.9, 4.6, 7.3)
    draw_arrow(3.7, 6.4, 4.6, 6.9)

    ax.text(5.9, 8.8, "2. PREPROCESSING & NORMALIZATION", color='#94a3b8', fontsize=9, fontweight='bold')
    draw_box(4.6, 6.2, 2.6, 1.8, '#0f172a', '#223048', "NLP Ingestion Layer", "Regex Cleaner • Cashtag Parser\nFinancial Stopwords • XML Normalizer")

    # Layer 2: Unified NLP Risk Engine
    draw_arrow(7.2, 7.1, 8.2, 7.1)
    ax.text(10.5, 8.8, "3. UNIFIED AI / NLP RISK ENGINE", color='#38bdf8', fontsize=10, fontweight='bold')
    
    # Large engine container
    engine_rect = patches.FancyBboxPatch((8.2, 4.8), 7.2, 3.7, boxstyle="round,pad=0.15,rounding_size=0.3",
                                         facecolor='#151e32', edgecolor='#38bdf8', linewidth=2)
    ax.add_patch(engine_rect)

    # 4 sub-modules inside engine
    draw_box(8.5, 6.8, 3.2, 1.3, '#1e293b', '#10b981', "Sentiment Polarity Engine", "Continuous [-1.0 to +1.0]\nProsusAI/FinBERT + Loughran", '#34d399')
    draw_box(12.0, 6.8, 3.1, 1.3, '#1e293b', '#f59e0b', "Event Classifier (9 Classes)", "Evidence-Gated Taxonomy\nNo Arbitrary SPY Defaults", '#fcd34d')
    draw_box(8.5, 5.2, 3.2, 1.3, '#1e293b', '#ef4444', "Impact Severity Scorer", "Calibrated [1.0 to 10.0]\nActive Ridge Regressor Pipeline", '#f87171')
    draw_box(12.0, 5.2, 3.1, 1.3, '#1e293b', '#06b6d4', "Entity & Sector Extractor", "16 Index Tickers + Sector Mapping\nEvidence-Based Cashtag Matching", '#67e8f9')

    # Layer 3: Persistence & API
    draw_arrow(11.8, 4.8, 11.8, 3.9)
    draw_box(9.2, 2.9, 5.2, 1.0, '#0f172a', '#3b82f6', "Structured Risk Signal Store (SQLite WAL)", "events • portfolio_positions • rebalance_history • stress_tests", '#38bdf8')

    draw_arrow(9.2, 3.4, 7.6, 3.4)
    draw_box(4.6, 2.8, 3.0, 1.2, '#151e32', '#22c55e', "FastAPI Backend Service", "REST API • OpenAPI /docs\nPydantic Validation Models", '#4ade80')

    # Layer 4: React UI
    draw_arrow(4.6, 3.4, 3.4, 3.4)
    draw_box(0.5, 2.7, 2.9, 1.4, '#151e32', '#60a5fa', "React + Vite Dashboard", "Tailored Institutional Terminal\nRecharts • Lucide • Glassmorphism", '#93c5fd')

    # Downstream Modules
    draw_arrow(6.1, 2.8, 6.1, 2.0)
    
    ax.text(8.0, 2.1, "4. DOWNSTREAM EXECUTION MODULES", color='#f59e0b', fontsize=10, fontweight='bold')
    draw_box(1.5, 0.4, 6.2, 1.4, '#151e32', '#3b82f6', 
             "Module A: Tactical High-Frequency Rebalancer", 
             "16-Asset Index • new_w = clamp(old_w + λ*sent*(imp/10))\nNormalized Σw=100% • Min/Max Floor & Cap • Audit History", '#60a5fa')
    
    draw_box(8.3, 0.4, 6.5, 1.4, '#151e32', '#ef4444', 
             "Module B: Strategic Wholesale Stress Testing", 
             "$50M Wholesale Multi-Asset Book (Equities, Bonds, Derivs, Cash)\nShocks >= 7.0 • Scenario Simulations • Asset & Sector Breakdown", '#f87171')

    # Draw connection lines from API to modules
    draw_arrow(4.6, 1.8, 4.6, 1.8)
    draw_arrow(6.1, 2.8, 11.5, 1.8)

    plt.tight_layout()
    plt.savefig(OUT_PATH, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated architecture diagram at {OUT_PATH}")

if __name__ == "__main__":
    create_diagram()
