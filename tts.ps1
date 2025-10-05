Add-Type -AssemblyName System.Speech
$spk = New-Object System.Speech.Synthesis.SpeechSynthesizer
$wav = "$PWD\hello.wav"
$spk.SetOutputToWaveFile($wav)
$spk.Speak("Hello world")
$spk.Dispose()
ffmpeg -y -i "$wav" -ar 44100 -ac 2 -b:a 192k "hello.mp3"