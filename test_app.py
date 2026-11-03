import unittest

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_returns_welcome_message(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome", response.get_json()["message"])

    def test_health_returns_healthy(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
