#!/bin/bash

# --- НАСТРОЙКИ ---
SERVICE_NAME="G.O.S.H.A"
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_FILE="$HOME/.config/systemd/user/$SERVICE_NAME.service"
PYTHON_BIN=$(which python3)

echo "==========================================="
echo "   Установка ассистента: $SERVICE_NAME"
echo "   Путь: $PROJECT_DIR"
echo "==========================================="

if [ -z "$PYTHON_BIN" ]; then
    echo "ОШИБКА: Python3 не найден!"
    exit 1
fi

# 1. Установка зависимостей Python
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo ">> Устанавливаю библиотеки..."
    pip3 install -r "$PROJECT_DIR/requirements.txt"
fi

# 2. Установка MPV (системный плеер)
echo ">> Проверка MPV..."
if ! command -v mpv &> /dev/null; then
    echo "Попытка установки mpv..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y mpv libportaudio2
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y mpv portaudio
    else
        echo "ВНИМАНИЕ: Установите 'mpv' вручную для вашего дистрибутива!"
    fi
fi

# 3. Создание Systemd сервиса
mkdir -p "$HOME/.config/systemd/user/"

echo ">> Создаю файл службы: $SERVICE_FILE"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=G.O.S.H.A - Generative Open Speech Human like Assistant 
After=network.target sound.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON_BIN $PROJECT_DIR/main.py

# Перезапуск при ошибках (on-failure).
# Если скрипт завершится штатно (код 0), перезапуска НЕ будет.
Restart=on-failure
RestartSec=5

# Переменные для вывода логов и доступа к экрану/звуку
Environment=PYTHONUNBUFFERED=1
Environment=DISPLAY=:0
Environment=PULSE_SERVER=unix:\${XDG_RUNTIME_DIR}/pulse/native

[Install]
WantedBy=default.target
EOF

# 4. Запуск
echo ">> Перезагрузка Systemd..."
systemctl --user daemon-reload
echo ">> Включение автозагрузки..."
systemctl --user enable $SERVICE_NAME
echo ">> Перезапуск сервиса..."
systemctl --user restart $SERVICE_NAME

echo "==========================================="
echo "   ГОТОВО! G.O.S.H.A запущен."
echo "==========================================="