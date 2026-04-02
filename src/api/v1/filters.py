import django_filters

from cosmetics_shop.models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    brand = django_filters.CharFilter(field_name="brand__slug")
    group = django_filters.CharFilter(field_name="group__slug")
    category = django_filters.CharFilter(field_name="group__category__slug")

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    class Meta:
        model = Product
        fields = ["brand", "group", "category"]
