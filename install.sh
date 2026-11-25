#!/usr/bin/env bash
# Установщик cbpi4-ui-patch. Запуск (от root, имя пользователя Pi не важно):
#   curl -fsSL https://raw.githubusercontent.com/zzorrro/cbpi4-ui-patch/main/install.sh | sudo bash
# Переменные окружения (необязательно):
#   NO_APPLY=1      только установить, патч не применять
#   WITH_THEME=1    дополнительно установить плагин цветов и шрифтов cbpi4-UITheme
#   INSTALL_DIR     куда ставить (по умолчанию /opt/cbpi4-ui-patch)
#   BASE_URL        откуда качать файлы
set -e
INSTALL_DIR="${INSTALL_DIR:-/opt/cbpi4-ui-patch}"
BIN="${BIN:-/usr/local/bin/cbpi4-ui-patch}"
BASE_URL="${BASE_URL:-https://raw.githubusercontent.com/zzorrro/cbpi4-ui-patch/main}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Нужны права root. Запустите через sudo:"
  echo "  curl -fsSL $BASE_URL/install.sh | sudo bash"
  exit 1
fi
command -v python3 >/dev/null || { echo "python3 не найден"; exit 1; }
command -v curl >/dev/null || { echo "curl не найден"; exit 1; }

mkdir -p "$INSTALL_DIR"
for f in patch_ui.py settings_default.py; do
  curl -fsSL "$BASE_URL/$f" -o "$INSTALL_DIR/$f.new"
  mv "$INSTALL_DIR/$f.new" "$INSTALL_DIR/$f"
done
# Ваши настройки не перезаписываются при обновлении
if [ ! -f "$INSTALL_DIR/settings.py" ]; then
  cp "$INSTALL_DIR/settings_default.py" "$INSTALL_DIR/settings.py"
fi
cat > "$BIN" <<EOF
#!/bin/sh
exec python3 "$INSTALL_DIR/patch_ui.py" "\$@"
EOF
chmod +x "$BIN"

echo "Установлено в $INSTALL_DIR"
echo "Настройки: sudo nano $INSTALL_DIR/settings.py"
echo "Команды: sudo cbpi4-ui-patch apply | restore | status | uninstall"
if [ -z "$NO_APPLY" ]; then
  "$BIN" apply
fi
if [ -n "$WITH_THEME" ]; then
  curl -fsSL "${THEME_INSTALL_URL:-https://raw.githubusercontent.com/zzorrro/cbpi4_UITheme/main/install.sh}" | bash
fi
