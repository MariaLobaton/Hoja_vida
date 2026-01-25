from django.urls import path
from .views import cv_view, editar_perfil, cv_pdf
from . import views

urlpatterns = [
    path("", cv_view, name="cv_view"),
    path("editar/", editar_perfil, name="editar_perfil"),
    path("pdf/", cv_pdf, name="cv_pdf"),
    path("garage/", views.garage_list, name="garage_list"),

]
