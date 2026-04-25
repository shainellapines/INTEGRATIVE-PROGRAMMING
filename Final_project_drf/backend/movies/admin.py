from django.contrib import admin
from .models import Movie, Genre, Rating, Watchlist

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Rating)
admin.site.register(Watchlist)
