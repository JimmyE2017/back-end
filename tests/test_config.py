import unittest

from mongoengine import disconnect

from app import create_app


class TestDevelopmentConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app("dev")

    def test_app_config(self):
        self.assertTrue(self.app.config["DEBUG"])

    def tearDown(self) -> None:
        disconnect()


class TestTestingConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app("test")

    def test_app_config(self):
        self.assertTrue(self.app.config["DEBUG"])
        self.assertTrue(self.app.config["TESTING"])

    def tearDown(self) -> None:
        disconnect()


class TestProductionConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app("prod")

    def test_app_config(self):
        self.assertFalse(self.app.config["DEBUG"])

    def tearDown(self) -> None:
        disconnect()
