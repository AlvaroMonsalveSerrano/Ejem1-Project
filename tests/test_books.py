"""Tests de integración para el recurso /v1/books."""
import pytest


VALID_AUTHOR = {
    "first_name": "Miguel",
    "last_name1": "Cervantes",
    "last_name2": "Saavedra",
    "country": "ES",
}


def _create_author(client, data: dict | None = None) -> dict:
    """Crea un autor vía POST y devuelve el cuerpo de respuesta; falla si no es 201."""
    payload = data if data is not None else VALID_AUTHOR
    resp = client.post("/v1/authors", json=payload)
    assert resp.status_code == 201
    return resp.json()


def _create_book(client, author_id: int, overrides: dict | None = None) -> dict:
    """Crea un libro vía POST con un autor; permite sobreescribir campos del payload."""
    payload = {
        "title": "Don Quijote de la Mancha",
        "publisher": "Francisco de Robles",
        "year": 1605,
        "authors": [{"author_id": author_id, "contribution_date": "1605-01-16"}],
    }
    if overrides:
        payload.update(overrides)
    resp = client.post("/v1/books", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# POST /v1/books
# ---------------------------------------------------------------------------


def test_create_book_valid_data_returns_201(client):
    author = _create_author(client)
    resp = client.post(
        "/v1/books",
        json={
            "title": "Don Quijote de la Mancha",
            "publisher": "Francisco de Robles",
            "year": 1605,
            "authors": [{"author_id": author["id"], "contribution_date": "1605-01-16"}],
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["title"] == "Don Quijote de la Mancha"
    assert body["year"] == 1605
    assert len(body["authors"]) == 1
    assert body["authors"][0]["id"] == author["id"]
    assert body["authors"][0]["contribution_date"] == "1605-01-16"
    assert "Location" in resp.headers
    assert resp.headers["Location"] == f"/v1/books/{body['id']}"


def test_create_book_empty_authors_returns_422(client):
    resp = client.post(
        "/v1/books",
        json={
            "title": "Un libro",
            "publisher": "Editorial",
            "year": 2000,
            "authors": [],
        },
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_book_nonexistent_author_returns_404(client):
    resp = client.post(
        "/v1/books",
        json={
            "title": "Un libro",
            "publisher": "Editorial",
            "year": 2000,
            "authors": [{"author_id": 9999, "contribution_date": "2000-01-01"}],
        },
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


def test_create_book_invalid_year_too_low_returns_422(client):
    author = _create_author(client)
    resp = client.post(
        "/v1/books",
        json={
            "title": "Antiguo",
            "publisher": "Ed",
            "year": 999,
            "authors": [{"author_id": author["id"], "contribution_date": "1000-01-01"}],
        },
    )
    assert resp.status_code == 422


def test_create_book_invalid_year_too_high_returns_422(client):
    author = _create_author(client)
    resp = client.post(
        "/v1/books",
        json={
            "title": "Futuro",
            "publisher": "Ed",
            "year": 2101,
            "authors": [{"author_id": author["id"], "contribution_date": "2100-01-01"}],
        },
    )
    assert resp.status_code == 422


def test_create_book_missing_authors_field_returns_422(client):
    resp = client.post(
        "/v1/books",
        json={"title": "Un libro", "publisher": "Editorial", "year": 2000},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /v1/books/{id}
# ---------------------------------------------------------------------------


def test_get_book_includes_authors_embedded(client):
    author = _create_author(client)
    book = _create_book(client, author["id"])
    resp = client.get(f"/v1/books/{book['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == book["id"]
    assert len(body["authors"]) == 1
    a = body["authors"][0]
    assert a["id"] == author["id"]
    assert a["first_name"] == "Miguel"
    assert a["contribution_date"] == "1605-01-16"


def test_get_book_not_found_returns_404(client):
    resp = client.get("/v1/books/9999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# GET /v1/books
# ---------------------------------------------------------------------------


def test_list_books_empty_returns_200_with_pagination(client):
    resp = client.get("/v1/books")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


def test_list_books_filter_by_title_contains(client):
    author = _create_author(client)
    _create_book(client, author["id"], {"title": "Don Quijote de la Mancha"})
    _create_book(client, author["id"], {"title": "La Odisea"})
    resp = client.get("/v1/books?title=quijote")
    body = resp.json()
    assert body["pagination"]["total"] == 1
    assert "Quijote" in body["data"][0]["title"]


def test_list_books_filter_by_author_id(client):
    author1 = _create_author(client, {**VALID_AUTHOR, "last_name1": "Cervantes"})
    author2 = _create_author(client, {**VALID_AUTHOR, "last_name1": "Homero"})
    _create_book(client, author1["id"], {"title": "Don Quijote"})
    _create_book(client, author2["id"], {"title": "La Odisea"})
    resp = client.get(f"/v1/books?author_id={author1['id']}")
    body = resp.json()
    assert body["pagination"]["total"] == 1
    assert body["data"][0]["title"] == "Don Quijote"


def test_list_books_ordered_by_title(client):
    author = _create_author(client)
    _create_book(client, author["id"], {"title": "Zorro"})
    _create_book(client, author["id"], {"title": "Alicia"})
    _create_book(client, author["id"], {"title": "Moby Dick"})
    resp = client.get("/v1/books")
    titles = [b["title"] for b in resp.json()["data"]]
    assert titles == sorted(titles)


def test_list_books_pagination(client):
    author = _create_author(client)
    for i in range(5):
        _create_book(client, author["id"], {"title": f"Libro {i}"})
    resp = client.get("/v1/books?page=2&page_size=2")
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["pagination"]["total"] == 5
    assert body["pagination"]["page"] == 2


# ---------------------------------------------------------------------------
# PATCH /v1/books/{id}
# ---------------------------------------------------------------------------


def test_patch_book_title_update(client):
    author = _create_author(client)
    book = _create_book(client, author["id"])
    resp = client.patch(f"/v1/books/{book['id']}", json={"title": "Don Quijote"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Don Quijote"
    assert body["year"] == 1605
    assert len(body["authors"]) == 1


def test_patch_book_replace_authors(client):
    author1 = _create_author(client, {**VALID_AUTHOR, "last_name1": "Cervantes"})
    author2 = _create_author(client, {**VALID_AUTHOR, "last_name1": "Homero"})
    book = _create_book(client, author1["id"])
    resp = client.patch(
        f"/v1/books/{book['id']}",
        json={
            "authors": [
                {"author_id": author1["id"], "contribution_date": "1605-01-16"},
                {"author_id": author2["id"], "contribution_date": "1615-11-01"},
            ]
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["authors"]) == 2
    author_ids = {a["id"] for a in body["authors"]}
    assert author1["id"] in author_ids
    assert author2["id"] in author_ids


def test_patch_book_authors_empty_list_returns_422(client):
    author = _create_author(client)
    book = _create_book(client, author["id"])
    resp = client.patch(f"/v1/books/{book['id']}", json={"authors": []})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_book_not_found_returns_404(client):
    resp = client.patch("/v1/books/9999", json={"title": "Nuevo"})
    assert resp.status_code == 404


def test_patch_book_nonexistent_author_returns_404(client):
    author = _create_author(client)
    book = _create_book(client, author["id"])
    resp = client.patch(
        f"/v1/books/{book['id']}",
        json={"authors": [{"author_id": 9999, "contribution_date": "2000-01-01"}]},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /v1/books/{id}
# ---------------------------------------------------------------------------


def test_delete_book_returns_204_authors_unaffected(client):
    author = _create_author(client)
    book = _create_book(client, author["id"])
    resp = client.delete(f"/v1/books/{book['id']}")
    assert resp.status_code == 204
    assert client.get(f"/v1/books/{book['id']}").status_code == 404
    assert client.get(f"/v1/authors/{author['id']}").status_code == 200


def test_delete_book_not_found_returns_404(client):
    resp = client.delete("/v1/books/9999")
    assert resp.status_code == 404
