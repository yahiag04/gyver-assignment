def test_health_endpoint_returns_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_displays_the_annunci_application(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Annunci Gyver" in response.text
