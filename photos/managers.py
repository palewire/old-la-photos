from django.db import models


class PhotoManager(models.Manager):

    def tweeted(self):
        return self.get_queryset().exclude(tweet_id='')

    def untweeted(self):
        return self.get_queryset().filter(tweet_id='')
