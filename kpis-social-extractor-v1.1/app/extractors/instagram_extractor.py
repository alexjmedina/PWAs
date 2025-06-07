import logging
from typing import Dict, Any, Optional

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class InstagramExtractor(BaseExtractor):
    async def extract_followers(self, url: str) -> Optional[int]:
        logger.warning(f"Instagram extraction is not fully implemented in this version.")
        return None

    async def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        logger.warning(f"Instagram engagement extraction not fully implemented in this version.")
        return None