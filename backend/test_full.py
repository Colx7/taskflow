import traceback
import sys
sys.path.insert(0, ".")

print("=== Loading FastAPI... ===")
try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import engine, Base
    print("=== App loaded OK ===")
except Exception as e:
    print(f"LOAD ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

print("=== Testing register... ===")
client = TestClient(app)
try:
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "testuser99",
            "email": "t99@test.com",
            "password": "test123456",
        },
    )
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text[:400]}")
except Exception as e:
    print(f"REQUEST ERROR: {e}")
    traceback.print_exc()
