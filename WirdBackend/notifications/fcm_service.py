import logging
from dataclasses import dataclass
from typing import List, Optional

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)


@dataclass
class NotificationPayload:
    title: str
    body: str
    data: Optional[dict] = None


class FCMService:
    """Firebase Cloud Messaging service for sending push notifications."""

    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK."""
        if cls._initialized:
            return

        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            cls._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise

    @classmethod
    def send_to_token(cls, token: str, payload: NotificationPayload) -> bool:
        """Send notification to a single FCM token."""
        cls.initialize()

        message = messaging.Message(
            notification=messaging.Notification(
                title=payload.title,
                body=payload.body,
            ),
            data=payload.data or {},
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
        )

        try:
            messaging.send(message)
            return True
        except messaging.UnregisteredError:
            return False
        except Exception as e:
            return False

    @classmethod
    def send_to_tokens(
            cls,
            tokens: List[str],
            payload: NotificationPayload
    ) -> dict:
        """Send notification to multiple FCM tokens."""
        cls.initialize()

        if not tokens:
            return {'success': 0, 'failure': 0, 'invalid_tokens': []}

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=payload.title,
                body=payload.body,
            ),
            data=payload.data or {},
            tokens=tokens,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
        )

        try:
            response = messaging.send_each_for_multicast(message)

            invalid_tokens = []
            for idx, send_response in enumerate(response.responses):
                if not send_response.success:
                    if isinstance(
                            send_response.exception,
                            messaging.UnregisteredError
                    ):
                        invalid_tokens.append(tokens[idx])

            return {
                'success': response.success_count,
                'failure': response.failure_count,
                'invalid_tokens': invalid_tokens,
            }
        except Exception as e:
            logger.error(f"Error sending multicast message: {e}")
            return {
                'success': 0,
                'failure': len(tokens),
                'invalid_tokens': []
            }
