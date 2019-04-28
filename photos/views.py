import json
from .models import Photo
from django.http import HttpResponse


def photo_list(request):
    """
    A dump of the latest scraped season totals.
    """
    obj_list = Photo.objects.all()
    dict_list = [o.__dict__() for o in obj_list]
    return HttpResponse(
        json.dumps(dict_list, indent=4),
        content_type="application/javascript"
    )
