from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Avg, Count
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import *


# =========================
# 🎬 MOVIE VIEWSET
# =========================
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    # 🔍 SEARCH + FILTER
    def get_queryset(self):
        qs = Movie.objects.annotate(
            avg_rating=Avg('ratings__score')
        ).prefetch_related('genres')

        search = self.request.query_params.get('search')
        genre = self.request.query_params.get('genre', '').lower()

        if search:
            qs = qs.filter(title__icontains=search)

        if genre:
            qs = qs.filter(genres__name__icontains=genre).distinct()

        return qs.order_by('-avg_rating', '-popularity')

    # ⭐ RECOMMENDATION SYSTEM
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        mood = request.query_params.get('mood', '').lower()

        movies = Movie.objects.annotate(
            avg_rating=Avg('ratings__score')
        ).prefetch_related('genres')

        mood_map = {
            "happy": ["comedy", "romance", "animation"],
            "sad": ["drama", "romance"],
            "excited": ["action", "sci-fi", "fantasy"],
            "scary": ["horror", "thriller", "crime"],
            "fantasy": ["fantasy", "animation", "sci-fi"]
        }

        results = []

        for m in movies:
            avg_rating = m.avg_rating or 0
            popularity = m.popularity or 0
            genre_names = [g.name.lower() for g in m.genres.all()]

            genre_match = 0
            if mood in mood_map:
                genre_match = sum(
                    1 for g in genre_names if g in mood_map[mood]
                )

            score = (
                (avg_rating * 0.5) +
                (genre_match * 2) +
                ((popularity / 100) * 0.2)
            )

            results.append((m, score))

        results.sort(key=lambda x: x[1], reverse=True)
        response = []
        for m, score in results:
            data = MovieSerializer(m).data
            data["match_score"] = round(score, 2)
            response.append(data)

        return Response(response)
    # 🎬 SIMILAR MOVIES
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        movie = self.get_object()
        genres = movie.genres.all()

        similar = Movie.objects.filter(
            genres__in=genres
        ).exclude(id=movie.id).annotate(
            shared_genres=Count('genres'),
            avg_rating=Avg('ratings__score')
        ).order_by('-shared_genres', '-avg_rating').distinct()

        return Response(MovieSerializer(similar, many=True).data)

    # 🔥 TRENDING
    @action(detail=False, methods=['get'])
    def trending(self, request):
        movies = Movie.objects.annotate(
            avg_rating=Avg('ratings__score')
        ).prefetch_related('genres').order_by('-popularity')[:10]

        return Response(MovieSerializer(movies, many=True).data)


# =========================
# 🎭 GENRE VIEWSET
# =========================
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


# =========================
# ⭐ RATING VIEWSET
# =========================
class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer

    def get_queryset(self):
        username = self.request.headers.get('X-Username')

        if not username:
            return Rating.objects.none()

        user, _ = User.objects.get_or_create(username=username)
        return Rating.objects.filter(user=user)

    def perform_create(self, serializer):
        username = self.request.headers.get('X-Username')

        if not username:
            raise ValidationError("Username required")

        user, _ = User.objects.get_or_create(username=username)

        movie = serializer.validated_data['movie']
        score = serializer.validated_data['score']

        rating, created = Rating.objects.update_or_create(
            user=user,
            movie=movie,
            defaults={'score': score}
        )

        serializer.instance = rating


# =========================
# ❤️ WATCHLIST VIEWSET
# =========================
class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer

    def get_queryset(self):
        username = self.request.headers.get('X-Username')

        if not username:
            return Watchlist.objects.none()

        user, _ = User.objects.get_or_create(username=username)
        return Watchlist.objects.filter(user=user)

    def perform_create(self, serializer):
        username = self.request.headers.get('X-Username')

        if not username:
            raise ValidationError("Username required")

        user, _ = User.objects.get_or_create(username=username)

        Watchlist.objects.get_or_create(
            user=user,
            movie=serializer.validated_data['movie']
        )