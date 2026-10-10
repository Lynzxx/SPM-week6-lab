import os
import sys
import threading
import unittest
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def start_local_app():
    """Serve the source app.py in-process on a free port (local runs only)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from werkzeug.serving import make_server

    from app import app

    return make_server("127.0.0.1", 0, app)


class FineCheckerPageTests(unittest.TestCase):
    """Drives the fine checker page in a real browser.

    Set E2E_BASE_URL to test an already running app (CI points it at the
    staged zip); otherwise the source app is started in-process.
    """

    @classmethod
    def setUpClass(cls):
        cls.server = None
        cls.base_url = os.environ.get("E2E_BASE_URL")
        if not cls.base_url:
            cls.server = start_local_app()
            threading.Thread(target=cls.server.serve_forever, daemon=True).start()
            cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        if cls.server:
            cls.server.shutdown()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def test_five_days_late_deluxe_duck_costs_three_dollars(self):
        # Brief: 2 grace days, then $0.50/day, doubled for deluxe, capped at $5.
        # 5 days -> 3 chargeable days -> $1.50 -> deluxe $3.00.
        page = self.page
        page.goto(f"{self.base_url}/")
        page.get_by_role("spinbutton", name="Days late").fill("5")
        page.get_by_role("checkbox", name="Deluxe duck").check()
        page.get_by_role("button", name="Check fine").click()

        expect(page.locator("#result")).to_have_text("Fine: $3.00")


if __name__ == "__main__":
    unittest.main()
