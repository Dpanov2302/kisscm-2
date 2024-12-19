import unittest
from unittest.mock import patch, mock_open
from main import (
    load_config,
    get_commit_data,
    parse_commit_data,
    build_dependency_graph,
    generate_graph_code,
)


class TestMain(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='{"repository_path": "/repo", "file_path": "file.txt"}')
    def test_load_config(self, mock_file):
        config = load_config("config.json")
        self.assertEqual(config["repository_path"], "/repo")
        self.assertEqual(config["file_path"], "file.txt")
        mock_file.assert_called_once_with("config.json", "r")

    @patch("subprocess.check_output")
    def test_get_commit_data(self, mock_subprocess):
        mock_subprocess.return_value = b"author John Doe 1609459200 +0200\nparent 1234567"
        commit_data = get_commit_data("/repo", "abc123")
        self.assertIn("author", commit_data)
        self.assertIn("parent 1234567", commit_data)
        mock_subprocess.assert_called_once_with(["git", "cat-file", "commit", "abc123"], cwd="/repo")

    def test_parse_commit_data(self):
        commit_data = "author John Doe 1609459200 +0200\nparent 1234567\n    Initial commit"
        parsed_data = parse_commit_data(commit_data)
        self.assertEqual(parsed_data["date"], "01.01.2021 00:00")
        self.assertEqual(parsed_data["parents"], ["1234567"])
        self.assertEqual(parsed_data["message"], "Initial commit")

    @patch("subprocess.check_output")
    def test_build_dependency_graph(self, mock_subprocess):
        mock_subprocess.side_effect = [
            b"abc123\ndef456",
            b"author John Doe 1609459200 +0200\nparent def456\n    Fix bugs",
            b"author Jane Smith 1609365600 +0200\n    Initial commit",
        ]
        graph = build_dependency_graph("/repo", "file.txt")
        self.assertIn("abc123", graph)
        self.assertIn("def456", graph)
        self.assertEqual(graph["abc123"]["message"], "Fix bugs")
        self.assertEqual(graph["def456"]["message"], "Initial commit")

    def test_generate_graph_code(self):
        graph = {
            "abc123": {"date": "01.01.2021 00:00", "message": "Fix bugs", "parents": ["def456"]},
            "def456": {"date": "31.12.2020 23:00", "message": "Initial commit", "parents": []},
        }
        graph_code = generate_graph_code(graph)
        self.assertIn('"abc123" [label="abc123 [01.01.2021 00:00, Fix bugs]"]', graph_code)
        self.assertIn('"def456" [label="def456 [31.12.2020 23:00, Initial commit]"]', graph_code)
        self.assertIn('"def456" -> "abc123";', graph_code)


if __name__ == "__main__":
    unittest.main()
