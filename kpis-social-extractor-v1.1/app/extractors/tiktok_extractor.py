import logging
from typing import Dict, Any, Optional

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class TikTokExtractor(BaseExtractor):
    def extract_followers(self, url: str) -> Optional[int]:
        logger.warning(f"TikTok extraction is complex and not implemented in this version.")
        return None

    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        logger.warning(f"TikTok extraction is complex and not implemented in this version.")
        return None