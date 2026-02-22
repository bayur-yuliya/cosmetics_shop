from django.urls import path

from accounts.views import auth, favorites, user_section

urlpatterns = [
    # auth
    path("login/", auth.login_view, name="account_login"),
    path("activate/", auth.activate_account, name="activate"),
    path("logout/", auth.logout_view, name="logout"),
    # favorites
    path(
        "favorites/remove/<int:product_id>/",
        favorites.remove_from_favorites,
        name="remove_from_favorites",
    ),
    path("favorites/", favorites.favorites, name="favorites"),
    # user_section
    path("order_history/", user_section.order_history, name="order_history"),
    path("delete_account/", user_section.delete_account, name="delete_account"),
    path("", user_section.user_contact, name="user_contact"),
]
