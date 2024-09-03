async def test_apidoc_exists(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert body["openapi"].startswith("3.")
