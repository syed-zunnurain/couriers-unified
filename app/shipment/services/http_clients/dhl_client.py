import logging
import requests
from typing import Dict, Any, Optional
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)


class DHLHttpClient(BaseHttpClient):
    def __init__(self, base_url: str, api_key: str = None, api_secret: str = None, 
                 username: str = None, password: str = None, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.password = password
        self._access_token = None
        self._token_expires_at = None
    
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        
        token = self._get_valid_token()
        if token:
            headers['Authorization'] = f"Bearer {token}"
        
        return headers
    
    def _get_valid_token(self) -> Optional[str]:
        import time
        
        if self._access_token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._access_token
        
        return self._fetch_access_token()
    
    def _fetch_access_token(self) -> Optional[str]:
        try:
            token_url = f"{self.base_url}/parcel/de/account/auth/ropc/v1/token"
            
            data = {
                'grant_type': 'password',
                'client_id': self.api_key,
                'client_secret': self.api_secret,
                'username': self.username,
                'password': self.password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            logger.info("DHLHttpClient: Fetching access token from DHL OAuth endpoint")
            
            response = self.session.post(
                token_url,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get('access_token')
                
                expires_in = token_data.get('expires_in', 3600)
                import time
                self._token_expires_at = time.time() + expires_in - 60  # 1 minute buffer
                
                logger.info("DHLHttpClient: Successfully obtained access token")
                return self._access_token
            else:
                logger.error(f"DHLHttpClient: Failed to get access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"DHLHttpClient: Error fetching access token: {str(e)}")
            return None
    
    def create_shipment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            endpoint = "parcel/de/shipping/v2/orders?validate=false"
            response = self._make_request('POST', endpoint, data=payload)
            
            if response.status_code == 200:
                logger.info("DHLHttpClient: Shipment created successfully")
                return {
                    'success': True,
                    'data': response.json(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"DHLHttpClient: Shipment creation failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f"DHL API error: HTTP {response.status_code}",
                    'data': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"DHLHttpClient: Error creating shipment: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}",
                'data': None,
                'status_code': 0
            }
    
    def track_shipment(self, tracking_number: str) -> Dict[str, Any]:
        try:
            endpoint = "track/shipments"
            test_tracking_number = ""
            params = {
                'trackingNumber': test_tracking_number,
                'service': 'express',
                'language': 'en',
                'offset': 0,
                'limit': 5
            }
            
            headers = {
                'accept': 'application/json',
                'DHL-API-Key': 'demo-key'  # Test environment key
            }
            
            logger.info(f"DHLHttpClient: Tracking shipment {tracking_number} (using hardcoded test number: {test_tracking_number})")
            
            tracking_base_url = "https://api-test.dhl.com"
            response = self.session.get(
                f"{tracking_base_url}/{endpoint}",
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"DHLHttpClient: Tracking info retrieved for {tracking_number}")
                return {
                    'success': True,
                    'data': response.json(),
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"DHLHttpClient: Tracking failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f"DHL API error: HTTP {response.status_code}",
                    'data': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"DHLHttpClient: Error tracking shipment: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}",
                'data': None,
                'status_code': 0
            }
    
    def cancel_shipment(self, courier_external_id: str) -> Dict[str, Any]:
        try:
            # Cancel shipment endpoint
            endpoint = f"parcel/de/shipping/v2/orders?shipment={courier_external_id}&profile=STANDARD_GRUPPENPROFIL"
            
            logger.info(f"DHLHttpClient: Cancelling shipment {courier_external_id}")
            
            response = self._make_request('DELETE', endpoint)
            
            if response.status_code == 200:
                logger.info(f"DHLHttpClient: Successfully cancelled shipment {courier_external_id}")
                return {
                    'success': True,
                    'data': response.json() if response.content else {},
                    'status_code': response.status_code
                }
            else:
                logger.warning(f"DHLHttpClient: Cancellation failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f"DHL API error: HTTP {response.status_code}",
                    'data': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"DHLHttpClient: Error cancelling shipment: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}",
                'data': None,
                'status_code': 0
            }
    
    def get_label(self, courier_external_id: str) -> Dict[str, Any]:
        try:
            endpoint = "parcel/de/shipping/v2/orders"
            params = {
                'shipment': courier_external_id,
                'docFormat': 'PDF',
                'includeDocs': 'URL'
            }
            
            logger.info(f"DHLHttpClient: Getting label for shipment {courier_external_id}")
            return self.get(endpoint, params=params)
                
        except Exception as e:
            logger.error(f"DHLHttpClient: Error getting label: {str(e)}")
            return {
                'success': False,
                'error': f"DHL API error: {str(e)}",
                'status_code': 0
            }