import twitter
import requests
import collections
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files import File
from photos.managers import PhotoManager


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
    tweet_id = models.CharField(blank=True, default="", max_length=500)
    # Managers
    objects = PhotoManager()

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

    def tweeted(self):
        """
        Has this photo been tweeted? Returns True or False.
        """
        if self.tweet_id:
            return True
        else:
            return False
    tweeted.boolean = True

    @property
    def twitter_url(self):
        """
        Where to find the tweet.
        """
        return f'https://twitter.com/muckrockbot/status/{self.tweet_id}/'

    def tweet(self):
        """
        Post this photo to Twitter.
        """
        if self.tweet_id or not self.image_url:
            return False
        api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_ACCESS_TOKEN_KEY,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        tweet = f"{self.title} {self.link}"
        status = api.PostUpdate(
            tweet,
            media=self.image_url,
            attachment_url=self.image_url
        )
        self.tweet_id = status.id
        self.save()
