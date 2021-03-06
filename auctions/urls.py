from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_auction", views.add_auction, name="add_auction"),
    path('<int:auction_id>', views.list_pages, name="list_pages"),
    path('comments', views.comments, name="comments"),
    path('category/<str:category>', views.category, name="category"),
    path('watchlist', views.watchlist, name="watchlist"),
]
