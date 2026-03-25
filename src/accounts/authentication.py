import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

logger = logging.getLogger(__name__)


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        user_model = get_user_model()

        logger.debug(f"Auth attempt: email={email}")

        try:
            user = user_model.objects.filter(email=email).first()
            logger.info(f"Auth success: user_id={user.id}")

            if user.check_password(password) and user.is_active:
                return user

            logger.warning(f"Auth failed: email={email}")
            return None

        except user_model.DoesNotExist as e:
            logger.exception(f"Auth error: email={email}, error={str(e)}")
            return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            logger.exception(f"User don't exist: id={user_id}")
            return None
