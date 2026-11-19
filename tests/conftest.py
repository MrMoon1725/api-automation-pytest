import os
import sys
from pathlib import Path
from typing import Iterator

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mock_api_server import create_server


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    external_url = os.getenv("API_BASE_URL")
    if external_url:
        yield external_url.rstrip("/")
        return

    server, port = create_server()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


@pytest.fixture(scope="session")
def auth_headers(base_url: str) -> dict:
    resp = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "password123"},
        timeout=5,
    )
    assert resp.status_code == 200
    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}
