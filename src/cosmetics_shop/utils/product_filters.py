import logging

logger = logging.getLogger(__name__)


class ProductFilter:
    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset
        self.form_data = request.GET or None
        self._prepare_sort_context()

    def apply_filters(self, form):
        """Applies filters from forms"""

        if not form.is_valid():
            logger.debug("Filter form invalid")
            return

        logger.debug("Applying filters", extra={"data": form.cleaned_data})

        if form.cleaned_data["group"]:
            self.queryset = self.queryset.filter(group__in=form.cleaned_data["group"])

        if form.cleaned_data["tags"]:
            self.queryset = self.queryset.filter(tags__in=form.cleaned_data["tags"])

        if form.cleaned_data["min_price"] is not None:
            self.queryset = self.queryset.filter(
                price__gte=form.cleaned_data["min_price"]
            )

        if form.cleaned_data["max_price"] is not None:
            self.queryset = self.queryset.filter(
                price__lte=form.cleaned_data["max_price"]
            )

        if form.cleaned_data["brand"]:
            self.queryset = self.queryset.filter(brand__in=form.cleaned_data["brand"])

        if form.cleaned_data["name"]:
            name = form.cleaned_data["name"].lower()
            self.queryset = self.queryset.filter(name__icontains=name)

    def _get_param(self, key, default=None):
        """Getting parameters from GET request"""
        return self.form_data.get(key, default) if self.form_data else default

    def _prepare_sort_context(self):
        """Prepares the context for sorting once at initialization"""
        self.current_sort = self._get_param("sort", None)
        self.current_direction = self._get_param("direction", "desc")
        self.sort_options = self._get_sort_options_with_urls()

    def _get_sort_options_with_urls(self):
        """Returns sorting options with pre-built URLs"""
        options = [
            {"value": "price", "label": "По цене"},
            {"value": "name", "label": "По названию"},
        ]

        for option in options:
            if option["value"] is None:
                option["url"] = ""
            else:
                option["url"] = self._build_sort_url(option["value"])
            option["is_active"] = self.current_sort == option["value"]

        return options

    def _build_sort_url(self, sort_field):
        """Internal method for constructing URLs"""
        params = self.request.GET.copy()
        params["sort"] = sort_field

        if not sort_field or sort_field.lower() == "none":
            params.pop("sort", None)
            params.pop("direction", None)
            return f"?{params.urlencode()}" if params else "?"

        if params.get("sort") == sort_field and params.get("direction") == "asc":
            params["direction"] = "desc"
        else:
            params["direction"] = "asc"

        return f"?{params.urlencode()}"

    def get_sort_options(self):
        """Returns predefined sorting options from a URL"""
        return self.sort_options

    def get_sort_params(self):
        """Getting sort parameters safely"""
        sort_by = self._get_param("sort", None)
        direction = self._get_param("direction", "desc")
        allowed_fields = {"price", "name"}
        allowed_directions = {"asc", "desc"}

        sort_by = sort_by if sort_by in allowed_fields else None
        direction = direction if direction in allowed_directions else "desc"

        return sort_by, direction

    def apply_sorting(self):
        """Applies sorting, storing missing items at the end"""

        sort_by, direction = self.get_sort_params()

        logger.debug(
            "Applying sorting",
            extra={"sort_by": sort_by, "direction": direction},
        )

        qs = self.queryset.annotate_availability()

        if not sort_by:
            return qs.order_by("is_out_of_stock", "-id")

        sort_field = f"-{sort_by}" if direction == "desc" else sort_by
        return qs.order_by("is_out_of_stock", sort_field)

    def get_clear_sort_url(self):
        """Return URL without sorting parameters, keeping filters"""
        params = self.request.GET.copy()
        params.pop("sort", None)
        params.pop("direction", None)
        return f"?{params.urlencode()}" if params else "?"
