import os

from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    transcript_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="pending", blank=True, null=True)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
