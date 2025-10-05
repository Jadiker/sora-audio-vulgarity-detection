import time
import logging
import subprocess
from pathlib import Path
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

    def __init__(self, prompt: str=""):
        self.prompt = prompt
        self.timer = Timer()
        logging.info("Loading model...")
        with self.timer.time():
            self.model = whisper.load_model("turbo")
        logging.info(f"Model loaded in {self.timer.last:.3f} seconds.")

    def transcribe(self, audio_file: str) -> str:
        '''Convert audio file to text using whisper.'''
        # uncomment to see (likely vulgar) prompt
        # logging.info(f"Transcribing audio with prompt: '{self.prompt}'")
        with self.timer.time():
            result = self.model.transcribe(
                audio_file,
                task="transcribe",
                # condition_on_previous_text=False, # had no impact # TODO delete
                initial_prompt=self.prompt
            )
        logging.info(f"Transcription complete in {self.timer.last:.3f} seconds.")
        text = result["text"]
        assert isinstance(text, str), "Transcription result is not a string"
        return text

def detect_vulgar(text: str, vulgar_phrases: list) -> bool:
    '''Detect if any vulgar phrases are present in the text.'''
    return any(phrase in text.lower() for phrase in vulgar_phrases)

def video_to_audio(video_file: str, audio_file: str):
    '''
    Convert video file to audio file using ffmpeg. Overwrites existing audio file.

    Based on https://stackoverflow.com/questions/26741116/python-extract-wav-from-video-file
    '''
    # delete existing audio file if it exists
    Path(audio_file).unlink(missing_ok=True)

    # check that the input file exists
    if not Path(video_file).exists():
        raise FileNotFoundError(f"Video file '{video_file}' does not exist.")
    
    # TODO this needs sanitization if used by untrusted users
    # use ffmpeg with bitrate 160k, 2 channels, 44100 Hz frequency, no video, overwrite
    command = f"ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 -vn {audio_file} -y -hide_banner -nostats -loglevel error"

    try:
        res = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"ffmpeg failed (exit {e.returncode}) while creating '{audio_file}'.\nSTDERR:\n{e.stderr}"
        ) from e

    if not Path(audio_file).exists():
        raise FileNotFoundError(
            f"ffmpeg reported success but '{audio_file}' was not created."
        )

if __name__ == "__main__":
    # Change this to test different files
    full_filename = "empty_example.mp4"

    file_name = Path(full_filename).stem
    file_extension = Path(full_filename).suffix

    video_file = f"videos/{full_filename}"
    audio_file = f"audios/{file_name}.wav"

    vulgar_phrases_file = "vulgar_phrases.txt"
    with open(vulgar_phrases_file, "r") as f:
        vulgar_phrases = [line.strip().lower() for line in f if line.strip()]
    logging.info(f"Processing file: {video_file}")
    video_to_audio(video_file, audio_file)
    # the prompt biases it towards hearing vulgar words
    # (some examples are not detected without the prompt)
    transcriber_prompt = f"{' '.join(vulgar_phrases)}."
    transcriber = Transcriber(prompt=transcriber_prompt)
    text = transcriber.transcribe(audio_file)
    print(text)
    vulgar = detect_vulgar(text, vulgar_phrases)
    if vulgar:
        print("Vulgar language detected!")
    else:
        print("No vulgar language detected.")