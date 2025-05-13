from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from places.models import Place


def show_places(request):
    places = Place.objects.all()
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(place.lng), float(place.lat)]
                },
                "properties": {
                    "title": place.title,
                    "placeId": place.id,
                    "detailsUrl": reverse('place-json-details', args=[place.id])
                }
            } for place in places
        ]
    }
    return render(request, 'index.html', {'geojson_data': geojson_data})


def get_place_details(request, place_id):
    place = get_object_or_404(Place, pk=place_id)
    images = [item.image.url for item in place.images.all()]

    return JsonResponse({
        "title": place.title,
        "imgs": images,
        "short_description": place.short_description,
        "long_description": place.long_description,
        "coordinates": {
            "lat": float(place.lat),
            "lng": float(place.lng)
        }
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})