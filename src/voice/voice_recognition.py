# 3rd party
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import tempfile
from faster_whisper import WhisperModel
import torch

# setup for audio recording and transcription
SAMPLERATE = 16000
BLOCK_DURATION = 10  # seconds of audio in buffer

q = queue.Queue()
recording = True

model = WhisperModel("base", compute_type="int8",
                     device="cuda" if torch.cuda.is_available() else "cpu")


def callback(indata, frames, time_info, status):
    """Capture audio into buffer"""
    if status:
        print(status)
    q.put(indata.copy())


def record_and_transcribe() -> None:
    with sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=callback):
        print("Starting audio recording...")
        audio_buffer = np.empty((0, 1), dtype=np.float32)

        try:
            while recording:
                try:
                    data = q.get(timeout=1)
                    audio_buffer = np.concatenate((audio_buffer, data), axis=0)

                    if len(audio_buffer) >= SAMPLERATE * BLOCK_DURATION:
                        block = audio_buffer[:SAMPLERATE * BLOCK_DURATION]
                        audio_buffer = audio_buffer[SAMPLERATE *
                                                    BLOCK_DURATION:]

                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                            wav.write(tmpfile.name, SAMPLERATE, block)
                            print("Recognizing...")
                            segments, _ = model.transcribe(tmpfile.name)

                            for seg in segments:
                                print(f"{seg.text.strip()}")
                                # result = agent.invoke(
                                #     {"input": seg.text.strip()})
                                # print(
                                #     f"Результат: {result['output'] if 'output' in result else 'Нет результата'}")

                except queue.Empty:
                    pass
        except KeyboardInterrupt:
            print("Stopped by user.")
