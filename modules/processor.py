import json
import subprocess
import os

class CommandProcessor:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        config_path = os.path.join(base_dir, "config.json")
        
        self.assistant_name = "гоша" # Дефолт
        self.commands = []

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.commands = data.get("commands", [])
                if "settings" in data and "name" in data["settings"]:
                    self.assistant_name = data["settings"]["name"].lower()
        except FileNotFoundError:
            print(f"Error: config.json not found at {config_path}")

    def process(self, text, assistant):
        if not text: return False
        
        text = text.lower()
        
        if self.assistant_name and not text.startswith(self.assistant_name):
            return False

        clean_text = text[len(self.assistant_name):].strip()
        
        if not clean_text:
            assistant.speak("Слушаю.")
            return True

        for cmd in self.commands:
            if any(trigger in clean_text for trigger in cmd["triggers"]):
                
                if "response" in cmd and cmd["response"]:
                    assistant.speak(cmd["response"])
                
                # Выполняем
                if "exec" in cmd and cmd["exec"]:
                    if cmd["exec"] == "exit_script":
                        return "EXIT"
                    
                    print(f">> Executing: {cmd['exec']}")
                    subprocess.Popen(cmd['exec'], shell=True)
                
                return True
                
        return False