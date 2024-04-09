from django.urls import path
from .views import home, get_recommendations, get_movie_poster_url_tmdb

urlpatterns = [
    path('', home, name='home'),  # URL route for the home view
    path('', get_recommendations, name='get_recommendations'),
    path('', get_movie_poster_url_tmdb, name='get_movie_poster_url_tmdb'),
]
