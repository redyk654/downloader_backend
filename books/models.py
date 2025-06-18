from django.db import models # type: ignore
from django.utils import timezone

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    published_year = models.IntegerField()

    def __str__(self):
        return self.title

class DownloadOperation(models.Model):
    video_url = models.URLField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} - {self.video_url[:50]}... at {self.timestamp}"