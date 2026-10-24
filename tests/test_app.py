import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
import app as appmod


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.c = appmod.app.test_client()

    def test_health(self):
        self.assertEqual(self.c.get("/health").get_json()["status"], "ok")

    def test_signup_and_signin_same_email(self):
        a = self.c.post("/api/users", json={"name": "Test", "email": "t@x.edu"})
        b = self.c.post("/api/users", json={"name": "Test", "email": "T@x.edu"})
        self.assertEqual(a.status_code, 201)
        self.assertEqual(b.status_code, 200)
        self.assertEqual(a.get_json()["id"], b.get_json()["id"])

    def test_invalid_user(self):
        self.assertEqual(self.c.post("/api/users", json={"name": "", "email": "bad"}).status_code, 400)

    def test_search(self):
        r = self.c.get("/api/search?skill=pyth").get_json()
        self.assertTrue(any(x["name"] == "Ravi Kumar" for x in r))

    def test_perfect_match(self):
        # Ravi (1) offers Python, wants Guitar; Anitha (2) offers Guitar, wants Python
        m = self.c.get("/api/matches/1").get_json()
        self.assertIn("Anitha Reddy", [x["name"] for x in m["perfect"]])

    def test_skill_duplicate_and_request_flow(self):
        body = {"user_id": 1, "skill": "Docker", "kind": "offer", "level": "Intermediate"}
        self.assertEqual(self.c.post("/api/skills", json=body).status_code, 201)
        self.assertEqual(self.c.post("/api/skills", json=body).status_code, 409)
        r = self.c.post("/api/requests", json={"from_user": 1, "to_user": 2, "offered_skill": "Python", "wanted_skill": "Guitar"})
        self.assertEqual(r.status_code, 201)
        rid = r.get_json()["id"]
        self.assertEqual(self.c.patch(f"/api/requests/{rid}", json={"status": "accepted"}).status_code, 200)
        self.assertEqual(self.c.patch(f"/api/requests/{rid}", json={"status": "nope"}).status_code, 400)
        self.assertEqual(self.c.post("/api/requests", json={"from_user": 1, "to_user": 1, "offered_skill": "a", "wanted_skill": "b"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
