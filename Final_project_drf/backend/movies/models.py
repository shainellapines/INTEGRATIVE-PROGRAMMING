from django.db import models
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    poster = models.URLField(blank=True)
    popularity = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE, 
        related_name='ratings'   # ✅ FIXED
    )

    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ('user', 'movie')


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE,
        related_name='watchlists'  # optional but clean
    )

    class Meta:
        unique_together = ('user', 'movie')

from rest_framework import serializers
from .models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    # For READ (display)
    genres = GenreSerializer(many=True, read_only=True)

    # For WRITE (create/update)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        write_only=True
    )

    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'

    def create(self, validated_data):
        genres = validated_data.pop('genre_ids', [])
        movie = Movie.objects.create(**validated_data)
        movie.genres.set(genres)
        return movie

    def update(self, instance, validated_data):
        genres = validated_data.pop('genre_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if genres is not None:
            instance.genres.set(genres)

        instance.save()
        return instance

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['user']  # user auto-set


class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source='movie',
        write_only=True
    )

    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'movie_id']
        read_only_fields = ['user']
