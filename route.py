import openrouteservice as ors


client = ors.Client(key="5b3ce3597851110001cf624837a94f6f86e844b198f1c81cfefd7b77")

mode_map = {
    "Voiture": "driving-car",
    "Camion": "driving-hgv",
    "Vélo": "cycling-regular",
    "Vélo de route": "cycling-road",
    "VTT": "cycling-mountain",
    "Pédestre": "foot-walking",
    "Randonnée": "foot-hiking",
}


def get_route(coordinates, mode):
    try:
        route = client.directions(
            coordinates=[list(reversed(c)) for c in coordinates],
            profile=mode_map[mode],
            format="geojson",
            optimize_waypoints=True if len(coordinates) > 3 else None,
        )
    except ors.exceptions.ApiError:  # 403 ({'error': 'Quota exceeded'}) for optimize
        route = client.directions(
            coordinates=[list(reversed(c)) for c in coordinates],
            profile=mode_map[mode],
            format="geojson",
        )
    return [list(reversed(c)) for c in route["features"][0]["geometry"]["coordinates"]]
