from django.urls import path
from .views import cv_view, cv_pdf, editar_perfil

urlpatterns = [
    path("", cv_view, name="cv"),
    path("pdf/", cv_pdf, name="cv_pdf"),
    path("editar/", editar_perfil, name="editar_perfil"),
]
