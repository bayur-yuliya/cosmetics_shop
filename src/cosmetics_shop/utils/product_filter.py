class ProductFilter:

    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset
        self.form_data = request.GET or None

    def apply_filters(self, form):
        """Applies filters from forms"""

        if form.is_valid():
            name = form.cleaned_data["name"]
            group = form.cleaned_data["group"]
            tags = form.cleaned_data["tags"]
            min_price = form.cleaned_data["min_price"]
            max_price = form.cleaned_data["max_price"]
            brand = form.cleaned_data["brand"]

            if group:
                self.queryset = self.queryset.filter(group__in=group)
            if tags:
                self.queryset = self.queryset.filter(tags__in=tags)
            if min_price is not None:
                self.queryset = self.queryset.filter(price__gte=min_price * 100, stock__gte=1)
            if max_price is not None:
                self.queryset = self.queryset.filter(price__lte=max_price * 100)
            if brand:
                self.queryset = self.queryset.filter(brand__in=brand)
            if name:
                name_lower = name.lower()
                self.queryset = [obj for obj in self.queryset if name_lower in obj.name.lower()]

        return self.queryset
