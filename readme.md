# Git Dependency Visualizer

## Описание проекта

Этот инструмент командной строки предназначен для визуализации графа зависимостей в Git-репозитории, включая транзитивные зависимости. Граф строится для коммитов, в которых фигурирует заданный файл, и отображает информацию о каждом коммите, такую как дата, время и сообщение.

Визуализация осуществляется с помощью Graphviz, и результат выводится в виде кода DOT, который можно затем визуализировать в графическом виде.

## Основные функции

- **Загрузка конфигурации**: Загрузка пути к репозиторию, файлу и инструменту для визуализации из конфигурационного файла JSON.
- **Извлечение данных о коммитах**: Получение данных о коммитах с использованием Git (например, автор, дата, родительские коммиты).
- **Построение графа зависимостей**: Строится граф зависимостей для всех коммитов, в которых присутствует указанный файл.
- **Генерация кода для Graphviz**: Генерация кода DOT для визуализации графа зависимостей.
- **Визуализация графа**: Визуализация графа с помощью Graphviz.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:Dpanov2302/kisscm-2.git
   cd kisscm-2
   ```

2. Убедитесь, что у вас установлен Python 3 и все необходимые библиотеки:
   ```bash
   pip install -r requirements.txt
   ```

3. Установите Graphviz (если еще не установлен). Для визуализации графа потребуется установить Graphviz:
   - Для Windows: скачайте и установите Graphviz с [официального сайта](https://graphviz.gitlab.io/download/).
   - Для Linux/MacOS:
     ```bash
     sudo apt-get install graphviz  # Ubuntu/Debian
     brew install graphviz  # MacOS (с использованием Homebrew)
     ```

## Конфигурационный файл

Пример конфигурации `config.json`:

```json
{
  "repository_path": "path/to/your/repo",
  "file_path": "path/to/your/file",
  "graph_visualizer_path": "path/to/your/Graphviz/bin/dot.exe",
  "output_file": "graph.dot"
}
```

### Описание полей:

- `repository_path`: Путь к Git-репозиторию, в котором будет строиться граф зависимостей.
- `file_path`: Путь к файлу в репозитории, для которого необходимо построить граф зависимостей.
- `graph_visualizer_path`: Путь к инструменту Graphviz, который будет использоваться для визуализации (например, путь к \`dot.exe\`).
- `output_file`: Путь для сохранения сгенерированного файла с кодом DOT для графа зависимостей.

## Как использовать

1. Создайте и настройте файл конфигурации `config.json` в корне репозитория.
2. Запустите скрипт:

   ```bash
   python main.py ./config.json
   ```

3. В результате будет сгенерирован код DOT для графа зависимостей. Он будет выведен на экран и сохранен в указанный файл.

4. Для визуализации графа выполните следующую команду с помощью Graphviz:

   ```bash
   dot -Tpng graph.dot -o graph.png
   ```

   Эта команда сгенерирует граф в формате PNG на основе кода DOT.

## Тестирование

Весь функционал визуализатора покрыт тестами. Для запуска тестов используйте:

```bash
python -m unittest discover -s tests
```

Тесты проверяют корректность работы всех основных функций, включая загрузку конфигурации, получение данных о коммитах, построение графа зависимостей и генерацию кода DOT.

## Зависимости

- Python 3.x
- Git
- Graphviz (для визуализации)
- Библиотека `subprocess` (встроенная)
- Библиотека `json` (встроенная)
