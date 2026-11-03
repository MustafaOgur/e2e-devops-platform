import pytest

URL = "/api/todos"


def create_todo(client, title="süt al"):
    return client.post(URL, json={"title": title}).json()


def test_create_todo_returns_created_todo(client):
    response = client.post(URL, json={"title": "süt al"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "süt al"
    assert body["completed"] is False
    assert body["created_at"]


def test_create_todo_strips_whitespace(client):
    response = client.post(URL, json={"title": "  süt al  "})

    assert response.json()["title"] == "süt al"


@pytest.mark.parametrize(
    "payload",
    [{}, {"title": ""}, {"title": "   "}, {"title": "x" * 201}],
    ids=["missing", "empty", "blank", "too-long"],
)
def test_create_todo_rejects_invalid_title(client, payload):
    response = client.post(URL, json=payload)

    assert response.status_code == 422


def test_create_todo_accepts_max_length_title(client):
    response = client.post(URL, json={"title": "x" * 200})

    assert response.status_code == 201


def test_list_todos_is_empty_at_start(client):
    response = client.get(URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_todos_returns_newest_first(client):
    create_todo(client, "ilk")
    create_todo(client, "son")

    titles = [todo["title"] for todo in client.get(URL).json()]

    assert titles == ["son", "ilk"]


def test_get_todo_returns_todo(client):
    todo = create_todo(client)

    response = client.get(f"{URL}/{todo['id']}")

    assert response.status_code == 200
    assert response.json() == todo


def test_get_todo_returns_404_when_missing(client):
    response = client.get(f"{URL}/999")

    assert response.status_code == 404


def test_update_todo_changes_only_completed(client):
    todo = create_todo(client)

    response = client.patch(f"{URL}/{todo['id']}", json={"completed": True})

    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == todo["title"]


def test_update_todo_changes_only_title(client):
    todo = create_todo(client)

    response = client.patch(f"{URL}/{todo['id']}", json={"title": "ekmek al"})

    assert response.status_code == 200
    assert response.json()["title"] == "ekmek al"
    assert response.json()["completed"] is False


def test_update_todo_ignores_null_values(client):
    todo = create_todo(client)

    response = client.patch(
        f"{URL}/{todo['id']}", json={"title": None, "completed": None}
    )

    assert response.status_code == 200
    assert response.json() == todo


def test_update_todo_rejects_blank_title(client):
    todo = create_todo(client)

    response = client.patch(f"{URL}/{todo['id']}", json={"title": "   "})

    assert response.status_code == 422


def test_update_todo_persists_change(client):
    todo = create_todo(client)

    client.patch(f"{URL}/{todo['id']}", json={"completed": True})

    assert client.get(f"{URL}/{todo['id']}").json()["completed"] is True


def test_update_todo_returns_404_when_missing(client):
    response = client.patch(f"{URL}/999", json={"completed": True})

    assert response.status_code == 404


def test_delete_todo_removes_todo(client):
    todo = create_todo(client)

    response = client.delete(f"{URL}/{todo['id']}")

    assert response.status_code == 204
    assert client.get(f"{URL}/{todo['id']}").status_code == 404


def test_delete_todo_returns_404_when_missing(client):
    response = client.delete(f"{URL}/999")

    assert response.status_code == 404
