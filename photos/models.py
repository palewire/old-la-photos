import requests
import collections
from io import BytesIO
from django.db import models
from django.core.files import File


class Photo(models.Model):
    """
    A photograph archived by the Los Angeles Public Library
    """
    # From LAPL
    title = models.CharField(max_length=2000)
    link = models.CharField(max_length=2000)
    description  = models.TextField(blank=True)
    pub_date = models.DateTimeField()
    # The photo itself
    image = models.ImageField(blank=True)
    # Our metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title

    def to_dict(self):
        """
        Returns this object in dict format.
        """
        return collections.OrderedDict([
            ("lapl_id", self.lapl_id),
            ("title", self.title),
            ("pub_date", str(self.pub_date)),
            ("description", self.description),
            ("lapl_url", self.link),
            ("download_url", self.download_url),
            ("image_url", self.image_url)
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

    @property
    def image_url(self):
        """
        Returns the URL to our archived version of the image.
        """
        if self.image:
            return self.image.url
        else:
            return None

    def get_image(self):
        """
        Downloads the photo from LAPL and returns it as a PIL Image object.
        """
        r = requests.get(self.download_url)
        obj = BytesIO(r.content)
        return File(obj)

    def save_image(self):
        """
        Saves the image from the LAPL site to our S3 archive.
        """
        filename = f"{self.lapl_id}.jpg"
        self.image.save(filename, self.get_image(), save=True)
