from django.shortcuts import render
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
                    "detailsUrl": f"/places/{place.id}/json/"
                }
            } for place in places
        ]
    }
    return render(request, 'index.html', {'geojson_data': geojson_data})
