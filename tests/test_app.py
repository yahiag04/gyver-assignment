from io import BytesIO

from PIL import Image

from app.seed import seed_database


def test_health_endpoint_returns_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_displays_the_annunci_application(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Annunci Gyver" in response.text


def test_home_page_uses_bootstrap_responsive_layout_and_dark_navbar(client):
    response = client.get("/")

    assert "bootstrap@5.3.8/dist/css/bootstrap.min.css" in response.text
    assert 'class="navbar navbar-dark navbar-gyver"' in response.text
    assert 'class="workspace row g-3"' in response.text
    assert "col-12 col-xl-4" in response.text
    assert "col-12 col-xl-8" in response.text


def _png_bytes(width, height):
    image = Image.new("RGB", (width, height), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _seed_demo_ads(client):
    with client.app.state.session_factory() as session:
        seed_database(session)


def test_whatsapp_image_upload_requires_portrait_a4_ratio(client):
    _seed_demo_ads(client)

    response = client.post(
        "/api/ads/seed-ad-whatsapp-001/variants/seed-variant-whatsapp-001/image",
        files={"image": ("square.png", _png_bytes(300, 300), "image/png")},
    )

    assert response.status_code == 422
    assert "A4" in response.json()["detail"]


def test_whatsapp_image_upload_accepts_a4_ratio(client):
    _seed_demo_ads(client)

    response = client.post(
        "/api/ads/seed-ad-whatsapp-001/variants/seed-variant-whatsapp-001/image",
        files={"image": ("a4.png", _png_bytes(210, 297), "image/png")},
    )

    assert response.status_code == 201


def test_non_whatsapp_image_upload_keeps_flexible_ratio(client):
    _seed_demo_ads(client)

    response = client.post(
        "/api/ads/seed-ad-instagram-001/variants/seed-variant-instagram-001/image",
        files={"image": ("square.png", _png_bytes(300, 300), "image/png")},
    )

    assert response.status_code == 201
