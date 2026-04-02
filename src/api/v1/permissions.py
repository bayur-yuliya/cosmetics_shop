from rest_framework.permissions import SAFE_METHODS, BasePermission


class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.method in ["POST", "PUT", "PATCH"]:
            return request.user.has_perm("cosmetics_shop.change_product")

        if request.method == "DELETE":
            return request.user.has_perm("cosmetics_shop.delete_product")

        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
