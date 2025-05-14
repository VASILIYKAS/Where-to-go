import json
import os
from urllib.parse import urlparse, unquote

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from places.models import Place, PlaceImage


class Command(BaseCommand):
    help = 'Команда для занесения в базу данных мест из json файла с GitHub'

    def add_arguments(self, parser):
        parser.add_argument('json_url', type=str,
                            help='URL JSON-файла на GitHub')

    def handle(self, *args, **options):
        json_url = options['json_url']

        response = requests.get(json_url)
        response.raise_for_status()
        raw_place = response.json()

        place, created = Place.objects.get_or_create(
            title=raw_place['title'],
            defaults={
                'short_description': raw_place['description_short'],
                'long_description': raw_place['description_long'],
                'lng': raw_place['coordinates']['lng'],
                'lat': raw_place['coordinates']['lat']
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Создано новое место: {place.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Место уже существует: {place.title}'))

        self.download_images(place, raw_place.get('imgs', []))

    def download_images(self, place, image_urls):
        for position, url in enumerate(image_urls, start=1):
            response = requests.get(url)
            response.raise_for_status()

            parsed_url = urlparse(url)
            filename = os.path.basename(unquote(parsed_url.path))

            place_image = PlaceImage(place=place, position=position)

            place_image.image.save(
                filename,
                ContentFile(response.content),
                save=True
            )