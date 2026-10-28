from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.view_listing, name="listing_detail"),
    path("my_listings", views.view_my_listings, name="view_my_listings"),
    path("listing/<int:listing_id>/disable", views.disable_listing, name="disable_listing"),
    path("my-wins/", views.view_my_wins, name="my_wins"),
    path("listing/<int:listing_id>/bid", views.add_bid, name="add_bid"),
    path("listing/<int:listing_id>/comment", views.add_comment, name="add_comment"),
    path("add_to_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("watchlist", views.view_watchlist, name="view_watchlist"),
    path("categories", views.view_categories, name="view_categories"),
    path("categories/<str:category_name>", views.view_category_listings, name="category_listings")
]
