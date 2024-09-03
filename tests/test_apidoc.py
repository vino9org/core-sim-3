async def test_apidoc_exists(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    body = await response.json
    assert body["openapi"].startswith("3.")
