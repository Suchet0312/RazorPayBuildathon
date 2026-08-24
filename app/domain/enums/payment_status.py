from enum import Enum


class PaymentStatus(str, Enum):
    FAILED = "failed"
    PENDING = "pending"
    RECOVERED = "recovered"
    SUCCEEDED = "succeeded"