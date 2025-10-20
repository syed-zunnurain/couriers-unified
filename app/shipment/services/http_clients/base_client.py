import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseHttpClient(ABC):
    """Base HTTP client for all courier integrations."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a configured requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            headers: Additional headers
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {**self._get_headers(), **(headers or {})}
        
        logger.info(f"BaseHttpClient: Making {method} request to {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            
            logger.info(f"BaseHttpClient: Response status: {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BaseHttpClient: Request failed: {str(e)}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make GET request with error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Dict containing response data or error
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            request_headers = {**self._get_headers(), **(headers or {})}
            
            logger.info(f"BaseHttpClient: Making GET request to {url}")
            if params:
                logger.info(f"BaseHttpClient: Query parameters: {params}")
            
            response = self.session.get(
                url=url,
                params=params,
                headers=request_headers,
                timeout=self.timeout
            )
            
            logger.info(f"BaseHttpClient: Response status: {response.status_code}")
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json() if response.content else {},
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"BaseHttpClient: GET request failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 0
            }
    
    @abstractmethod
    def create_shipment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create shipment with the courier."""
        pass
    
    @abstractmethod
    def track_shipment(self, tracking_number: str) -> Dict[str, Any]:
        """Track shipment with the courier."""
        pass
