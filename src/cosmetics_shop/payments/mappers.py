from cosmetics_shop.models import Payment
from cosmetics_shop.payments.enums import MonoStatus

MONO_STATUS_MAP = {
    MonoStatus.CREATED.value: Payment.PaymentStatus.PENDING,
    MonoStatus.PROCESSING.value: Payment.PaymentStatus.PENDING,
    MonoStatus.HOLD.value: Payment.PaymentStatus.PENDING,
    MonoStatus.SUCCESS.value: Payment.PaymentStatus.SUCCESS,
    MonoStatus.FAILURE.value: Payment.PaymentStatus.FAILED,
    MonoStatus.REVERSED.value: Payment.PaymentStatus.FAILED,
    MonoStatus.EXPIRED.value: Payment.PaymentStatus.FAILED,
}
