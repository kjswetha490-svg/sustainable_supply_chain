"""Unit tests for Flask Web API endpoints and Authentication."""
import unittest
import json
from sustainable_supply_chain.web.app import app


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_unauthorized_access_redirects(self):
        """Verify unauthenticated user accessing / is redirected to /login."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers["Location"])

    def test_unauthorized_api_returns_401(self):
        """Verify unauthenticated API request receives 401 Unauthorized."""
        resp = self.client.get("/api/overview")
        self.assertEqual(resp.status_code, 401)
        data = json.loads(resp.data)
        self.assertTrue(data.get("login_required"))

    def test_login_page_renders(self):
        """Verify /login GET renders login portal."""
        resp = self.client.get("/login")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Member Sign In", resp.data)

    def test_login_invalid_credentials(self):
        """Verify invalid login attempt is rejected."""
        resp = self.client.post("/login", data={"email": "hacker@random.com", "password": "wrongpassword"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Access Denied", resp.data)

    def test_login_valid_and_authenticated_access(self):
        """Verify authorized member can log in and access protected dashboard and APIs."""
        # 1. Log in as Swetha (CSO)
        login_resp = self.client.post("/login", data={"email": "swetha@apex.com", "password": "green2026"})
        self.assertEqual(login_resp.status_code, 302)

        # 2. Access dashboard
        dashboard_resp = self.client.get("/")
        self.assertEqual(dashboard_resp.status_code, 200)
        self.assertIn(b"Sustainable Supply Chain AI", dashboard_resp.data)
        self.assertIn(b"Swetha", dashboard_resp.data)

        # 3. Access overview API
        overview_resp = self.client.get("/api/overview")
        self.assertEqual(overview_resp.status_code, 200)
        data = json.loads(overview_resp.data)
        self.assertIn("carbon_report", data)
        self.assertIn("circularity_metrics", data)

        # 4. Access routes API
        routes_resp = self.client.get("/api/climate/routes?origin=Hai+Phong&destination=Frankfurt&weight=50")
        self.assertEqual(routes_resp.status_code, 200)
        routes_data = json.loads(routes_resp.data)
        self.assertIn("modal_options", routes_data)

        # 5. Access simulator API
        sim_resp = self.client.post("/api/simulator/run", json={"carbon_tax": 100.0, "delay_days": 5.0})
        self.assertEqual(sim_resp.status_code, 200)
        sim_data = json.loads(sim_resp.data)
        self.assertIn("simulated", sim_data)

        # 6. Access agent chat API
        chat_resp = self.client.post("/api/agent/chat", json={"message": "Audit our Scope 1, 2, and 3 carbon emissions"})
        self.assertEqual(chat_resp.status_code, 200)
        chat_data = json.loads(chat_resp.data)
        self.assertIn("response", chat_data)
        self.assertEqual(chat_data["intent"], "AUDIT_CARBON")

        # 7. Logout
        logout_resp = self.client.get("/logout")
        self.assertEqual(logout_resp.status_code, 302)

        # 8. Post-logout access should be redirected again
        post_logout = self.client.get("/")
        self.assertEqual(post_logout.status_code, 302)


if __name__ == "__main__":
    unittest.main()
