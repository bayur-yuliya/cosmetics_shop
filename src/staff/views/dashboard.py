from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from cosmetics_shop.models import Favorite
from staff.services.dashboard_service import  get_today_stats, get_month_stats


@permission_required("staff.dashboard_view", raise_exception=False)
def index(request: HttpRequest) -> HttpResponse:
    today = timezone.now().date()

    today_stats = get_today_stats()
    month_stats = get_month_stats(today)

    max_favorite = (
        Favorite.objects
        .annotate(num_product=Count("product"))
        .order_by("-num_product")
        .select_related("product__group")[:3]
    )

    current_year = timezone.now().year
    years = range(current_year - 5, current_year + 1)

    return render(
        request,
        "staff/dashboard.html",
        {
            "title": "Главная страница",
            "number_of_completed_orders_today": today_stats["total_orders"],
            "number_of_orders_per_month": month_stats["total_orders"],
            "summ_bill": month_stats["total_revenue"],
            "average_bill": month_stats["avg_check"],
            "max_favorite": max_favorite,
            "years": years,
            "current_year": current_year,
        },
    )
