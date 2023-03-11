from hijri_converter import Hijri
from rest_framework.response import Response


def get_today_date_hijri():
    return Hijri.today()


def destroy(instance):
    instance.is_active = False
    instance.save()
    return Response(status=204)
