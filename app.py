import streamlit as st
import whisper
from moviepy.editor import VideoFileClip
from fpdf import FPDF
import tempfile
from googletrans import Translator

# Whisper model for transcription
model = whisper.load_model("base")

# Function to extract audio from video
def extract_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')  # Save as PCM WAV
    return audio_path

# Function to transcribe video and return time-aligned subtitles
def transcribe_with_timestamps(file_path):
    result = model.transcribe(file_path)
    segments = result['segments']
    return segments

# Function to save subtitles with timestamps to a PDF
def save_subtitles_to_pdf(subtitles, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Loop through each subtitle segment and add it to the PDF
    for segment in subtitles:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text']
        timestamp = f"{start_time:.2f} - {end_time:.2f}"
        pdf.cell(200, 10, txt=f"{timestamp}: {text}", ln=True)

    # Save the PDF
    pdf_file_path = f"{filename}.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Function to save full subtitles without timestamps to a PDF
def save_full_subtitles_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add full subtitle text as a paragraph
    pdf.multi_cell(200, 10, txt=text)

    # Save the PDF
    pdf_file_path = f"{filename}.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Function to translate subtitles to a specified language using Google Translate
def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Streamlit interface
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Drag and Drop"])

# Home Page Content
if page == "Home":
    st.title("Subtitle Generation App Overview")
    st.markdown("""
    Here’s an overview of the key concepts used in the above code:
    
    ### 1. **Streamlit**:
    Streamlit is an open-source Python framework for creating data apps quickly and easily. It simplifies the process of developing interactive web apps for machine learning, data science, and other applications.
    - **`st.sidebar`**: Creates a sidebar for navigation, where you can place buttons or input elements.
    - **`st.file_uploader`**: Allows users to upload files directly in the app, here restricted to MP4 video files.
    - **`st.button`**: A button element that triggers specific actions, like generating subtitles or downloading PDFs.
    - **`st.video`**: Displays a video in the app from a given file path.
    - **`st.download_button`**: Allows users to download a generated file, such as PDFs with subtitles.

    ### 2. **Whisper Model (from OpenAI)**:
    Whisper is a state-of-the-art speech-to-text model provided by OpenAI. It is capable of transcribing audio and video files into text.
    - **`whisper.load_model`**: Loads the Whisper model, which transcribes speech from audio files.
    - **`model.transcribe`**: This function transcribes the audio from the video file and provides timestamps along with the transcribed text.

    ### 3. **MoviePy**:
    MoviePy is a Python library for video editing, handling, and manipulation. It’s used here to extract audio from the video file.
    - **`VideoFileClip`**: Represents a video file. You can load an MP4 video file using this function.
    - **`video.audio.write_audiofile`**: Extracts the audio from the video and saves it as a separate WAV file for further processing.

    ### 4. **FPDF**:
    FPDF is a Python library for creating PDF files. It’s used here to store the generated subtitles (both with and without timestamps) into PDF format.
    - **`pdf.add_page()`**: Adds a new page to the PDF document.
    - **`pdf.cell()`**: Adds a single line of text to the PDF.
    - **`pdf.multi_cell()`**: Adds multi-line text, useful for paragraphs, to the PDF.

    ### 5. **Translation (using `googletrans`)**:
    The `googletrans` package is used to translate the transcribed subtitles into various languages.
    - **`Translator`**: A class provided by the `googletrans` package to perform translations.
    - **`translate_text` function**: This function takes the full transcribed text and translates it to the specified language.

    ### 6. **File Handling with `tempfile`**:
    The `tempfile` library is used to handle temporary file storage. In this case, it is used to save the uploaded video file and extracted audio file during processing.
    - **`tempfile.NamedTemporaryFile()`**: Creates a temporary file in the system that gets deleted after processing.

    ### 7. **How It Works**:
    1. **Upload**: The user uploads an MP4 video file using the file uploader in the Streamlit sidebar.
    2. **Extract Audio**: The app extracts the audio from the video file using MoviePy and converts it to a WAV file.
    3. **Generate Subtitles**: When the user clicks "Generate Subtitles," the Whisper model transcribes the audio into text, along with timestamps.
    4. **Display Subtitles**: Subtitles are displayed in two formats: line-by-line with timestamps, and in full paragraph form without timestamps.
    5. **Translate Subtitles**: The user can select languages and translate the generated subtitles into the selected languages.
    6. **PDF Downloads**: The app allows the user to download the generated subtitles as PDF files with timestamps for each selected language.

    ### 8. **User Interface**:
    - The **sidebar** holds a Home button and the file uploader.
    - The video is displayed in the main content area after uploading.
    - Subtitle generation and PDF download buttons are positioned under the video for a clean and intuitive layout.

    ### 9. **Error Handling and File Management**:
    - **Temporary files**: The use of temporary files ensures that uploaded files are managed efficiently without cluttering the server.
    - **Button-based operations**: Key operations (such as subtitle generation and downloading) only occur when the corresponding buttons are clicked, optimizing the app's performance and preventing unnecessary calculations.

    These concepts together form a powerful combination for creating an interactive web application capable of video processing, transcription, translation, and document generation, all within the Streamlit environment.
    """)

# Drag and Drop Page
if page == "Drag and Drop":
    st.title("Upload Your Video")
    
    # Drag and Drop File Uploader
    uploaded_file = st.file_uploader("Drag and Drop or Click to Upload MP4 Video", type="mp4")

    # If a video is uploaded, start processing
    if uploaded_file:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(uploaded_file.read())
            video_file_path = temp_video_file.name

        # Display the uploaded video in the Streamlit UI
        st.video(video_file_path)

        # Extract audio from video
        st.write("Extracting audio...")
        temp_audio_file_path = extract_audio_from_video(video_file_path)

        # Language Translation Section
        st.subheader("Select Language for Subtitles")
        target_language = st.selectbox("Choose Language", ["en", "it", "en-gb", "en-in", "es"])

        # Generate subtitles when button is clicked
        if st.button("Generate Subtitles"):
            if target_language:
                st.write("Generating subtitles in", target_language, "...")

                # Get time-aligned transcription using Whisper
                subtitles = transcribe_with_timestamps(temp_audio_file_path)

                # Translate subtitles
                translated_subtitles = []
                for segment in subtitles:
                    translated_text = translate_text(segment['text'], target_language)
                    translated_subtitles.append(translated_text)

                # Display line-by-line subtitles with timestamps
                st.write("Subtitles with Timeline (Line-by-Line):")
                full_subtitle_text = ""
                for idx, segment in enumerate(subtitles):
                    start_time = segment['start']
                    end_time = segment['end']
                    text = translated_subtitles[idx]
                    full_subtitle_text += f"{text} "
                    st.write(f"[{start_time:.2f} - {end_time:.2f}] {text}")

                # Display complete translated subtitle text without timestamps
                st.write("Full Translated Subtitles (Paragraph):")
                st.write(full_subtitle_text)

                # Save translated subtitles with timestamps to PDF
                if st.button("Download Subtitles with Timeline as PDF"):
                    pdf_path_with_timestamps = save_subtitles_to_pdf(subtitles, "Translated_Subtitles_with_Timestamps")
                    with open(pdf_path_with_timestamps, "rb") as pdf_file:
                        st.download_button(label="Download Translated Subtitles with Timestamps",
                                           data=pdf_file,
                                           file_name="Translated_Subtitles_with_Timestamps.pdf",
                                           mime="application/pdf")

                # Save full translated subtitles to PDF
                if st.button("Download Full Translated Subtitles as PDF"):
                    pdf_path_full = save_full_subtitles_to_pdf(full_subtitle_text, "Translated_Full_Subtitles")
                    with open(pdf_path_full, "rb") as pdf_file:
                        st.download_button(label="Download Full Translated Subtitles",
                                           data=pdf_file,
                                           file_name="Translated_Full_Subtitles.pdf",
                                           mime="application/pdf")
            else:
                st.warning("Please select a language to generate subtitles.")
