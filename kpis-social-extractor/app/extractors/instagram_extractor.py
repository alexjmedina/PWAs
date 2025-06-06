# kpis-social-extractor/app/extractors/instagram_extractor.py
import logging
import requests
from typing import Dict, Any, Optional
from app.extractors.base_extractor import BaseExtractor
from app.utils.human_simulation import HumanSimulation # Para scraping fallback
from fake_useragent import UserAgent # Para scraping fallback
# Quita los imports de Playwright si decides eliminar el scraping completamente para este extractor
from playwright.sync_api import sync_playwright, Page, Browser

logger = logging.getLogger(__name__)

class InstagramExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.access_token = self.config.META_ACCESS_TOKEN
        self.base_graph_url = "https://graph.facebook.com/v19.0" # API de Meta (Facebook)
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()

    def _get_facebook_page_id_from_url(self, fb_page_url: str) -> Optional[str]:
        """
        Extrae el ID o nombre de usuario de una página de Facebook desde su URL.
        """
        try:
            path_parts = fb_page_url.strip().split('?')[0].split('/')
            page_identifier = path_parts[-1] if path_parts[-1] else path_parts[-2]
            
            # Manejar el caso de profile.php?id=NUMERO
            if page_identifier.lower() == 'profile.php':
                query_params = fb_page_url.split('?')[-1]
                for param in query_params.split('&'):
                    if param.startswith('id='):
                        return param.split('=')[-1]
            return page_identifier
        except Exception as e:
            logger.error(f"Error al extraer ID de página de Facebook desde la URL '{fb_page_url}': {e}")
            return None

    def _get_instagram_business_account_id(self, facebook_page_id: str) -> Optional[str]:
        """
        Obtiene el ID de la Cuenta de Instagram Business vinculada a una Página de Facebook.
        """
        if not self.access_token:
            logger.warning("Instagram API: Token de acceso de Meta no disponible.")
            return None
        
        api_url = f"{self.base_graph_url}/{facebook_page_id}"
        params = {
            "fields": "instagram_business_account{id}", # Solicitar solo el ID
            "access_token": self.access_token
        }
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "instagram_business_account" in data and data["instagram_business_account"]:
                ig_business_id = data["instagram_business_account"]["id"]
                logger.info(f"ID de cuenta de Instagram Business encontrado: {ig_business_id} para la página de Facebook {facebook_page_id}")
                return ig_business_id
            else:
                logger.warning(f"La página de Facebook '{facebook_page_id}' no parece tener una cuenta de Instagram Business vinculada o no se pudo acceder a ella. Respuesta: {data}")
                return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP al buscar la cuenta de Instagram para la página de Facebook {facebook_page_id}: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            logger.error(f"Error de red al buscar la cuenta de Instagram para la página de Facebook {facebook_page_id}: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al buscar la cuenta de Instagram para la página de Facebook {facebook_page_id}: {e}")
        return None

    def extract_followers(self, fb_page_url_or_id: str) -> Optional[int]:
        """
        Extrae el número de seguidores de un perfil de Instagram usando la API.
        IMPORTANTE: La 'url' aquí debe ser la URL o ID de la PÁGINA DE FACEBOOK VINCULADA.
        """
        facebook_page_id = self._get_facebook_page_id_from_url(fb_page_url_or_id)
        if not facebook_page_id:
            logger.error(f"URL proporcionada ('{fb_page_url_or_id}') no es una URL/ID de página de Facebook válida para Instagram.")
            # Podrías intentar un scraping directo si se pasa una URL de Instagram, pero la API no lo permite.
            return self._extract_followers_via_scraping(f"https://www.instagram.com/{fb_page_url_or_id.split('/')[-1]}")


        ig_business_id = self._get_instagram_business_account_id(facebook_page_id)
        if not ig_business_id:
            logger.warning(f"No se pudo obtener el ID de Instagram Business para la página de Facebook {facebook_page_id}.")
            # Aquí, el fallback a scraping debería usar la URL de Instagram, si la tuvieras.
            # Como no la tenemos directamente, el scraping de followers podría ser menos efectivo.
            return self._extract_followers_via_scraping(f"https://www.instagram.com/{facebook_page_id}") # Esto es un placeholder

        if not self.access_token:
            logger.warning("Instagram API: Token de acceso de Meta no disponible para obtener seguidores.")
            return self._extract_followers_via_scraping(f"https://www.instagram.com/{facebook_page_id}") # Placeholder

        api_url = f"{self.base_graph_url}/{ig_business_id}"
        params = {"fields": "followers_count", "access_token": self.access_token}
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            followers = data.get("followers_count")
            if followers is not None:
                logger.info(f"Seguidores de Instagram extraídos vía API: {followers}")
                return followers
            else:
                logger.warning(f"Campo 'followers_count' no encontrado para la cuenta de Instagram {ig_business_id}. Respuesta: {data}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP de API al extraer seguidores de Instagram para {ig_business_id}: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            logger.error(f"Error de red de API al extraer seguidores de Instagram para {ig_business_id}: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al extraer seguidores de Instagram vía API para {ig_business_id}: {e}")
        
        logger.warning(f"Fallo en la extracción de seguidores de Instagram vía API, usando fallback a scraping para {facebook_page_id}.")
        return self._extract_followers_via_scraping(f"https://www.instagram.com/{facebook_page_id}") # Placeholder

    def extract_engagement(self, fb_page_url_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Extrae métricas de engagement de un perfil de Instagram usando la API.
        IMPORTANTE: La 'url' aquí debe ser la URL o ID de la PÁGINA DE FACEBOOK VINCULADA.
        """
        facebook_page_id = self._get_facebook_page_id_from_url(fb_page_url_or_id)
        if not facebook_page_id:
            logger.error(f"URL proporcionada ('{fb_page_url_or_id}') no es una URL/ID de página de Facebook válida para Instagram.")
            return self._extract_engagement_via_scraping(f"https://www.instagram.com/{fb_page_url_or_id.split('/')[-1]}")

        ig_business_id = self._get_instagram_business_account_id(facebook_page_id)
        if not ig_business_id:
            logger.warning(f"No se pudo obtener el ID de Instagram Business para la página de Facebook {facebook_page_id}.")
            return self._extract_engagement_via_scraping(f"https://www.instagram.com/{facebook_page_id}")

        if not self.access_token:
            logger.warning("Instagram API: Token de acceso de Meta no disponible para engagement.")
            return self._extract_engagement_via_scraping(f"https://www.instagram.com/{facebook_page_id}")

        api_url = f"{self.base_graph_url}/{ig_business_id}/media" # Endpoint para obtener los media (posts)
        params = {
            "fields": "like_count,comments_count,media_type,timestamp",
            "limit": 10, # Analizar los últimos 10 posts
            "access_token": self.access_token
        }
        try:
            response = requests.get(api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or not data["data"]:
                logger.warning(f"No se encontraron media (posts) para la cuenta de Instagram {ig_business_id}.")
                return {"posts": 0, "avg_likes": 0, "avg_comments": 0, "total_engagement": 0}

            media_items = data["data"]
            total_likes = 0
            total_comments = 0
            media_count = 0

            for item in media_items:
                # Considerar solo imágenes y videos, no stories si aparecen (depende de los permisos)
                if item.get("media_type") in ["IMAGE", "VIDEO", "CAROUSEL_ALBUM"]:
                    total_likes += item.get("like_count", 0)
                    total_comments += item.get("comments_count", 0)
                    media_count +=1
            
            if media_count == 0: # Si solo hay stories o no hay posts analizables
                 logger.warning(f"No se encontraron posts analizables (imágenes/videos) para la cuenta de Instagram {ig_business_id}.")
                 return {"posts": 0, "avg_likes": 0, "avg_comments": 0, "total_engagement": 0}

            engagement_metrics = {
                "posts": media_count,
                "avg_likes": round(total_likes / media_count) if media_count > 0 else 0,
                "avg_comments": round(total_comments / media_count) if media_count > 0 else 0,
            }
            engagement_metrics["total_engagement"] = engagement_metrics["avg_likes"] + engagement_metrics["avg_comments"]
            logger.info(f"Engagement de Instagram extraído vía API para {ig_business_id}: {engagement_metrics}")
            return engagement_metrics
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP de API al extraer engagement de Instagram para {ig_business_id}: {e.response.status_code} - {e.response.text}")
        except requests.RequestException as e:
            logger.error(f"Error de red de API al extraer engagement de Instagram para {ig_business_id}: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al extraer engagement de Instagram vía API para {ig_business_id}: {e}")
        
        logger.warning(f"Fallo en la extracción de engagement de Instagram vía API, usando fallback a scraping para {facebook_page_id}.")
        return self._extract_engagement_via_scraping(f"https://www.instagram.com/{facebook_page_id}") # Placeholder

    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        logger.info(f"Fallback: Intentando scraping de seguidores de Instagram para {url}")
        # Tu lógica de scraping aquí...
        return None

    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Fallback: Intentando scraping de engagement de Instagram para {url}")
        # Tu lógica de scraping aquí...
        return None