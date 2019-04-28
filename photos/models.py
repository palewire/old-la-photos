import requests
import collections
from PIL import Image
from io import BytesIO
from django.db import models


class Photo(models.Model):
    """
    A photograph archived by the Los Angeles Public Library
    """
    # From LAPL
    title = models.CharField(max_length=2000)
    link = models.CharField(max_length=2000)
    description  = models.TextField(blank=True)
    pub_date = models.DateTimeField()
    # Our metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title

    def __dict__(self):
        """
        Returns this object in dict format.
        """
        return collections.OrderedDict([
            ("lapl_id", self.lapl_id),
            ("title", self.title),
            ("pub_date", str(self.pub_date)),
            ("description", self.description),
            ("url", self.link),
            ("download_url", self.download_url)
        ])

    @property
    def lapl_id(self):
        """
        Returns the unique identifier of the photo.
        """
        return self.link.split("/")[-1]

    @property
    def download_url(self):
        """
        Returns the URL where a JPG file can be downloaded.
        """
        return f"https://tessa.lapl.org/utils/getdownloaditem/collection/photos/id/{self.lapl_id}"

    def get_image(self):
        """
        Downloads the photo from LAPL and returns it as a PIL Image object.
        """
        r = requests.get(url)
        obj = BytesIO(response.content)
        return Image.open(obj)
