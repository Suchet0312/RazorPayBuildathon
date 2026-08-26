import os
import razorpay
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RazorpayClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RazorpayClient, cls).__new__(cls)
            cls._instance.client = cls._init_client()
        return cls._instance

    @classmethod
    def _init_client(cls) -> Optional[razorpay.Client]:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        if not key_id or not key_secret:
            logger.warning("Razorpay credentials not found in environment. Integration will be disabled.")
            return None
        
        try:
            return razorpay.Client(auth=(key_id, key_secret))
        except Exception as e:
            logger.error(f"Failed to initialize Razorpay Client: {e}")
            return None

    def fetch_payment(self, payment_id: str) -> dict:
        if not self.client:
            raise ValueError("Razorpay Client is not initialized.")
        return self.client.payment.fetch(payment_id)

    def create_payment_link(self, amount: int, currency: str, description: str, reference_id: str) -> dict:
        if not self.client:
            raise ValueError("Razorpay Client is not initialized.")
        
        # Amount in paise (multiply by 100)
        payload = {
            "amount": amount * 100,
            "currency": currency,
            "accept_partial": False,
            "description": description,
            "reference_id": reference_id,
            "reminder_enable": True,
            "notes": {
                "source": "Agentic Recovery Brain"
            }
        }
        return self.client.payment_link.create(payload)
