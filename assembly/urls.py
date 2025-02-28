from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload_file, name="upload_file"),
    path("delete/<int:pk>/", views.delete_file, name="delete_file"),
    path("convert/<int:pk>/", views.convert_audio_to_text, name="convert"),
    path("download/<int:pk>/", views.download_text_file, name="download_text"),
    path("", views.file_list, name="file_list"),
]
