from django.urls import path

from accounts import views

urlpatterns = [
    path("order_history/", views.order_history, name="order_history"),
    path("logout/", views.logout_view, name="logout"),
    path("favorites/", views.favorites, name="favorites"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("", views.user_contact, name="user_contact"),
]
