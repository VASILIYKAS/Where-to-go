from django.db import models


class Place(models.Model):
    title = models.CharField('Название', max_length=200)
    description_short = models.CharField('Краткое описание', blank=True)
    description_long = models.CharField('Полное описание', blank=True)
    lng = models.FloatField('Долгота(longitude)')
    lat = models.FloatField('Широта(latitude)')

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.title