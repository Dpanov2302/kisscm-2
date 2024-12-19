import os


def print_tree(startpath, exclude_files=None, prefix=""):
    """Рекурсивная функция для вывода дерева каталогов с возможностью исключения файлов."""
    if exclude_files is None:
        exclude_files = []

    entries = list(os.scandir(startpath))
    entries.sort(key=lambda e: (not e.is_dir(), e.name))

    for index, entry in enumerate(entries):
        if entry.name in exclude_files or entry.name.startswith(".") or entry.name.startswith("__p"):
            continue

        connector = "└── " if index == len(entries) - 1 else "├── "
        print(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))

        if entry.is_dir():
            extension = "    " if index == len(entries) - 1 else "│   "
            print_tree(entry.path, exclude_files, prefix + extension)


if __name__ == "__main__":
    root_path = os.path.abspath(os.path.dirname(__file__))
    root_name = os.path.basename(root_path)
    print("Файловая структура проекта:")
    print(root_name + "/")
    print_tree(root_path)
