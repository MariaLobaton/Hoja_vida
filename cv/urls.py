from django.urls import path
from . import views

urlpatterns = [
    path("", views.cv_view, name="cv"),
    path("pdf/", views.cv_pdf, name="cv_pdf"),
]
