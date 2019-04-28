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
