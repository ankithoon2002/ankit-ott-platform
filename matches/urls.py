from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('watch/<int:match_id>/', views.watch_match, name='watch_match'),
    path('watch-content/<str:content_type>/<int:tmdb_id>/', views.watch_movie, name='watch_movie'),
    path('watchlist/', views.my_watchlist, name='my_watchlist'),
    path('watchlist/toggle/<int:item_id>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('api/score/<int:match_id>/', views.get_match_score, name='get_match_score'),
    path('sync-movies/', views.auto_sync_movies, name='auto_sync_movies'),
]
