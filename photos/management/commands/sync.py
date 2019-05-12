# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from photos.models import Photo
from dateutil.parser import parse as dateparse
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Save the latest photos from the LAPL's RSS feed"

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        url = "https://tessa.lapl.org/cdm/viewfeed/collection/photos"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        item_list = soup.find_all("item")
        for item in item_list:
            data_dict = dict(
                title=self._parse_str(item.find("title")),
                physical_description=self._parse_str(item.find("description")),
                link=self._parse_str(item.find("guid"))
            )
            try:
                obj = Photo.objects.get(link=data_dict['link'])
                print(f"Updating {obj.link}")
            except Photo.DoesNotExist:
                obj = Photo(link=data_dict['link'])
                print(f"Creating {obj.link}")
            obj.title = data_dict['title']
            obj.physical_description = data_dict['physical_description']
            obj.lapl_id = obj.get_lapl_id()
            obj.save()
            if not obj.image:
                print(f"Archiving image {obj.download_url}")
                obj.save_image()

    def _parse_str(self, element):
        """
        Parse a string out of our scrape.
        """
        return element.string.strip()
