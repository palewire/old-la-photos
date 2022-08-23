import time
from photos.models import Photo
from django.utils import timezone
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Make tweets at @OldLAPhotos"

    def handle(self, *args, **options):
        # Heroku only lets task run hourly. But we want to run every other hour.
        this_hour = timezone.now().hour
        # So we will hack it to run only every other hour
        if this_hour % 2:
            # Tweet away...
            obj_list = Photo.objects.untweeted().order_by("?")
            obj = obj_list[0]
            print(f"Tweeting {obj}")
            obj.tweet()
            time.sleep(3)
        else:
            print("Not this hour.")
