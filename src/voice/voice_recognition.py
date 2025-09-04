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

    def __init__(self, on_transcribe_callback, SAMPLE_RATE: int = 16000, BLOCK_DURATION: int = 4):
        self.SAMPLE_RATE = SAMPLE_RATE
        self.BLOCK_DURATION = BLOCK_DURATION
        self.recording = False
        self.queue = queue.Queue()
        self.stream = None
        self.silence_threshold = 0.005
        self.min_speech_duration = 1.0
        self.pause_duration = 0.7
        self.model = None
        self.on_transcribe_callback = on_transcribe_callback

    def _initialize_model(self):
        """Initialize the Whisper model if not already initialized."""
        if self.model is None:
            print("Initializing voice recognition model...")
            self.model = WhisperModel("tiny", compute_type="int8",
                                      device="cuda" if torch.cuda.is_available() else "cpu")
            print("Model initialized!")

    def _callback(self, indata, frames, time, status):
        """Capture audio into buffer"""
        if status:
            print(f"Status: {status}")
        self.queue.put(indata.copy())

    def _is_silent(self, audio_data: np.ndarray) -> bool:
        """Check if the audio chunk is silent."""
        return np.max(np.abs(audio_data)) < self.silence_threshold

    def _record_and_transcribe(self) -> None:
        """Record audio and transcribe it using the Whisper model."""
        self._initialize_model()

        self.stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            callback=self._callback,
            blocksize=int(self.SAMPLE_RATE * 0.1)  # 100ms chunks
        )
        self.stream.start()

        audio_buffer = np.empty((0, 1), dtype=np.float32)
        silence_duration = 0
        speech_duration = 0
        last_speech_time = 0

        try:
            while self.recording:
                try:
                    data = self.queue.get(timeout=0.1)
                    current_time = len(audio_buffer) / self.SAMPLE_RATE

                    if self._is_silent(data):
                        silence_duration += 0.1  # 100ms chunk
                        if silence_duration >= self.pause_duration and speech_duration >= self.min_speech_duration:
                            block = audio_buffer
                            audio_buffer = np.empty((0, 1), dtype=np.float32)
                            silence_duration = 0
                            speech_duration = 0
                    else:
                        silence_duration = 0
                        speech_duration = current_time - last_speech_time
                        last_speech_time = current_time

                    audio_buffer = np.concatenate((audio_buffer, data), axis=0)

                    process_buffer = False
                    block = None

                    if len(audio_buffer) >= self.SAMPLE_RATE * self.BLOCK_DURATION:
                        block = audio_buffer[:self.SAMPLE_RATE *
                                             self.BLOCK_DURATION]
                        audio_buffer = audio_buffer[self.SAMPLE_RATE *
                                                    self.BLOCK_DURATION:]
                        process_buffer = True

                    elif silence_duration >= self.pause_duration and speech_duration >= self.min_speech_duration:
                        block = audio_buffer
                        audio_buffer = np.empty((0, 1), dtype=np.float32)
                        process_buffer = True
                        silence_duration = 0
                        speech_duration = 0

                    if process_buffer and block is not None and len(block) > 0:

                        if self.model:
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                                wav.write(tmpfile.name,
                                          self.SAMPLE_RATE, block)
                                print("Recognizing...")
                                segments, _ = self.model.transcribe(
                                    tmpfile.name)

                                for seg in segments:
                                    transcribed_text = seg.text.strip()
                                    print(f"Transcribed: {transcribed_text}")
                                    if self.on_transcribe_callback:
                                        self.on_transcribe_callback(
                                            transcribed_text)
                        else:
                            print("Warning: Model not initialized")
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
            self._initialize_model()
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
