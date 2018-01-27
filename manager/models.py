from django.db import models

# Create your models here.


class Anime(models.Model):
    title = models.CharField(max_length=128)


class Cap(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    story_no = models.IntegerField()
    index = models.IntegerField()