from django.core.cache import caches
from hijri_converter import Hijri

current_hijri_date = Hijri.today().datetuple()[2]
cache = caches['default']


def get_from_cache(key):
    result = cache.get(key)
    return result


def save_to_cache(key, value, timeout):
    cache.set(key, value, timeout=timeout)
