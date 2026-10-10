"""
FinSight AI — Public Financial News Ingestion Service
Fetches real, unauthenticated public financial RSS feeds (e.g. Wall Street Journal Markets / MarketWatch),
normalizes incoming records into the standard risk event schema, processes them through the
Unified NLP Risk Engine, and persists structured events into SQLite.

Features:
- Dual endpoint fallback (WSJ Markets RSS + MarketWatch Headlines).
- Timeout protection (5s) and comprehensive network exception handling.
- XML entity cleansing and duplication prevention.
- Seamless offline mode: returns status metadata without interrupting core application workflows.
- Explicit attribution and data-source labeling (distinguishes 'Live RSS' from synthetic simulation).
"""

import re
import logging
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.repositories.event_repository import EventRepository
from backend.ml.nlp_engine import get_risk_engine, UnifiedRiskEngine

logger = logging.getLogger("finsight.ingestion")

RSS_FEEDS = [
    {
        "name": "Wall Street Journal Markets",
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "source_label": "WSJ Markets Live RSS"
    },
    {
        "name": "MarketWatch Realtime",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
        "source_label": "MarketWatch RSS Feed"
    }
]

class IngestionService:
    def __init__(
        self,
        event_repo: Optional[EventRepository] = None,
        risk_engine: Optional[UnifiedRiskEngine] = None
    ):
        self.event_repo = event_repo or EventRepository()
        self.risk_engine = risk_engine or get_risk_engine()

    def fetch_and_ingest_rss(self, max_items: int = 10) -> Dict[str, Any]:
        """
        Polls genuine public financial RSS feeds, normalizes headlines,
        processes signals through the NLP Risk Engine, and stores new events.
        """
        ingested_events: List[Dict[str, Any]] = []
        errors: List[str] = []
        source_used = None

        for feed_cfg in RSS_FEEDS:
            feed_url = feed_cfg["url"]
            source_label = feed_cfg["source_label"]
            try:
                req = urllib.request.Request(
                    feed_url,
                    headers={
                        "User-Agent": "FinSight-AI/1.1 (Academic Financial Risk Intelligence Prototype; Python/urllib)"
                    }
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    if resp.status != 200:
                        errors.append(f"{feed_cfg['name']} returned HTTP {resp.status}")
                        continue
                    xml_bytes = resp.read()

                tree = ET.fromstring(xml_bytes)
                items = tree.findall(".//item")
                if not items:
                    continue

                source_used = feed_cfg["name"]

                for item in items[:max_items]:
                    title_elem = item.find("title")
                    desc_elem = item.find("description")
                    pubdate_elem = item.find("pubDate")

                    headline = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                    description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

                    # Clean any raw HTML tags from RSS description
                    description_clean = re.sub(r'<[^>]+>', '', description).strip()
                    full_text = f"{headline}. {description_clean}" if description_clean else headline

                    if not headline or len(headline) < 5:
                        continue

                    # Process via NLP engine
                    signal = self.risk_engine.process_text(
                        text=full_text,
                        headline=headline,
                        source=source_label,
                        source_type="Live RSS"
                    )

                    # Deduplication check: verify if headline already present in recent events
                    existing = self.event_repo.get_events(search=headline[:40], limit=1)
                    if existing and existing.get("total", 0) > 0:
                        continue

                    import random
                    event_id = f"RSS-{random.randint(10000, 99999)}"
                    signal["event_id"] = event_id

                    # Record publication timestamp if present
                    if pubdate_elem is not None and pubdate_elem.text:
                        signal["source_timestamp"] = pubdate_elem.text.strip()

                    self.event_repo.insert_event(signal)
                    ingested_events.append(signal)

                if ingested_events:
                    break

            except Exception as exc:
                logger.warning(f"Failed to fetch public feed {feed_cfg['name']}: {exc}")
                errors.append(f"{feed_cfg['name']}: {str(exc)}")

        return {
            "status": "success" if ingested_events else ("offline" if errors else "empty"),
            "items_ingested": len(ingested_events),
            "source_used": source_used or "None (Offline / Fallback)",
            "events": ingested_events,
            "errors": errors
        }
