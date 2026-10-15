"""
Unit Tests for Dashboard API Endpoints
Verifies:
- Workspace file listing & safe reading
- Path traversal protection via ExecutionBoundary
- Durable tasks store endpoint
- Skills catalog retrieval
"""
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from dashboard.server import app, SESSION_TOKEN
from core.config import WORKSPACE_DIR

class TestDashboardAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, cookies={"session_token": SESSION_TOKEN})
        self.test_file = Path(WORKSPACE_DIR) / "test_api_sample.py"
        self.test_file.write_text('print("Unit test sample")\n', encoding="utf-8")

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_workspace_files_list(self):
        res = self.client.get("/api/workspace/files")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("files", data)
        self.assertTrue(any(f["name"] == "test_api_sample.py" for f in data["files"]))

    def test_workspace_file_read(self):
        res = self.client.get("/api/workspace/file?path=test_api_sample.py")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("Unit test sample", data.get("content", ""))

    def test_path_traversal_blocked(self):
        res = self.client.get("/api/workspace/file?path=../../core/config.py")
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertFalse(data.get("success"))
        self.assertIn("Path traversal access denied", data.get("error", ""))

    def test_durable_tasks_endpoint(self):
        res = self.client.get("/api/tasks")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_skills_catalog_endpoint(self):
        res = self.client.get("/api/brain/skills")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

if __name__ == "__main__":
    unittest.main()
