import os
import re
import zlib

def get_commits_with_file(repo_path, file_name):
    """
    Возвращает список коммитов, в которых фигурирует указанный файл.

    :param repo_path: Путь до локального репозитория.
    :param file_name: Имя файла для поиска.
    :return: Список хэшей коммитов.
    """
    def read_git_object(object_hash):
        """Читает и декомпрессирует объект Git по его хэшу."""
        object_path = os.path.join(repo_path, '.git', 'objects', object_hash[:2], object_hash[2:])
        with open(object_path, 'rb') as f:
            compressed_data = f.read()
            decompressed_data = zlib.decompress(compressed_data)
        return decompressed_data

    def parse_tree_hash(commit_data):
        """Извлекает хэш дерева из данных коммита."""
        match = re.search(r"tree\s+([a-f0-9]{40})", commit_data)
        if match:
            return match.group(1)
        else:
            raise ValueError("Хэш дерева не найден в данных коммита.")

    def parse_tree(tree_data):
        """
        Разбирает данные дерева Git и извлекает файлы.
        Возвращает список кортежей (mode, file_name, object_hash).
        """
        files = []
        index = 0

        while index < len(tree_data):
            space_pos = tree_data.find(b' ', index)
            if space_pos == -1:
                break
            null_pos = tree_data.find(b'\x00', space_pos)
            if null_pos == -1:
                break
            mode = tree_data[index:space_pos].decode('ascii', errors='replace')
            file_name = tree_data[space_pos + 1:null_pos].decode('utf-8', errors='replace')
            object_hash = tree_data[null_pos + 1:null_pos + 21].hex()
            index = null_pos + 21
            files.append((mode, file_name, object_hash))
        return files

    # Читаем все коммиты из logs/HEAD
    commits = []
    with open(os.path.join(repo_path, '.git', 'logs', 'HEAD'), 'r') as log_file:
        for log in log_file:
            commit_hash = log.strip().split()[1]
            commits.append(commit_hash)

    # Поиск коммитов с указанным файлом
    matching_commits = []
    for commit_hash in commits:
        # Декодируем данные коммита
        commit_data = read_git_object(commit_hash).decode('utf-8')
        tree_hash = parse_tree_hash(commit_data)

        # Декодируем данные дерева
        tree_data = read_git_object(tree_hash)
        files_in_tree = parse_tree(tree_data)

        # Проверяем наличие файла в дереве
        if any(f[1] == file_name for f in files_in_tree):
            matching_commits.append(commit_hash)

    return matching_commits
