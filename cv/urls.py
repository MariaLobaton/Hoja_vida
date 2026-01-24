from django.urls import path
from .views import cv_view, editar_perfil, cv_pdf

urlpatterns = [
    path("", cv_view, name="cv_view"),
    path("editar/", editar_perfil, name="editar_perfil"),
    path("pdf/", cv_pdf, name="cv_pdf"),
]
