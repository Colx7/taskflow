import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 用不冲突的用户名测试
resp = client.post(
    "/api/auth/register",
    json={
        "username": "testuser_final",
        "email": "final_test@example.com",
        "password": "SecurePass123!",
    },
)

print(f"Status: {resp.status_code}")
print(f"Body: {resp.text}")
