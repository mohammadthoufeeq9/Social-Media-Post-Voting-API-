from fastapi.testclient import TestClient
from fast_app.main import app

client=TestClient(app)

def test_docs_page():
    response=client.get('/docs')
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["permissions-policy"] == ("camera=(), microphone=(), geolocation=()")

def test_my_posts_requires_authentication():
    response = client.get("/my-posts")

    assert response.status_code == 401