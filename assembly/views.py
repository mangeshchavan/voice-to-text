import os

import assemblyai as aai
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from dotenv import load_dotenv

from assembly.forms import FileUploadForm
from assembly.models import UploadedFile


load_dotenv()


def upload_file(request):
    if request.method == "POST":
        # Log headers for debugging AJAX requests
        print("--- UPLOAD REQUEST ---")
        print("HEADERS:", request.headers)

        form = FileUploadForm(request.POST, request.FILES)

        # Check if it's an AJAX request
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            print("AJAX request detected.")
            if form.is_valid():
                form.save()
                print("Form is valid. File saved.")
                return JsonResponse({"success": True})
            else:
                print("Form is invalid. Errors:", form.errors.as_json())
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            # Handle non-AJAX form submission as a fallback
            print("Standard form submission detected.")
            if form.is_valid():
                form.save()
                print("Form is valid. File saved. Redirecting.")
                return redirect("file_list")
            else:
                # Re-render the page with form errors for non-AJAX
                print("Form is invalid. Errors:", form.errors)
                return render(request, "uploads/upload.html", {"form": form})

    else:
        form = FileUploadForm()

    return render(request, "uploads/upload.html", {"form": form})


def file_list(request):
    files = UploadedFile.objects.all().order_by("-uploaded_at")  # Show newest first
    print(f"Found {files.count()} files in database")  # Debug
    for file in files:
        print(f"File: {file.file.name}, uploaded at: {file.uploaded_at}")  # Debug
    return render(request, "uploads/file_list.html", {"files": files})


def delete_file(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk)
    if request.method == "POST":
        file.delete()
        return redirect("file_list")
    return render(request, "uploads/delete_file.html", {"file": file})


def convert_audio_to_text(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)

    # --- Start transcription job ---
    language = request.POST.get("language", "en")

    config = aai.TranscriptionConfig(
        language_code=language,
        punctuate=True,
        format_text=False,
        speaker_labels=True,
        # word_boost is for boosting existing words, not for custom vocabulary
        # word_boost=["HappyThoughts"],
        custom_spelling={
            # Map a simple ASCII placeholder to the desired non-ASCII output
            "HappyThoughts": ["हैपी थॉटस"],
            "थॉटस": ["थार्स"],
            "शुभेच्छा": ["शुभिक्षा"],
        },
    )

    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    transcriber = aai.Transcriber(config=config)

    try:
        # Submit the file for transcription
        transcript = transcriber.submit(uploaded_file.file.path)

        # Save the transcript ID and initial status to the model
        uploaded_file.transcript_id = transcript.id
        uploaded_file.status = transcript.status  # Should be 'queued' or 'processing'
        uploaded_file.save()

        # Redirect to the waiting page
        return redirect("wait_for_conversion", pk=uploaded_file.pk)

    except Exception as e:
        # Handle potential API errors
        print(f"Error submitting file to AssemblyAI: {e}")
        # Optionally, add a message to the user
        return redirect("file_list")  # Redirect back with an error message later


def wait_for_conversion(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    return render(request, "uploads/convert.html", {"file": uploaded_file})


def check_transcription_status(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    if not uploaded_file.transcript_id:
        return JsonResponse(
            {"status": "error", "message": "No transcript ID found."}, status=400
        )

    try:
        # --- THE CORRECT FIX (from documentation) ---
        transcript = aai.Transcript.get_by_id(uploaded_file.transcript_id)
        # --- End Fix ---

        uploaded_file.status = transcript.status

        response_data = {"status": transcript.status}

        if transcript.status == aai.TranscriptStatus.completed:
            # Save the final text and utterances
            utterances_list = []
            for utterance in transcript.utterances:
                utterance_text = f"Speaker {utterance.speaker}: {utterance.text}"
                utterances_list.append(utterance_text)

            final_text = "\n".join(utterances_list)
            uploaded_file.text = final_text
            response_data["text"] = final_text

            # --- FIX: Re-implement .txt file generation ---
            txt_file_path = os.path.join(
                settings.MEDIA_ROOT,
                f"{os.path.splitext(uploaded_file.file.name)[0]}.txt",
            )
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            # --- End Fix ---

        elif transcript.status == aai.TranscriptStatus.error:
            response_data["message"] = transcript.error

        uploaded_file.save()
        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error checking status: {e}")
        return JsonResponse(
            {"status": "error", "message": "Failed to check status."}, status=500
        )


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
