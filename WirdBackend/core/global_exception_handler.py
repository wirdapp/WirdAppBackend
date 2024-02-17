from rest_framework.response import Response
from rest_framework.views import exception_handler
import logging
import os
import traceback

logger = logging.getLogger('django')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    logger.exception(exc)
    logger.error(traceback.format_exc())
    if response is not None:
        return response
    else:
        return Response(f"{exc}", status=500)
