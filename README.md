# EmyDocx

Локальный редактор Markdown с экспортом в редактируемый DOCX. Интерфейс написан на Python и Flet; сервер и учётная запись не нужны. Текущий выпуск — MVP 0.1.

## Возможности

- Открытие файлов `.md`, `.markdown` и `.txt`, редактирование и сохранение Markdown.
- Экспорт в DOCX с настройкой шрифта, размеров текста, цветов, полей и межстрочного интервала.
- Три готовых шаблона оформления в `templates.json`.
- Заголовки, абзацы, выделение, код, ссылки, списки, цитаты, разделители и таблицы.
- Базовое отображение формул с Unicode-символами и верхними/нижними индексами.

## Установка и запуск

Нужен Python 3.11–3.14. Проверки в CI выполняются на Linux и Windows для всех этих версий; локально проект проверен на Python 3.14.8. Исходный код запускается из корня репозитория.

### Linux

```bash
git clone https://github.com/dead-crayzed/EmyDocx.git
cd EmyDocx
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

На Arch Linux, если системный диалог выбора файла не открывается, установите `zenity` командой `sudo pacman -S zenity`.

### Windows (PowerShell)

```powershell
git clone https://github.com/dead-crayzed/EmyDocx.git
cd EmyDocx
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Если PowerShell блокирует активацию окружения, используйте `.venv\Scripts\python.exe -m pip install -r requirements.txt` и `.venv\Scripts\python.exe main.py`.

## Проверки для разработчиков

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m ruff check .
python -m pytest -q
```

GitHub Actions запускает эти проверки при каждом `push` и `pull_request` на Linux и Windows с Python 3.11–3.14.

## Шаблоны

Настройки хранятся в `templates.json`. Каждый шаблон содержит `font_name`, `body_size`, `h1_size`, `h2_size`, `h3_size`, `body_color`, `heading_color`, `margin_cm` и `line_spacing`. Цвета задаются в формате `#RRGGBB`. Если файл отсутствует или содержит некорректный JSON, используются встроенные шаблоны.

## Структура проекта

```text
EmyDocx/
├── .github/workflows/ci.yml
├── emydocx/
│   ├── app.py                 # окно приложения и обработчики
│   ├── converter/             # разбор Markdown и создание DOCX
│   ├── services/              # открытие и сохранение файлов
│   ├── ui/                    # компоненты интерфейса
│   └── template_service.py
├── tests/
├── main.py
├── templates.json
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## Ограничения MVP

- Предпросмотра WYSIWYG и автосохранения пока нет. При создании нового документа несохранённые изменения не запрашиваются повторно.
- Изображения в Markdown показываются текстовым маркером по alt-тексту; сами файлы изображений в DOCX не встраиваются.
- Формулы отображаются приближённо и не создают редактируемые объекты Office Math.
- Отображение сложных таблиц и многоуровневых списков может отличаться между Word, LibreOffice и другими редакторами.
- Мобильные платформы не проверялись. Ручная проверка графического интерфейса на Windows ещё требуется.

## Лицензия

Исходный код распространяется по [лицензии MIT](LICENSE).
