from django.urls import path
from . import views

urlpatterns = [
    # Hard part compass page (single input → API call → save instruction)
    path("compass/", views.compass, name="compass"),
]