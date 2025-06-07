import logging
from typing import Dict, Any, Optional

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class LinkedInExtractor(BaseExtractor):
    async def extract_followers(self, url: str) -> Optional[int]:
        logger.warning(f"LinkedIn extraction is not implemented in this version.")
        return None

    async def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        logger.warning(f"LinkedIn engagement extraction not implemented in this version.")
        return None