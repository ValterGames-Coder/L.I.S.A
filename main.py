import sys
import os
from modules.voice import HybridVoice
from modules.processor import CommandProcessor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    try:
        assistant = HybridVoice(BASE_DIR)
        processor = CommandProcessor(BASE_DIR)

        assistant.speak("Ассистент на связи. Жду команд.")

        while True:
            text = assistant.listen()
            if text:
                res = processor.process(text, assistant)
                if res == "EXIT":
                    assistant.speak("Отключаюсь.")
                    sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()