import sys
import os
import json
import pyaudio
import subprocess
import asyncio
import edge_tts
from vosk import Model, KaldiRecognizer

class HybridVoice:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        config_path = os.path.join(base_dir, "config.json")
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.cfg = json.load(f)

        self.vosk_path = os.path.join(base_dir, self.cfg["settings"]["vosk_path"])
        self.voice_name = self.cfg["settings"]["voice"]
        self.temp_audio = "/tmp/gosha_reply.mp3"

        if not os.path.exists(self.vosk_path):
            print(f"ОШИБКА: Нет модели Vosk в {self.vosk_path}")
            sys.exit(1)
            
        print(">> Загрузка Vosk...")
        model = Model(self.vosk_path)
        self.rec = KaldiRecognizer(model, 16000)
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
        self.stream.start_stream()
        print(">> Гоша готов к работе.")

    async def _generate_audio(self, text):
        communicate = edge_tts.Communicate(text, self.voice_name)
        await communicate.save(self.temp_audio)

    def speak(self, text):
        print(f"GOSHA: {text}")
        if self.stream.is_active(): self.stream.stop_stream()

        try:
            asyncio.run(self._generate_audio(text))
            subprocess.run(
                ["mpv", "--no-terminal", "--speed=1.1", self.temp_audio],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Ошибка озвучки: {e}")
        finally:
            if self.stream.is_stopped(): self.stream.start_stream()

    def listen(self):
        try:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                res = json.loads(self.rec.Result())
                text = res['text']
                if text:
                    print(f"You: {text}")
                    return text
        except OSError:
            pass
        return ""