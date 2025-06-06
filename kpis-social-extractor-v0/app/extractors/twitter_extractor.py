"""
Twitter/X Extractor Module - KPIs Social Extractor

This module implements Twitter/X-specific extraction logic using the hybrid approach:
1. Twitter API v2 (when credentials are available) using the 'tweepy' library.
2. Advanced web scraping with Playwright as a fallback.
"""

import tweepy
import logging
from typing import Optional, Dict, Any

from app.extractors.base_extractor import BaseExtractor
from app.config.config import Config
# Importaciones para el fallback de scraping (si se mantiene)
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
from app.utils.human_simulation import HumanSimulation

logger = logging.getLogger(__name__)

class TwitterExtractor(BaseExtractor):
    """
    Extractor para X (Twitter) que prioriza el uso de la API v2 con Tweepy.
    """
    def __init__(self):
        """Inicializa el extractor y el cliente de la API de Twitter."""
        super().__init__()
        self.api_client = None
        self.user_agent = UserAgent()
        self.human_simulation = HumanSimulation()

        # La API v2 de Twitter utiliza un "Bearer Token" para la autenticación de solo lectura (App-only).
        # Este es el método más simple y robusto para obtener datos públicos.
        # Asegúrate de que TWITTER_API_KEY en tu archivo .env contenga este Bearer Token.
        # Puedes obtenerlo desde tu portal de desarrollador de X.
        bearer_token = self.config.TWITTER_API_KEY

        # En el método __init__ de TwitterExtractor
        if bearer_token:
            try:
                # Añade wait_on_rate_limit=True
                self.api_client = tweepy.Client(bearer_token, wait_on_rate_limit=True)
                logger.info("Cliente de la API de Twitter (Tweepy) inicializado correctamente.")
            except Exception as e:
                logger.error(f"Error al inicializar el cliente de Tweepy: {e}")
        else:
            logger.warning("No se proporcionó un Bearer Token en la configuración (TWITTER_API_KEY). La extracción dependerá únicamente del web scraping.")

    def _extract_username_from_url(self, url: str) -> Optional[str]:
        """Extrae el nombre de usuario de la URL de un perfil de Twitter."""
        try:
            # Elimina parámetros de consulta y toma la última parte de la URL
            return url.strip().split('?')[0].split('/')[-1]
        except IndexError:
            logger.error(f"No se pudo analizar la URL para extraer el nombre de usuario: {url}")
            return None

    def extract_followers(self, url: str) -> Optional[int]:
        """
        Intenta extraer seguidores vía API. Si falla o no está disponible,
        se podría implementar un fallback a scraping.
        """
        # --- Nivel 1: Extracción vía API (Método preferido) ---
        if self.api_client:
            username = self._extract_username_from_url(url)
            if not username:
                return None

            try:
                logger.info(f"Buscando usuario '{username}' vía API de Twitter.")
                response = self.api_client.get_user(username=username, user_fields=["public_metrics"])
                
                if response.data and response.data.public_metrics and 'followers_count' in response.data.public_metrics:
                    followers_count = response.data.public_metrics['followers_count']
                    logger.info(f"Seguidores extraídos para '{username}': {followers_count}")
                    return followers_count
                else:
                    error_message = f"No se pudo encontrar el usuario '{username}' o sus métricas públicas."
                    if response.errors:
                        error_message += f" Detalles: {response.errors}"
                    logger.error(error_message)

            except tweepy.errors.TweepyException as e:
                logger.error(f"Error de la API de Tweepy al extraer seguidores para '{username}': {e}")
            except Exception as e:
                logger.error(f"Error inesperado al extraer seguidores de Twitter para '{username}': {e}")
        
        # --- Nivel 2: Fallback a Web Scraping (Opcional) ---
        # Si la extracción con API falla, se puede llamar a un método de scraping.
        logger.warning(f"La extracción vía API para '{url}' falló o no está configurada. El fallback a scraping no está implementado en este ejemplo.")
        # Aquí podrías llamar a tu método _extract_followers_via_scraping(url) si deseas mantenerlo.
        
        return None

    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Intenta extraer engagement vía API. Si falla, se podría usar scraping.
        """
        # --- Nivel 1: Extracción de Engagement vía API ---
        if self.api_client:
            username = self._extract_username_from_url(url)
            if not username:
                return None
            
            try:
                # Primero, obtenemos el ID del usuario a partir de su nombre de usuario
                user_response = self.api_client.get_user(username=username)
                if not user_response.data:
                    logger.error(f"No se pudo obtener el ID para el usuario '{username}'.")
                    return None
                user_id = user_response.data.id

                # Luego, obtenemos los tweets más recientes del usuario
                tweets_response = self.api_client.get_users_tweets(
                    id=user_id,
                    max_results=10,  # Analizar los últimos 10 tweets
                    exclude=["retweets", "replies"],
                    tweet_fields=["public_metrics"]
                )

                if not tweets_response.data:
                    logger.warning(f"No se encontraron tweets recientes para el usuario '{username}'.")
                    return {"posts": 0, "avg_likes": 0, "avg_retweets": 0, "total_engagement": 0}

                tweets = tweets_response.data
                total_likes = 0
                total_retweets = 0
                tweet_count = len(tweets)

                for tweet in tweets:
                    if tweet.public_metrics:
                        total_likes += tweet.public_metrics.get("like_count", 0)
                        total_retweets += tweet.public_metrics.get("retweet_count", 0)

                avg_likes = round(total_likes / tweet_count) if tweet_count > 0 else 0
                avg_retweets = round(total_retweets / tweet_count) if tweet_count > 0 else 0
                
                engagement_metrics = {
                    "posts": tweet_count,
                    "avg_likes": avg_likes,
                    "avg_retweets": avg_retweets,
                    "total_engagement": avg_likes + avg_retweets # Ejemplo simplificado de engagement total
                }
                logger.info(f"Métricas de engagement extraídas para '{username}': {engagement_metrics}")
                return engagement_metrics

            except tweepy.errors.TweepyException as e:
                logger.error(f"Error de la API de Tweepy al extraer engagement para '{username}': {e}")
            except Exception as e:
                logger.error(f"Error inesperado al extraer engagement de Twitter para '{username}': {e}")

        # --- Nivel 2: Fallback a Web Scraping ---
        logger.warning(f"La extracción de engagement vía API para '{url}' falló o no está configurada. El fallback a scraping no está implementado en este ejemplo.")
        return None