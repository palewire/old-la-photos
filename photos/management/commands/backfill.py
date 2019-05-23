# -*- coding: utf-8 -*-
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from photos.models import Photo
from django.db.models import Max
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Save the older photos from the LAPL's online database"

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        print("Backfilling images")
        # Get some random photo ids to try.
        max_lapl_id = Photo.objects.aggregate(max=Max("lapl_id"))['max'] or 5000
        print(f"{max_lapl_id} potential IDs in the source archive")
        id_list = set(Photo.objects.values_list("id", flat=True))
        print(f"{len(id_list)} photos now in our mirror database")
        id_range = set(range(1, max_lapl_id+1))
        missing_ids = id_range.difference(id_list)
        print(f"{len(missing_ids) potential photos yet to mirror}")
        sample_ids = random.sample(missing_ids, 25)
        for lapl_id in sample_ids:
            try:
                obj = Photo.objects.get(lapl_id=lapl_id)
                print(f"{obj} already exists with id {lapl_id}")
                continue
            except Photo.DoesNotExist:
                # Create the object.
                obj = Photo(
                    link= f"https://tessa.lapl.org/cdm/ref/collection/photos/id/{lapl_id}",
                    lapl_id=lapl_id
                )

                # Pull the data from the LAPL site
                print(f"Scraping {obj.link}")
                r = requests.get(obj.link)
                soup = BeautifulSoup(r.content, "html.parser")

                # Parse and save to the object
                obj.title = self._parse_text(soup.select("td#metadata_title")[0])
                obj.physical_description = self._parse_text(soup.select("td#metadata_descri")[0])
                obj.description = self._parse_text(soup.select("td#metadata_descra")[0])
                # obj.collection = self._parse_text(soup.select("td#metadata_collec")[0])
                obj.subcollection = self._parse_text(soup.select("td#metadata_collea")[0])
                obj.save()

                # Tack on the tags
                obj.tags.add(*self._parse_list(soup.select("td#metadata_subjec")[0]))

                # Save the image
                print(f"Archiving image {obj.download_url}")
                obj.save_image()
                time.sleep(1)

    def _remove_period(self, s):
        if s[-1] == '.':
            return s[:-1]
        else:
            return s

    def _parse_list(self, element):
        """
        Parse a list from the scrape.
        """
        element_list = element.find_all("a")
        return [self._remove_period(e.string.strip()) for e in element_list]

    def _parse_text(self, element):
        """
        Parse a string out of our scrape.
        """
        return element.text.strip()
