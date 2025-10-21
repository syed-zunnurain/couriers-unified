import logging
from typing import Optional
from ...models import Shipment
from ...services.couriers.courier_factory import courier_factory
from ...services.couriers.cancellable_courier_interface import CancellableCourierInterface
from ...schemas.cancellation_response import CancellationResponse

logger = logging.getLogger(__name__)


class CourierCancellationService:
    def __init__(self, courier_factory_instance=None):
        self._courier_factory = courier_factory_instance or courier_factory

    def cancel_with_courier(self, shipment: Shipment) -> CancellationResponse:
        try:
            logger.info(f"CourierCancellationService: Cancelling shipment {shipment.reference_number} with {shipment.courier.name}")
            
            courier_instance = self._courier_factory.get_courier_instance(
                shipment.courier.name.lower(),
                shipment.courier
            )
            
            if not courier_instance:
                logger.warning(f"CourierCancellationService: Courier instance not found for {shipment.courier.name}")
                return CancellationResponse.create_error_response(
                    'Courier instance not found',
                    'COURIER_NOT_FOUND'
                )
            
            if not isinstance(courier_instance, CancellableCourierInterface):
                logger.warning(f"CourierCancellationService: Courier {shipment.courier.name} does not implement CancellableCourierInterface")
                return CancellationResponse.create_error_response(
                    'Courier does not support cancellation',
                    'CANCELLATION_NOT_SUPPORTED'
                )
            
            # Call courier's cancel method
            logger.info(f"CourierCancellationService: Calling {shipment.courier.name} API to cancel shipment {shipment.courier_external_id}")
            courier_result = courier_instance.cancel_shipment(shipment.courier_external_id)
            
            # Convert courier result to response object
            if courier_result.get('success'):
                logger.info(f"CourierCancellationService: Successfully cancelled with {shipment.courier.name}")
                return CancellationResponse.create_success_response(
                    courier_result.get('message', 'Shipment cancelled with courier'),
                    shipment.id,
                    shipment.reference_number,
                    shipment.courier_external_id,
                    courier_result
                )
            else:
                logger.warning(f"CourierCancellationService: {shipment.courier.name} cancellation failed: {courier_result.get('message')}")
                return CancellationResponse.create_error_response(
                    courier_result.get('message', 'Courier cancellation failed'),
                    'COURIER_CANCELLATION_FAILED',
                    courier_result.get('message'),
                    courier_result
                )
            
        except Exception as e:
            logger.error(f"CourierCancellationService: Error cancelling with courier: {str(e)}", exc_info=True)
            return CancellationResponse.create_error_response(
                f'Error cancelling with courier: {str(e)}',
                'COURIER_CANCELLATION_ERROR'
            )
