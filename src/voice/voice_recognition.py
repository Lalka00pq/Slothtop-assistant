#project
from src.agent.agent import agent
# 3rd party
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import tempfile
from faster_whisper import WhisperModel
import torch

# Настройки
SAMPLERATE = 16000
BLOCK_DURATION = 10  # Секунд аудио в буфере

q = queue.Queue()
recording = True

model = WhisperModel("base", compute_type="int8", device="cuda" if torch.cuda.is_available() else "cpu")


def callback(indata, frames, time_info, status):
    """Захватываем аудио в буфер"""
    if status:
        print(status)
    q.put(indata.copy())


def record_and_transcribe():
    with sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=callback):
        print("Говорите... (нажмите Ctrl+C для выхода)")
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
                            print("Распознаю...")
                            segments, _ = model.transcribe(tmpfile.name)

                            for seg in segments:
                                print(f"{seg.text.strip()}")
                                agent.run(seg.text.strip())

                except queue.Empty:
                    pass
        except KeyboardInterrupt:
            print("Остановлено пользователем.")
