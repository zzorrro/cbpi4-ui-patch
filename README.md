# cbpi4-ui-patch

Патч интерфейса CraftBeerPi4 (пакет `cbpi4gui` 0.5.0, файл `main.65b608fc.js`): стабильная ширина кнопок Actor, кнопки +/-, крупное окно мощности и уведомления, настраиваемые размеры. Цвета и шрифты настраиваются отдельно, плагином [cbpi4-UITheme](https://github.com/zzorrro/cbpi4-UITheme) (Settings, вкладка UI Theme).

## Установка (любой пользователь Pi)

    curl -fsSL https://raw.githubusercontent.com/zzorrro/cbpi4-ui-patch/main/install.sh | sudo bash

Скрипт ставит файлы в `/opt/cbpi4-ui-patch`, создаёт команду `cbpi4-ui-patch`, сам находит файл интерфейса и применяет патч. После этого в браузере Ctrl+F5.

Установка вместе с плагином цветов и шрифтов: `curl -fsSL ... | sudo WITH_THEME=1 bash`.

## Команды

    sudo cbpi4-ui-patch apply      # применить (или применить заново после правки настроек)
    sudo cbpi4-ui-patch restore    # вернуть оригинальный файл
    sudo cbpi4-ui-patch status     # состояние
    sudo cbpi4-ui-patch uninstall  # вернуть оригинал и удалить патч с системы

Если файл не найден автоматически: `sudo cbpi4-ui-patch apply --file /путь/к/main.65b608fc.js`

## Настройки

    sudo nano /opt/cbpi4-ui-patch/settings.py
    sudo cbpi4-ui-patch apply

В `settings.py` настраивается блок SIZES (размеры и время показа). Файл `settings.py` не перезаписывается при обновлении. Значения по умолчанию и описания: `settings_default.py`.

## Обновление

Повторно выполните команду установки. После обновления пакета cbpi4gui через pip выполните `sudo cbpi4-ui-patch apply`.
