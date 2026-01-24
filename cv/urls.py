from django.urls import path
from .views import cv_view, cv_pdf

urlpatterns = [
    path("", cv_view, name="cv"),
    path("pdf/", cv_pdf, name="cv_pdf"),
]
