from django.http import JsonResponse

from cosmetics_shop.services.nova_poshta_service import NovaPoshtaAPI


def cities_view(request):
    """Endpoint for autocompletion of cities"""
    search = request.GET.get("q", "").strip()

    if len(search) < 2:
        return JsonResponse({"data": []})

    api = NovaPoshtaAPI()
    response_data = api.get_cities(search)

    data = response_data.get("data", []) if response_data.get("success") else []

    return JsonResponse({"data": data})


def warehouses_view(request):
    """Endpoint for loading branches after selecting a city"""
    city_ref = request.GET.get("city_ref", "")

    if not city_ref:
        return JsonResponse({"data": []})

    api = NovaPoshtaAPI()
    response_data = api.get_warehouses(city_ref)

    data = response_data.get("data", []) if response_data.get("success") else []

    return JsonResponse({"data": data})
