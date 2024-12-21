import json
import os
import zlib
from datetime import datetime, timezone
from commit_handler import get_commits_with_file_


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


def read_git_object(repo_path, object_hash):
    """Чтение объекта Git из .git/objects."""
    object_dir = os.path.join(repo_path, '.git', 'objects', object_hash[:2])
    object_file = os.path.join(object_dir, object_hash[2:])
    if not os.path.isfile(object_file):
        return None

    with open(object_file, 'rb') as f:
        compressed_data = f.read()

    decompressed_data = zlib.decompress(compressed_data)
    return decompressed_data


def get_commit_data(repo_path, commit_hash):
    """Получение данных о коммите напрямую из .git/objects."""
    commit_data_raw = read_git_object(repo_path, commit_hash)
    if not commit_data_raw:
        print(f"Ошибка: объект коммита {commit_hash} не найден.")
        return None

    commit_data = commit_data_raw.decode('utf-8')
    return commit_data


def parse_commit_data(commit_data):
    """Парсинг информации из коммита (дата, автор, родительский коммит, сообщение)."""
    commit_data = commit_data.replace('tree', '\ntree')
    lines = commit_data.splitlines()
    commit_info = {"parents": [], "message": ""}
    tree_hash = None

    for line in lines:
        if line.startswith("tree "):
            tree_hash = line.split()[1]
        elif line.startswith('author'):
            parts = line.split()
            timestamp = int(parts[-2])
            commit_info['date'] = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%d.%m.%Y %H:%M')
        elif line.startswith('parent'):
            commit_info["parents"].append(line.split()[1])
        elif line.startswith("    "):
            commit_info["message"] = line.strip()

    commit_info['tree'] = tree_hash
    return commit_info

def get_commits_with_file(repo_path, file_path):
    """Получение всех коммитов, в которых фигурирует указанный файл."""
    import subprocess
    try:
        output = subprocess.check_output(
            ["git", "log", "--pretty=format:%H", "--", file_path],
            cwd=repo_path
        ).decode("utf-8")
        return output.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении коммитов для файла {file_path}: {e}")
        return []

def build_dependency_graph(repo_path, file_name):
    """Построение графа зависимостей для коммитов с файлом."""
    commits = get_commits_with_file(repo_path, file_name)
    if not commits:
        print(f"Не найдено коммитов для файла {file_name}.")
        return {}

    graph = {}
    print(f"Найдено коммитов для файла {file_name}: {len(commits)}")
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
    file_name = config["file_name"]
    output_file = config["output_file"]
    output_path = config.get("output_file", output_file)

    graph = build_dependency_graph(repo_path, file_name)

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
