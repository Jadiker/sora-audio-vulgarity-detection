import time
import logging
import subprocess
import pathlib
from contextlib import contextmanager

import whisper

logging.basicConfig(level=logging.INFO)
logging.info("Imports and logging setup complete.")

class Timer:
    '''Times operations.'''
    def __init__(self):
        self.times = []

    @property
    def last(self) -> float:
        if self.times:
            return self.times[-1]
        else:
            raise ValueError("No times recorded.")

    @contextmanager
    def time(self):
        '''Time an operation as a context manager.'''
        start = time.perf_counter()
        yield
        end = time.perf_counter()
        self.times.append(end - start)

class Transcriber:
    '''Handles audio transcription using whisper.'''

    def __init__(self):
        self.timer = Timer()
        logging.info("Loading model...")
        with self.timer.time():
            self.model = whisper.load_model("turbo")
        logging.info(f"Model loaded in {self.timer.last:.3f} seconds.")

    def transcribe(self, audio_file: str) -> str:
        '''Convert audio file to text using whisper.'''
        logging.info("Transcribing audio...")
        with self.timer.time():
            result = self.model.transcribe(audio_file)
        logging.info(f"Transcription complete in {self.timer.last:.3f} seconds.")
        text = result["text"]
        assert isinstance(text, str), "Transcription result is not a string"
        return text

def detect_vulgar(text: str, vulgar_words: list) -> bool:
    '''Detect if any vulgar words are present in the text.'''
    return any(word in text.lower() for word in vulgar_words)

def video_to_audio(video_file: str, audio_file: str):
    '''Convert video file to audio file using ffmpeg. Overwrites existing audio file.'''
    # based on https://stackoverflow.com/questions/26741116/python-extract-wav-from-video-file
    # TODO this needs sanitization if used by untrusted users
    # use ffmpeg with bitrate 160k, 2 channels, 44100 Hz frequency, no video
    command = f"ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 -vn {audio_file} -y -hide_banner -nostats -loglevel quiet"
    subprocess.call(command, shell=True)

if __name__ == "__main__":
    transcriber = Transcriber()
    with open("vulgar_language.txt", "r") as f:
        vulgar_words = [line.strip().lower() for line in f if line.strip()]
    full_filename = "dum_n.mp4"
    file_name = pathlib.Path(full_filename).stem
    file_extension = pathlib.Path(full_filename).suffix
    video_file = f"videos/{full_filename}"
    audio_file = f"audios/{file_name}.wav"
    video_to_audio(video_file, audio_file)
    text = transcriber.transcribe(audio_file)
    print(text)
    vulgar = detect_vulgar(text, vulgar_words)
    if vulgar:
        print("Vulgar language detected.")
    else:
        print("No vulgar language detected!")