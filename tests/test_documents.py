# Document upload, validation, listing, and deletion tests.

from sqlalchemy import select

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.user import User


def _register_and_token(client, email: str, password: str = "a-secure-password-1") -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_upload_success(client):
    token = _register_and_token(client, "uploadok@example.com")
    response = client.post(
        "/documents/",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "notes.txt"
    assert data["file_type"] == "txt"
    assert data["status"] == "pending"
    assert "id" in data


def test_upload_rejects_wrong_file_type(client):
    token = _register_and_token(client, "badtype@example.com")
    response = client.post(
        "/documents/",
        files={"file": ("malware.exe", b"data", "application/octet-stream")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 400


def test_upload_rejects_file_too_large(client):
    token = _register_and_token(client, "toobig@example.com")
    limit_bytes = 10 * 1024 * 1024
    payload = b"x" * (limit_bytes + 1)
    response = client.post(
        "/documents/",
        files={"file": ("big.txt", payload, "text/plain")},
        headers=_auth_headers(token),
    )
    assert response.status_code == 400


def test_list_documents_scoped_to_current_user(client):
    t1 = _register_and_token(client, "user1@example.com")
    t2 = _register_and_token(client, "user2@example.com")
    client.post(
        "/documents/",
        files={"file": ("a.txt", b"one", "text/plain")},
        headers=_auth_headers(t1),
    )
    client.post(
        "/documents/",
        files={"file": ("b.txt", b"two", "text/plain")},
        headers=_auth_headers(t2),
    )
    r1 = client.get("/documents/", headers=_auth_headers(t1))
    r2 = client.get("/documents/", headers=_auth_headers(t2))
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert len(r1.json()) == 1
    assert len(r2.json()) == 1
    assert r1.json()[0]["filename"] == "a.txt"
    assert r2.json()[0]["filename"] == "b.txt"


def test_delete_removes_document_and_chunks(client, db_session):
    token = _register_and_token(client, "deleter@example.com")
    user = db_session.scalars(select(User).where(User.email == "deleter@example.com")).one()
    r = client.post(
        "/documents/",
        files={"file": ("chunked.txt", b"hello", "text/plain")},
        headers=_auth_headers(token),
    )
    doc_id = r.json()["id"]
    chunk = Chunk(
        document_id=doc_id,
        user_id=user.id,
        text="segment",
        embedding=[0.0] * 768,
        chunk_index=0,
    )
    db_session.add(chunk)
    db_session.flush()

    del_r = client.delete(f"/documents/{doc_id}", headers=_auth_headers(token))
    assert del_r.status_code == 204

    db_session.expire_all()
    assert db_session.get(Document, doc_id) is None
    remaining = db_session.scalars(select(Chunk).where(Chunk.user_id == user.id)).all()
    assert remaining == []
