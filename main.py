import subprocess
import json
from datetime import datetime, timezone


def load_config(config_path):
    """Загрузка конфигурации из JSON-файла."""
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации '{config_path}' не найден.")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: не удалось разобрать JSON в файле '{config_path}'.")
        raise


def get_commit_data(repo_path, commit_hash):
    """Получение данных о коммите по его хешу с использованием git cat-file."""
    try:
        commit_data = subprocess.check_output(
            ["git", "cat-file", "commit", commit_hash],
            cwd=repo_path
        ).decode("utf-8")
        return commit_data
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при извлечении данных коммита {commit_hash}: {e}")
        return None


def parse_commit_data(commit_data):
    """Парсинг информации из коммита (дата, автор, родительский коммит, сообщение)."""
    lines = commit_data.splitlines()
    commit_info = {"parents": [], "message": ""}
    for line in lines:
        if line.startswith('author'):
            parts = line.split()
            timestamp = int(parts[-2])
            commit_info['date'] = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%d.%m.%Y %H:%M')
        elif line.startswith('parent'):
            commit_info["parents"].append(line.split()[1])
        elif line.startswith("    "):  # Сообщение коммита
            commit_info["message"] = line.strip()
    return commit_info


def get_commits_with_file(repo_path, file_path):
    """Получение всех коммитов, в которых фигурирует указанный файл."""
    try:
        output = subprocess.check_output(
            ["git", "log", "--pretty=format:%H", "--", file_path],
            cwd=repo_path
        ).decode("utf-8")
        return output.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении коммитов для файла {file_path}: {e}")
        return []


def build_dependency_graph(repo_path, file_path):
    """Построение графа зависимостей для коммитов с файлом."""
    commits = get_commits_with_file(repo_path, file_path)
    if not commits:
        print(f"Не найдено коммитов для файла {file_path}.")
        return {}

    graph = {}
    print(f"Найдено коммитов для файла {file_path}: {len(commits)}")
    for commit_hash in commits:
        commit_data = get_commit_data(repo_path, commit_hash)
        if commit_data:
            commit_info = parse_commit_data(commit_data)
            graph[commit_hash] = commit_info

    return graph


def generate_graph_code(graph):
    """Генерация кода Graphviz для графа зависимостей."""
    graph_code = "digraph G {\n"
    for commit_hash, info in graph.items():
        node_label = f"{commit_hash[:7]} [{info['date']}, {info['message']}]"
        graph_code += f'    "{commit_hash}" [label="{node_label}"];\n'
        for parent in info["parents"]:
            graph_code += f'    "{parent}" -> "{commit_hash}";\n'
    graph_code += "}"
    return graph_code


def save_graph_to_file(graph_code, output_path):
    """Сохранение кода Graphviz в файл."""
    with open(output_path, 'w') as file:
        file.write(graph_code)
    print(f"Граф зависимостей сохранен в файл: {output_path}")


def main(config_path):
    config = load_config(config_path)
    repo_path = config["repository_path"]
    file_path = config["file_path"]
    output_path = config.get("output_file", "graph.dot")

    graph = build_dependency_graph(repo_path, file_path)

    if not graph:
        print("Не удалось найти коммиты с указанным файлом.")
        return

    graph_code = generate_graph_code(graph)

    print("\nГенерируемый код Graphviz:")
    print(graph_code)

    save_graph_to_file(graph_code, output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Пожалуйста, укажите путь к файлу конфигурации.")
    else:
        main(sys.argv[1])
