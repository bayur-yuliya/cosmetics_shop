class ProductFilter:

    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset
        self.form_data = request.GET or None
        self._prepare_sort_context()

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

    def _prepare_sort_context(self):
        """Prepares the context for sorting once at initialization"""
        self.current_sort = self.request.GET.get('sort', 'id')
        self.current_direction = self.request.GET.get('direction', 'desc')
        self.sort_options = self._get_sort_options_with_urls()

    def _get_sort_options_with_urls(self):
        """Returns sorting options with pre-built URLs"""
        options = [
            {'value': 'price', 'label': 'По цене'},
            {'value': 'name', 'label': 'По названию'},
        ]

        for option in options:
            option['url'] = self._build_sort_url(option['value'])
            option['is_active'] = (self.current_sort == option['value'])

        return options

    def _build_sort_url(self, sort_field):
        """Internal method for constructing URLs"""
        params = self.request.GET.copy()
        params['sort'] = sort_field

        if params.get('sort') == sort_field and params.get('direction') == 'asc':
            params['direction'] = 'desc'
        else:
            params['direction'] = 'asc'

        return f"?{params.urlencode()}"

    def get_sort_options(self):
        """Returns predefined sorting options from a URL"""
        return self.sort_options

    def get_sort_params(self):
        """Getting sort parameters safely"""

        sort_by = self.request.GET.get("sort", "id")
        direction = self.request.GET.get('direction', 'desc')
        allowed_fields = {'price', 'name', 'id'}
        allowed_directions = {'asc', 'desc'}

        sort_by = sort_by if sort_by in allowed_fields else 'id'
        direction = direction if direction in allowed_directions else 'desc'

        return sort_by, direction

    def apply_sorting(self):
        """Applies sorting to queryset"""
        sort_by, direction = self.get_sort_params()

        if direction == 'desc':
            sort_field = f'-{sort_by}'
        else:
            sort_field = sort_by

        return self.queryset.order_by(sort_field)
