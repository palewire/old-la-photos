import collections
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
            ("link", self.link),
        ])

    @property
    def lapl_id(self):
        """
        Returns the unique identifier of the photo.
        """
        return self.link.split("/")[-1]
