from rest_framework.permissions import SAFE_METHODS, BasePermission


class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.method in ["POST", "PUT", "PATCH"]:
            return request.user.has_perm("products.change_product")

        if request.method == "DELETE":
            return request.user.has_perm("products.delete_product")

        return False
