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
