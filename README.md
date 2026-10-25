# EmyDocx — MVP 0.1

Локальный Markdown → DOCX редактор на Python + Flet.

## Возможности первой версии

- Редактор Markdown в двухпанельном интерфейсе.
- Открытие `.md`, `.markdown` и `.txt`.
- Сохранение исходного Markdown.
- Экспорт в настоящий редактируемый `.docx`.
- Настройка шрифта, размеров заголовков, цвета текста, полей и интервала.
- Три пресета оформления в `templates.json`.
- Базовая поддержка заголовков, абзацев, жирного/курсива, кода, ссылок, списков, цитат, горизонтальных разделителей и Markdown-таблиц.
- Обработка происходит локально, сервер и база данных не нужны.

## Запуск в Linux (Arch Linux / KDE Plasma)

Рекомендуется Python 3.11 или новее.

```bash
cd EmyDocx
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Если системный диалог выбора файла не открывается в Linux, установите `zenity`:

```bash
sudo pacman -S zenity
```

## Запуск в Windows

```powershell
cd EmyDocx
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Если PowerShell запрещает активацию окружения, можно запускать зависимости напрямую через `.venv\Scripts\python.exe`.

## Где менять шаблоны

Редактируйте `templates.json`. Доступные поля:

- `font_name`
- `body_size`
- `h1_size`, `h2_size`, `h3_size`
- `body_color`, `heading_color` в формате `#RRGGBB`
- `margin_cm`
- `line_spacing`

## Структура

```text
EmyDocx/
├── main.py
├── requirements.txt
├── templates.json
├── README.md
└── emydocx/
    ├── __init__.py
    └── converter.py
```

## Известные ограничения MVP

- Это первый прототип, а не финальный редактор Word.
- Нет полноценного WYSIWYG-предпросмотра: Markdown редактируется в исходном виде.
- Таблицы, вложенные списки, изображения, сноски и сложная разметка требуют дополнительной полировки.
- Для изображений в Markdown пока вставляется текстовый маркер, сами изображения не встраиваются.
- Для переносимости на iOS/Android потребуется отдельно проверить UX выбора файлов и ограничения платформ.

## Следующий разумный этап

1. Автосохранение черновика и предупреждение о несохранённых изменениях.
2. Предпросмотр Markdown.
3. Подсветка синтаксиса в редакторе.
4. Дополнительные параметры документа: ориентация, колонтитулы, нумерация страниц.
5. Сборка установщиков для Windows и Linux.
