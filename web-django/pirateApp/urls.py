from django.urls import path

from .views import index, compass, list_hunt_instructions, fetch_and_save_instruction, treasure

urlpatterns = [
    path("", index),
    path("compass/", compass),

    path("api/hard/list/", list_hunt_instructions), # pt debug
    path("api/hard/fetch/", fetch_and_save_instruction), # pt debug
    path("treasure/", treasure),

]
