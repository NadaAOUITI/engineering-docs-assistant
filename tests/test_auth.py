# Auth endpoint and JWT protection tests.

def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "a-secure-password-1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "first-password-1"}
    assert client.post("/auth/register", json=payload).status_code == 200
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert "detail" in response.json()


def test_login_success(client):
    email = "loginok@example.com"
    password = "correct-password-1"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)


def test_login_wrong_password(client):
    email = "wrongpw@example.com"
    client.post("/auth/register", json={"email": email, "password": "right-password-1"})
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "wrong-password-1"},
    )
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/documents/")
    assert response.status_code == 401
