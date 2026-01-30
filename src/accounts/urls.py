from django.urls import path

from accounts import views

urlpatterns = [
    path("activate/", views.activate_account, name="activate"),
    path("order_history/", views.order_history, name="order_history"),
    path("logout/", views.logout_view, name="logout"),
    path("favorites/", views.favorites, name="favorites"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path(
        "favorites/remove/<int:product_id>/",
        views.remove_from_favorites,
        name="remove_from_favorites",
    ),
    path("", views.user_contact, name="user_contact"),
]
