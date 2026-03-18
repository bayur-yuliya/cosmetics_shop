from django.urls import path

from accounts.views import auth, favorites, user_section

urlpatterns = [
    # auth
    path("activate/", auth.activate_account, name="activate"),
    # favorites
    path(
        "favorites/remove/<int:product_id>/",
        favorites.remove_from_favorites,
        name="remove_from_favorites",
    ),
    path("favorites/", favorites.favorites, name="favorites"),
    # user_section
    path("order_history/", user_section.order_history, name="order_history"),
    path(
        "delete/reset/",
        user_section.reset_account_deletion,
        name="reset_account_deletion",
    ),
    path("delete/", user_section.delete_account, name="delete_account"),
    path("", user_section.user_contact, name="user_contact"),
]
