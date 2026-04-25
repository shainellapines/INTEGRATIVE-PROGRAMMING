from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, GenreViewSet, RatingViewSet, WatchlistViewSet

router = DefaultRouter()
router.register('movies', MovieViewSet)
router.register('genres', GenreViewSet)
router.register('ratings', RatingViewSet, basename='rating')
router.register('watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = router.urls