from django.urls import include, path, re_path

from .views import BackgroundInfoView, BackgroundView

urlpatterns = [
    path('bg/', BackgroundView.as_view(), name="bg"),
    path('bg/info/', BackgroundInfoView.as_view(), name="bg"),
]