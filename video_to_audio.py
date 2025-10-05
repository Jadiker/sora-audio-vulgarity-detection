# from https://stackoverflow.com/questions/26741116/python-extract-wav-from-video-file
import subprocess

def video_to_audio(video_file: str, audio_file: str):
    # TODO this needs sanitization if used by untrusted users
    # use ffmpeg with bitrate 160k, 2 channels, 44100 Hz frequency, no video
    command = f"ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 -vn {audio_file}"
    subprocess.call(command, shell=True)

if __name__ == "__main__":
    video_to_audio("videos/dum_n.mp4", "audios/dum_n.wav")