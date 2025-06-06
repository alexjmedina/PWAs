# kpis-social-extractor/app/extractors/facebook_extractor.py
import logging
import requests
from typing import Dict, Any, Optional

from app.extractors.base_extractor import BaseExtractor
from app.utils.human_simulation import HumanSimulation # Para scraping fallback
from fake_useragent import UserAgent # Para scraping fallback
# Quita los imports de Playwright si decides eliminar el scraping completamente para este extractor
from playwright.sync_api import sync_playwright, Page, Browser


logger = logging.getLogger(__name__)

class FacebookExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.access_token = self.config.META_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v19.0" # Usa la versión más reciente que soporte tu token
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()

    def _extract_page_id_from_url(self, url: str) -> Optional[str]:
        try:
            # Intenta extraer la parte que parece ser el ID o nombre de usuario de la página
            # Esto es una simplificación; una solución más robusta podría necesitar la API de búsqueda
            path_parts = url.strip().split('?')[0].split('/')
            # A menudo es el último elemento, o el penúltimo si la URL termina con '/'
            page_id = path_parts[-1] if path_parts[-1] else path_parts[-2]
            if page_id.lower() == 'profile.php': # Maneja URLs con profile.php?id=NUMERO
                query_params = url.split('?')[-1]
                for param in query_params.split('&'):
                    if param.startswith('id='):
                        return param.split('=')[-1]
            return page_id
        except Exception as e:
            logger.error(f"Error al extraer page_id de la URL '{url}': {e}")
            return None

    def _extract_followers_via_api(self, page_id: str) -> Optional[int]:
        if not self.access_token:
            logger.warning("Facebook API: Token de acceso de Meta no disponible.")
            return None

        api_url = f"{self.base_url}/{page_id}"
        params = {"fields": "fan_count", "access_token": self.access_token} # Usar self.access_token

        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "fan_count" in data:
                logger.info(f"Seguidores de Facebook extraídos vía API para '{page_id}': {data['fan_count']}")
                return data["fan_count"]
            else:
                logger.warning(f"Campo 'fan_count' no encontrado en la respuesta de la API para la página {page_id}. Respuesta: {data}")
                return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP en la API de Facebook al extraer seguidores para '{page_id}': {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            logger.error(f"Error de red en la API de Facebook al extraer seguidores para '{page_id}': {e}")
        except Exception as e:
            logger.error(f"Error inesperado al extraer seguidores vía API para '{page_id}': {e}")
        return None

    def _extract_engagement_via_api(self, page_id: str) -> Optional[Dict[str, Any]]:
        if not self.access_token:
            logger.warning("Facebook API: Token de acceso de Meta no disponible.")
            return None

        api_url = f"{self.base_url}/{page_id}/posts"
        params = {
            "fields": "id,likes.summary(true),comments.summary(true),shares",
            "limit": 10, # Analizar los últimos 10 posts
            "access_token": self.access_token # Usar self.access_token
        }
        try:
            response = requests.get(api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or not data["data"]:
                logger.warning(f"No se encontraron posts en la respuesta de la API para la página {page_id}.")
                return {"posts": 0, "avg_likes": 0, "avg_comments": 0, "avg_shares": 0, "total_engagement": 0}

            posts_data = data["data"]
            total_likes = 0
            total_comments = 0
            total_shares = 0
            post_count = len(posts_data)

            for post in posts_data:
                total_likes += post.get("likes", {}).get("summary", {}).get("total_count", 0)
                total_comments += post.get("comments", {}).get("summary", {}).get("total_count", 0)
                total_shares += post.get("shares", {}).get("count", 0)
            
            engagement_metrics = {
                "posts": post_count,
                "avg_likes": round(total_likes / post_count) if post_count > 0 else 0,
                "avg_comments": round(total_comments / post_count) if post_count > 0 else 0,
                "avg_shares": round(total_shares / post_count) if post_count > 0 else 0,
            }
            engagement_metrics["total_engagement"] = engagement_metrics["avg_likes"] + engagement_metrics["avg_comments"] + engagement_metrics["avg_shares"]
            logger.info(f"Engagement de Facebook extraído vía API para '{page_id}': {engagement_metrics}")
            return engagement_metrics

        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP en la API de Facebook al extraer engagement para '{page_id}': {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            logger.error(f"Error de red en la API de Facebook al extraer engagement para '{page_id}': {e}")
        except Exception as e:
            logger.error(f"Error inesperado al extraer engagement vía API para '{page_id}': {e}")
        return None

    def extract_followers(self, url: str) -> Optional[int]:
        page_id = self._extract_page_id_from_url(url)
        if not page_id:
            logger.error(f"No se pudo determinar el Page ID de Facebook desde la URL: {url}")
            return self._extract_followers_via_scraping(url) # Fallback a scraping si falla la extracción de ID

        followers = self._extract_followers_via_api(page_id)
        if followers is not None:
            return followers
        
        logger.warning(f"Fallo en la extracción de seguidores de Facebook vía API para {page_id}, usando fallback a scraping.")
        return self._extract_followers_via_scraping(url)

    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        page_id = self._extract_page_id_from_url(url)
        if not page_id:
            logger.error(f"No se pudo determinar el Page ID de Facebook desde la URL: {url}")
            return self._extract_engagement_via_scraping(url)

        engagement = self._extract_engagement_via_api(page_id)
        if engagement is not None:
            return engagement
            
        logger.warning(f"Fallo en la extracción de engagement de Facebook vía API para {page_id}, usando fallback a scraping.")
        return self._extract_engagement_via_scraping(url)
        
    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        logger.info(f"Fallback: Intentando scraping de seguidores de Facebook para {url}")
        # Aquí puedes poner tu lógica de scraping con Playwright que tenías
        # ...
        return None # Placeholder si no se implementa el scraping

    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Fallback: Intentando scraping de engagement de Facebook para {url}")
        # Aquí puedes poner tu lógica de scraping con Playwright que tenías
        # ...
        return None # Placeholder