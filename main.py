import whisper
import logging
logging.info("Imports complete.")

logging.info("Loading model...")
model = whisper.load_model("turbo")
logging.info("Model loaded.")

logging.info("Transcribing audio...")
result = model.transcribe("hello.mp3")
logging.info("Transcription complete.")

print(result["text"])