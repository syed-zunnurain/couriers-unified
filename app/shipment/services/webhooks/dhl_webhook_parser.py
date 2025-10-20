from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class DHLWebhookData:
    tracking_number: str
    status: str
    timestamp: str
    location_address: Optional[str] = None
    location_country: Optional[str] = None
    location_postal_code: Optional[str] = None


class DHLWebhookParser:
    
    @classmethod
    def parse(cls, payload: Dict[str, Any]) -> Optional[DHLWebhookData]:
        try:
            tracking_number = payload.get('tracking_number')
            status = payload.get('status')
            
            if not tracking_number or not status:
                return None
            
            location = payload.get('location', {})
            
            return DHLWebhookData(
                tracking_number=str(tracking_number),
                status=str(status).upper(),
                timestamp=datetime.utcnow().isoformat(),
                location_address=location.get('addressLocality'),
                location_country=location.get('countryCode'),
                location_postal_code=location.get('postalCode')
            )
            
        except Exception:
            return None
