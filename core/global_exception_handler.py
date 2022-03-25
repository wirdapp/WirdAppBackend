from rest_framework.response import Response
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger('django')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code == 500:
            logger.exception(response)
        return response
    else:
        logger.exception(exc)
        return Response(f"{exc}", status=500)
