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


class IsAdminOrOwnerReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if request.method in SAFE_METHODS:
            return obj.client and obj.client.user == request.user

        return False
