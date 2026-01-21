import json
import subprocess
import os

class CommandProcessor:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        config_path = os.path.join(base_dir, "config.json")
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.commands = json.load(f)["commands"]
        except FileNotFoundError:
            print(f"Error: config.json not found at {config_path}")
            self.commands = []

    def process(self, text, assistant):
        if not text: return False

        text = text.lower()

        for cmd in self.commands:
            if any(trigger in text for trigger in cmd["triggers"]):
                
                # 1. Говорим
                if "response" in cmd:
                    assistant.speak(cmd["response"])
                
                # 2. Выполняем
                if "exec" in cmd:
                    if cmd["exec"] == "exit_script":
                        return "EXIT"
                    
                    print(f">> Executing: {cmd['exec']}")
                    # Запускаем процесс независимо
                    subprocess.Popen(cmd['exec'], shell=True)
                
                return True
        return False