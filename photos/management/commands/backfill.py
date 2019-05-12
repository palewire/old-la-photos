# -*- coding: utf-8 -*-
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
        # Get some random photo ids to try.
        max_lapl_id = Photo.objects.aggregate(max=Max("lapl_id"))['max'] or 5000
        attempts = 0
        candidates = []
        while True:
            random_number = random.randrange(max_lapl_id)
            attempts += 1
            logger.debug(f"Making backfill attempt {attempts}")
            try:
                Photo.objects.get(lapl_id=random_number)
            except Photo.DoesNotExist:
                candidates.append(random_number)
            if len(candidates) >= 5 or attempts >= 20:
                break
        # Scrape them
        for lapl_id in candidates:
            obj = Photo(
                link= f"https://tessa.lapl.org/cdm/ref/collection/photos/id/{lapl_id}",
                lapl_id=lapl_id
            )
            logger.debug(f"Scraping {obj.link}")
            r = requests.get(obj.link)
            soup = BeautifulSoup(r.content, "html.parser")
            obj.title = self._parse_text(soup.select("td#metadata_title")[0])
            obj.physical_description = self._parse_text(soup.select("td#metadata_descri")[0])
            obj.description = self._parse_text(soup.select("td#metadata_descra")[0])
            obj.collection = self._parse_text(soup.select("td#metadata_collec")[0])
            obj.subcollection = self._parse_text(soup.select("td#metadata_collea")[0])
            obj.save()
            logger.debug(f"Archiving image {obj.download_url}")
            obj.save_image()

    def _parse_text(self, element):
        """
        Parse a string out of our scrape.
        """
        return element.text.strip()
