# 3rd party
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import tempfile
from faster_whisper import WhisperModel
import torch


class VoiceRecognition:
    """Class for real-time voice recognition using Whisper model."""

    def __init__(self, SAMPLE_RATE: int = 16000, BLOCK_DURATION: int = 10):
        self.SAMPLE_RATE = SAMPLE_RATE
        self.BLOCK_DURATION = BLOCK_DURATION
        self.recording = False
        self.queue = queue.Queue()
        self.stream = None
        self.model = WhisperModel("base", compute_type="int8",
                                  device="cuda" if torch.cuda.is_available() else "cpu")

    def _callback(self, indata, frames, time, status):
        """Capture audio into buffer"""
        if status:
            print(f"Status: {status}")
        self.queue.put(indata.copy())

    def _record_and_transcribe(self) -> None:
        """Record audio and transcribe it using the Whisper model."""
        self.stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            callback=self._callback
        )
        self.stream.start()

        audio_buffer = np.empty((0, 1), dtype=np.float32)

        try:
            while self.recording:
                try:
                    data = self.queue.get(timeout=1)
                    audio_buffer = np.concatenate((audio_buffer, data), axis=0)

                    if len(audio_buffer) >= self.SAMPLE_RATE * self.BLOCK_DURATION:
                        block = audio_buffer[:self.SAMPLE_RATE *
                                             self.BLOCK_DURATION]
                        audio_buffer = audio_buffer[self.SAMPLE_RATE *
                                                    self.BLOCK_DURATION:]

                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                            wav.write(tmpfile.name, self.SAMPLE_RATE, block)
                            print("Recognizing...")
                            segments, _ = self.model.transcribe(tmpfile.name)

                            for seg in segments:
                                print(f"{seg.text.strip()}")
                except queue.Empty:
                    if not self.recording:
                        break
                    continue
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

    def start_recording(self):
        """Start recording audio."""
        if not self.recording:
            print("Starting audio recording...")
            self.recording = True
            self._record_and_transcribe()

    def stop_recording(self):
        """Stop recording audio."""
        if self.recording:
            print("Stopping audio recording...")
            self.recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
