from django.urls import path
from .views import list_hunt_instructions, fetch_and_save_instruction

urlpatterns = [
    path("api/hard/list/", list_hunt_instructions),
    path("api/hard/fetch/", fetch_and_save_instruction),
    path("api/hard/fetch", fetch_and_save_instruction),  # fără slash
]
