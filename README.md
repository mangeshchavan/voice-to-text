# voice-to-text
Audio Upload and Transcription Service This project offers a streamlined service for uploading audio files and converting them into text using the AssemblyAI API. It enables users to transform spoken content into written format, making it suitable for note-taking, content creation, and enhancing accessibility.


# Assembly Project

## Project Description

The Assembly Project is a Django web application that allows users to upload audio files, convert them to text using AssemblyAI's transcription service, and manage their uploaded files. Users can view a list of uploaded files, delete files, and download the transcribed text. The application is designed to be user-friendly and leverages Bootstrap for responsive design.

## Features

- Upload audio files
- Convert audio files to text
- View a list of uploaded files
- Delete uploaded files
- Download transcribed text files

## Requirements

- Python 3.x
- Django 5.0.3 or higher
- AssemblyAI API key (for transcription)

## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Obtain your AssemblyAI API Key**:
   - Visit [AssemblyAI's official website](https://www.assemblyai.com/).
   - Sign up for a new account or log in if you already have one.
   - Access your dashboard and find the section labeled "API Keys" to copy your API key.

3. **Install Poetry** (if you haven't already):

   Follow the instructions on the [Poetry installation page](https://python-poetry.org/docs/#installation).

4. **Install dependencies**:

   ```bash
   poetry install
   ```

5. **Set up environment variables**:

   Create a `.env` file in the root directory of the project and add your AssemblyAI API key:

   ```plaintext
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

6. **Run database migrations**:

   ```bash
   poetry run python manage.py migrate
   ```

7. **Run the development server**:

   ```bash
   poetry run python manage.py runserver
   ```

8. **Access the application**:

   Open your web browser and go to `http://127.0.0.1:8000/upload/` to start using the application.

## Usage

- To upload a file, navigate to the upload page and select an audio file.
- After uploading, you will be redirected to the file list page where you can see all uploaded files.
- You can convert the audio to text by selecting a file and choosing the desired language.
- You can also delete files or download the transcribed text from the file list page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
