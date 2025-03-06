import os

import assemblyai as aai
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from dotenv import load_dotenv

from assembly.forms import FileUploadForm
from assembly.models import UploadedFile


load_dotenv()


def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("file_list")
    else:
        form = FileUploadForm()
    return render(request, "uploads/upload.html", {"form": form})


def file_list(request):
    files = UploadedFile.objects.all()
    return render(request, "uploads/file_list.html", {"files": files})


def delete_file(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    if request.method == "POST":
        file.delete()
        return redirect("file_list")
    return render(request, "uploads/delete_file.html", {"file": file})


def convert_audio_to_text(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    word_boost = ["हैपी थॉटस"]  # noqa
    language = request.POST.get("language", "en")
    print(f"language {language}")
    config = aai.TranscriptionConfig(
        # language_code='en',
        language_code=language,
        punctuate=True,
        format_text=False,
    )
    config.set_custom_spelling({"थॉटस": ["थार्स"], "शुभेच्छा": ["शुभिक्षा"]})
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "default_api_key")
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(file.file.path)

    # Save the transcription text to the UploadedFile model
    file.text = transcript.text
    file.save()
    txt_file_path = os.path.join(
        settings.MEDIA_ROOT, f"{os.path.splitext(file.file.name)[0]}.txt"
    )
    with open(txt_file_path, "w") as f:
        f.write(transcript.text)
    return redirect("file_list")


def download_text_file(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    txt_file_name = f"{os.path.splitext(file.file.name)[0]}.txt"
    txt_file_path = os.path.join(settings.MEDIA_ROOT, txt_file_name)

    if os.path.exists(txt_file_path):
        with open(txt_file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="text/plain; charset=utf-8")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{txt_file_name}"'  # noqa
            return response
    else:
        return HttpResponse("Text file not found.", status=404)
