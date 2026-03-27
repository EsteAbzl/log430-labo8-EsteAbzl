"""
Handler: Stock Decreased
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import requests
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer


class StockDecreasedHandler(EventHandler):
    """Handles StockDecreased events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "StockDecreased"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        '''
        TODO: Consultez le diagramme de machine à états pour savoir quelle opération 
        effectuer dans cette méthode. 
        
        **Conseil** : si vous préférez, avant de travailler sur l'implémentation event-driven, 
        effectuez un appel synchrone (requête HTTP) à l'API Payments, attendez le résultat, puis 
        continuez la saga. L'approche synchrone peut être plus facile à comprendre dans un premier temps.
          
        En revanche, dans une implémentation 100% event-driven, ce StockDecreasedHandler se trouvera 
        dans l'API Payments et non dans Store Manager, car c'est l'API Payments qui doit 
        être notifiée de la mise à jour du stock afin de générer une transaction de paiement.
        '''
        try:

            # création du lien de paiement
            response = requests.post(f'http://api-gateway:8080/payments-api/payments',
                json={
                    "user_id": event_data['user_id'],
                    "order_id": event_data['order_id'],
                    "total_amount": event_data['total_amount']
                },
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                self.logger.debug("Transition d'état: CreatePayment -> PAYMENT_CREATED")
                # Si la transaction de paiement a été crée, déclenchez PaymentCreated.
                payload = response.json() or {}
                payment_id = payload.get('payment_id')

                event_data['payment_link'] = f"http://api-gateway:8080/payments-api/payments/process/{payment_id}"
                event_data['event'] = "PaymentCreated"
                self.logger.debug(f"payment_link={event_data['payment_link']}")
            else:
                # Si la mise à jour du stock a échoué, déclenchez PaymentCreationFailed.
                self.logger.debug("payment demandé mais pas ok")
                event_data['event'] = "PaymentCreationFailed"

        except Exception as e:
            # Si la mise à jour du stock a échoué, déclenchez PaymentCreationFailed.
            self.logger.debug(f"payment erreur : {e}")
            event_data['event'] = "PaymentCreationFailed"
            event_data['error'] = str(e)
        finally:
            self.order_producer.get_instance().send(config.KAFKA_TOPIC, value=event_data)


