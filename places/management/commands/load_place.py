import os
import time
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
            self.stdout.write(self.style.SUCCESS(
                f'Создано новое место: {place.title}'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Место уже существует: {place.title}'))

        self.download_images(place, raw_place.get('imgs', []))

    def download_images(self, place, image_urls):
        success_count = 0
        for position, url in enumerate(image_urls, start=1):
            try:
                self.process_single_image(place, position, url)
                success_count += 1
            except requests.exceptions.HTTPError as e:
                self.stderr.write(self.style.ERROR(
                    f'HTTP ошибка ({url}): {str(e)}'))
            except requests.exceptions.ConnectionError as e:
                self.stderr.write(self.style.ERROR(
                    f'Ошибка соединения ({url}): {str(e)}.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f'Неизвестная ошибка ({url}): {str(e)}'))

        total = len(image_urls)
        if success_count == total:
            self.stdout.write(self.style.SUCCESS(
                f'Все {total} изображения "{place.title}" успешно загружены.'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Успешно загружено {success_count} из {total} изображений для "{place.title}"'))

    def process_single_image(self, place, position, url):
        self.stdout.write(f'Загрузка изображения {position}')

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            parsed_url = urlparse(url)
            filename = os.path.basename(unquote(parsed_url.path))

            PlaceImage.objects.create(
                place=place,
                position=position,
                image=ContentFile(response.content, name=filename)
            )
            return

        except requests.exceptions.ConnectionError as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка соединения ({url}): {str(e)}.'))
            time.sleep(3)
            return