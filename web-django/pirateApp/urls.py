from django.urls import path
from .views import index, compass, list_hunt_instructions, fetch_and_save_instruction

urlpatterns = [
    path("", index),
    path("compass/", compass),

    # rămân utile pentru debug/React
    path("api/hard/list/", list_hunt_instructions),
    path("api/hard/fetch/", fetch_and_save_instruction),
]
