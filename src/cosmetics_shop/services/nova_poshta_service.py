import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class NovaPoshtaAPI:
    BASE_URL = settings.NOVA_POSHTA_API_URL

    def __init__(self):
        self.api_key = settings.NOVA_POSHTA_API_KEY

    def _request(self, model_name, called_method, properties=None):
        payload = {
            "apiKey": self.api_key,
            "modelName": model_name,
            "calledMethod": called_method,
            "methodProperties": properties or {},
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error Nova Poshta API: {str(e)}")
            return {"success": False, "data": []}

    def get_cities(self, search: str = ""):
        """Search for cities by string"""
        return self._request(
            "Address", "getCities", {"FindByString": search, "Limit": 20}
        )

    def get_warehouses(self, city_ref: str):
        """Getting branches by CityRef (city identifier)"""
        return self._request("Address", "getWarehouses", {"CityRef": city_ref})
