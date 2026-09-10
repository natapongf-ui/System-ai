import threading
import queue
import time
import os

class VoiceAlertSystem:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.is_running = True
        self.enabled = True
        self.last_played = {}
        self.cooldown = 3.0 # seconds between same messages
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _process_queue(self):
        try:
            import pyttsx3
            # Initialize COM for Windows thread safety if on Windows
            if os.name == 'nt':
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pass

            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'thai' in voice.name.lower() or 'th' in voice.languages:
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 155)
        except Exception as e:
            engine = None

        while self.is_running:
            try:
                message = self.message_queue.get(timeout=0.5)
                if self.enabled and engine is not None and message:
                    try:
                        engine.say(message)
                        engine.runAndWait()
                    except Exception:
                        pass
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue

    def play(self, message: str):
        if not self.enabled or not message:
            return
            
        current_time = time.time()
        # Check cooldown to prevent spamming the same message
        if message in self.last_played:
            if current_time - self.last_played[message] < self.cooldown:
                return
                
        self.last_played[message] = current_time
        try:
            self.message_queue.put(message, block=False)
        except queue.Full:
            pass

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def stop(self):
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1)

voice_alert = VoiceAlertSystem()
