from rest_framework.response import Response
from rest_framework.views import exception_handler
import logging
import os

logger = logging.getLogger('django')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        e_codes = os.environ.get('ERROR_CODES')
        error_list = [int(e) for e in e_codes.split(',')] if e_codes else [500]
        if response.status_code in error_list:
            logger.exception(response)
        return response
    else:
        logger.exception(exc)
        return Response(f"{exc}", status=500)
