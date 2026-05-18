"""Tests de integración para el recurso /v1/authors."""
import pytest


VALID_AUTHOR = {
    "first_name": "Miguel",
    "last_name1": "Cervantes",
    "last_name2": "Saavedra",
    "country": "ES",
}


def _create_author(client, data: dict | None = None) -> dict:
    payload = data if data is not None else VALID_AUTHOR
    resp = client.post("/v1/authors", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# POST /v1/authors
# ---------------------------------------------------------------------------


def test_create_author_valid_data_returns_201(client):
    resp = client.post("/v1/authors", json=VALID_AUTHOR)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["first_name"] == "Miguel"
    assert body["last_name1"] == "Cervantes"
    assert body["last_name2"] == "Saavedra"
    assert body["country"] == "ES"
    assert "Location" in resp.headers
    assert resp.headers["Location"] == f"/v1/authors/{body['id']}"


def test_create_author_without_optional_last_name2_returns_201(client):
    resp = client.post(
        "/v1/authors",
        json={"first_name": "Ana", "last_name1": "García", "country": "ES"},
    )
    assert resp.status_code == 201
    assert resp.json()["last_name2"] is None


def test_create_author_invalid_country_returns_422(client):
    payload = {**VALID_AUTHOR, "country": "XX"}
    resp = client.post("/v1/authors", json=payload)
    assert resp.status_code == 422
    error = resp.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"


def test_create_author_missing_required_field_returns_422(client):
    resp = client.post("/v1/authors", json={"last_name1": "García", "country": "ES"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_author_empty_first_name_returns_422(client):
    resp = client.post(
        "/v1/authors",
        json={"first_name": "", "last_name1": "García", "country": "ES"},
    )
    assert resp.status_code == 422


def test_create_author_country_lowercase_accepted(client):
    resp = client.post(
        "/v1/authors",
        json={"first_name": "Ana", "last_name1": "García", "country": "es"},
    )
    assert resp.status_code == 201
    assert resp.json()["country"] == "ES"


# ---------------------------------------------------------------------------
# GET /v1/authors/{id}
# ---------------------------------------------------------------------------


def test_get_author_existing_returns_200(client):
    created = _create_author(client)
    resp = client.get(f"/v1/authors/{created['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created["id"]
    assert body["first_name"] == "Miguel"
    assert body["country"] == "ES"


def test_get_author_not_found_returns_404(client):
    resp = client.get("/v1/authors/9999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# GET /v1/authors
# ---------------------------------------------------------------------------


def test_list_authors_empty_returns_200_with_pagination(client):
    resp = client.get("/v1/authors")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["pagination"]["total"] == 0
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["page_size"] == 20


def test_list_authors_filter_by_country(client):
    _create_author(client, {**VALID_AUTHOR, "country": "ES"})
    _create_author(client, {**VALID_AUTHOR, "last_name1": "Rulfo", "country": "MX"})
    resp = client.get("/v1/authors?country=ES")
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["total"] == 1
    assert body["data"][0]["country"] == "ES"


def test_list_authors_pagination(client):
    for i in range(5):
        _create_author(client, {**VALID_AUTHOR, "last_name1": f"Apellido{i}"})
    resp = client.get("/v1/authors?page=1&page_size=2")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["page_size"] == 2


def test_list_authors_ordered_by_last_name1(client):
    _create_author(client, {**VALID_AUTHOR, "last_name1": "Zorrilla"})
    _create_author(client, {**VALID_AUTHOR, "last_name1": "Alarcón"})
    _create_author(client, {**VALID_AUTHOR, "last_name1": "Machado"})
    resp = client.get("/v1/authors")
    names = [a["last_name1"] for a in resp.json()["data"]]
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# PATCH /v1/authors/{id}
# ---------------------------------------------------------------------------


def test_patch_author_partial_update_returns_200(client):
    created = _create_author(client)
    resp = client.patch(
        f"/v1/authors/{created['id']}",
        json={"first_name": "Miguel de"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["first_name"] == "Miguel de"
    assert body["last_name1"] == "Cervantes"
    assert body["country"] == "ES"


def test_patch_author_not_found_returns_404(client):
    resp = client.patch("/v1/authors/9999", json={"first_name": "Nuevo"})
    assert resp.status_code == 404


def test_patch_author_invalid_country_returns_422(client):
    created = _create_author(client)
    resp = client.patch(f"/v1/authors/{created['id']}", json={"country": "ZZ"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /v1/authors/{id}
# ---------------------------------------------------------------------------


def test_delete_author_no_books_returns_204(client):
    created = _create_author(client)
    resp = client.delete(f"/v1/authors/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/v1/authors/{created['id']}").status_code == 404


def test_delete_author_not_found_returns_404(client):
    resp = client.delete("/v1/authors/9999")
    assert resp.status_code == 404


def test_delete_author_with_books_returns_409(client):
    author = _create_author(client)
    client.post(
        "/v1/books",
        json={
            "title": "Don Quijote",
            "publisher": "Robles",
            "year": 1605,
            "authors": [{"author_id": author["id"], "contribution_date": "1605-01-16"}],
        },
    )
    resp = client.delete(f"/v1/authors/{author['id']}")
    assert resp.status_code == 409
    error = resp.json()["error"]
    assert error["code"] == "AUTHOR_HAS_BOOKS"
    assert any("author_id" in d["field"] for d in error["details"])
