# Video Processing Tools

- Silence removing
- Swapping audio (with prior waveform sync)
- Increase volume (TBD)
- Transcription

# To test it
1. Upload video and microphone audio to 'video' folder in root directory
2. Run `python src/video_processing/audio_sync.py` (edit main() method with your file paths)
3. Run `python src/video_processing/remove_silence.py` (edit main() method with your file paths)
4. Run `python src/video_processing/transcribe.py` (edit main() method with your file paths)