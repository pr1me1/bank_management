import logging
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.configs import settings

logger = logging.getLogger(__name__)


class GNKAPIService:

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.INFO_ENDPOINT = settings.INN_CHECK_INFO_ENDPOINT
        self.BASE_URL = settings.INN_CHECK_BASE_URL
        self.timeout = timeout
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _validate_inn(self, inn: str) -> bool:
        if not inn:
            return False

        inn = inn.strip()

        return inn.isdigit() and (len(inn) == 9 or len(inn) == 14)

    def get_company_info(self, inn: str) -> Optional[Dict[str, Any]]:
        if not self._validate_inn(inn):
            raise ValueError(f"Invalid INN format. INN must be exactly 9 or 14 digits, got: {inn}")

        if not self.BASE_URL:
            logger.warning("INN_CHECK_BASE_URL is not configured. GNK API validation will be skipped.")
            return None

        endpoint = self.INFO_ENDPOINT if self.INFO_ENDPOINT.startswith('/') else f"/{self.INFO_ENDPOINT}"

        base_url = self.BASE_URL.rstrip('/')

        url = f"{base_url}{endpoint}/{inn}"

        try:
            logger.info(f"Fetching company info for INN: {inn}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched company info for INN: {inn}")
            if not data.get("tin") or not data.get("fullName"):
                return None
            return data

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching company info for INN: {inn}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Company not found for INN: {inn}")
            else:
                logger.error(f"HTTP error while fetching company info for INN {inn}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while fetching company info for INN {inn}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while fetching company info for INN {inn}: {e}", exc_info=True)
            return None

    def __del__(self):

        if hasattr(self, 'session'):
            self.session.close()


__all__ = ['GNKAPIService']
