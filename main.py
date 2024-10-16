from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
import os
import whisper
from moviepy.editor import VideoFileClip
from fpdf import FPDF
import tempfile
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Whisper model for transcription
model = whisper.load_model("base")

# Serve static files for the HTML interface
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# Function to save time-aligned subtitles to a PDF
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

# HTML form for file upload
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Video to Subtitles with Timestamps</title>
</head>
<body>
    <h1>Upload MP4 Video to Generate Time-Aligned Subtitles</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".mp4" required>
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def main():
    return html_content

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.mp4'):
        return {"error": "File format not supported. Please upload an MP4 file."}
    
    # Save the uploaded video file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(await file.read())
        video_file_path = temp_video_file.name

    # Extract audio from video
    temp_audio_file_path = extract_audio_from_video(video_file_path)

    # Get time-aligned transcription using Whisper
    subtitles = transcribe_with_timestamps(temp_audio_file_path)

    # Save subtitles with timestamps to PDF
    pdf_path = save_subtitles_to_pdf(subtitles, "Subtitles_with_Timestamps")

    # Cleanup temporary files
    os.remove(video_file_path)
    os.remove(temp_audio_file_path)

    # Return response with subtitles
    return {
        "message": "Transcription successful!",
        "subtitles": subtitles,
        "pdf_path": pdf_path
    }

@app.get("/download/subtitles")
def download_subtitles_pdf():
    return FileResponse("Subtitles_with_Timestamps.pdf", media_type='application/pdf', filename="Subtitles_with_Timestamps.pdf")

# HTML for displaying subtitles with timestamps
@app.get("/display-subtitles")
async def display_subtitles():
    # Load subtitles and display them with timestamps (for demonstration purposes)
    subtitles = [
        {"start": 0.5, "end": 2.0, "text": "Hello, welcome to the video."},
        {"start": 2.5, "end": 5.0, "text": "This is a demo of subtitle generation."}
    ]
    html_subtitles = "<h2>Subtitles</h2><ul>"
    for subtitle in subtitles:
        html_subtitles += f"<li>{subtitle['start']:.2f} - {subtitle['end']:.2f}: {subtitle['text']}</li>"
    html_subtitles += "</ul>"
    
    return HTMLResponse(content=html_subtitles)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
