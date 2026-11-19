import requests
from src.schemas import AuthTokenResponse, BookingPayload, BookingRecord, HealthResponse

SLA_MS = 500


def _sample_booking() -> dict:
    return {
        "firstname": "Mateo",
        "lastname": "Pimienta",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-05"},
        "additionalneeds": "Breakfast",
    }


def test_health_endpoint_contract_and_sla(base_url: str) -> None:
    resp = requests.get(f"${base_url}/health", timeout=5)
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() * 1000 < SLA_MS
    parsed = HealthResponse(**resp.json())
    assert parsed.status == "ok"


def test_auth_valid_credentials_returns_token(base_url: str) -> None:
    resp = requests.post(
        f"${base_url}/auth",
        json={"username": "admin", "password": "password123"},
        timeout=5,
    )
    assert resp.status_code == 200
    parsed = AuthTokenResponse(**resp.json())
    assert len(parsed.token) >= 8


def test_auth_invalid_credentials_returns_401(base_url: str) -> None:
    resp = requests.post(
        f"${base_url}/auth",
        json={"username": "admin", "password": "wrong-password"},
        timeout=5,
    )
    assert resp.status_code == 401
    assert "error" in resp.json()


def test_create_booking_without_auth_returns_401(base_url: str) -> None:
    resp = requests.post(f"${base_url}/bookings", json=_sample_booking(), timeout=5)
    assert resp.status_code == 401


def test_create_booking_invalid_payload_returns_400(base_url: str, auth_headers: dict) -> None:
    bad_payload = _sample_booking()
    bad_payload["totalprice"] = -10
    resp = requests.post(
        f"${base_url}/bookings",
        json=bad_payload,
        headers=auth_headers,
        timeout=5,
    )
    assert resp.status_code == 400


def test_full_crud_lifecycle_and_pydantic_contracts(base_url: str, auth_headers: dict) -> None:
    create_resp = requests.post(
        f"${base_url}/bookings",
        json=_sample_booking(),
        headers=auth_headers,
        timeout=5,
    )
    assert create_resp.status_code == 201
    assert create_resp.elapsed.total_seconds() * 1000 < SLA_MS
    created = BookingRecord(**create_resp.json())
    booking_id = created.bookingid

    get_resp = requests.get(f"${base_url}/bookings/${booking_id}", timeout=5)
    assert get_resp.status_code == 200
    fetched = BookingPayload(**get_resp.json())
    assert fetched.firstname == "Mateo"

    updated_payload = _sample_booking()
    updated_payload["totalprice"] = 320
    updated_payload["additionalneeds"] = "Late Checkout"
    put_resp = requests.put(
        f"${base_url}/bookings/${booking_id}",
        json=updated_payload,
        headers=auth_headers,
        timeout=5,
    )
    assert put_resp.status_code == 200
    updated = BookingPayload(**put_resp.json())
    assert updated.totalprice == 320
    assert updated.additionalneeds == "Late Checkout"

    del_resp = requests.delete(
        f"${base_url}/bookings/${booking_id}",
        headers=auth_headers,
        timeout=5,
    )
    assert del_resp.status_code == 204

    verify_resp = requests.get(f"${base_url}/bookings/${booking_id}", timeout=5)
    assert verify_resp.status_code == 404


def test_get_nonexistent_booking_returns_404(base_url: str) -> None:
    resp = requests.get(f"${base_url}/bookings/999999", timeout=5)
    assert resp.status_code == 404
