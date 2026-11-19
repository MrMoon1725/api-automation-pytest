import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Tuple


class _BookingStore:
    def __init__(self) -> None:
        self.next_id = 1
        self.bookings: Dict[int, Dict[str, Any]] = {}
        self.valid_token = "qa-token-secret-2026"


def create_server(host: str = "127.0.0.1", port: int = 0) -> Tuple[ThreadingHTTPServer, int]:
    store = _BookingStore()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, code: int, payload: Any) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8"))

        def _is_authorized(self) -> bool:
            auth = self.headers.get("Authorization", "")
            return auth == f"Bearer {store.valid_token}"

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send_json(200, {"status": "ok", "service": "booking-api"})
                return
            if self.path == "/bookings":
                items = [{"bookingid": k, "booking": v} for k, v in store.bookings.items()]
                self._send_json(200, items)
                return
            if self.path.startswith("/bookings/"):
                try:
                    bid = int(self.path.split("/")[-1])
                except ValueError:
                    self._send_json(400, {"error": "Invalid booking ID"})
                    return
                if bid not in store.bookings:
                    self._send_json(404, {"error": "Booking not found"})
                    return
                self._send_json(200, store.bookings[bid])
                return
            self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            try:
                data = self._read_json()
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Malformed JSON"})
                return

            if self.path == "/auth":
                if data.get("username") == "admin" and data.get("password") == "password123":
                    self._send_json(200, {"token": store.valid_token})
                else:
                    self._send_json(401, {"error": "Invalid credentials"})
                return

            if self.path == "/bookings":
                if not self._is_authorized():
                    self._send_json(401, {"error": "Unauthorized"})
                    return
                required = {"firstname", "lastname", "totalprice", "depositpaid", "bookingdates"}
                if not required.issubset(data.keys()) or data.get("totalprice", -1) < 0:
                    self._send_json(400, {"error": "Invalid booking payload"})
                    return
                bid = store.next_id
                store.next_id += 1
                store.bookings[bid] = data
                self._send_json(201, {"bookingid": bid, "booking": data})
                return

            self._send_json(404, {"error": "Not found"})

        def do_PUT(self) -> None:
            if not self.path.startswith("/bookings/"):
                self._send_json(404, {"error": "Not found"})
                return
            if not self._is_authorized():
                self._send_json(401, {"error": "Unauthorized"})
                return
            try:
                bid = int(self.path.split("/")[-1])
            except ValueError:
                self._send_json(400, {"error": "Invalid booking ID"})
                return
            if bid not in store.bookings:
                self._send_json(404, {"error": "Booking not found"})
                return
            data = self._read_json()
            store.bookings[bid] = data
            self._send_json(200, data)

        def do_DELETE(self) -> None:
            if not self.path.startswith("/bookings/"):
                self._send_json(404, {"error": "Not found"})
                return
            if not self._is_authorized():
                self._send_json(401, {"error": "Unauthorized"})
                return
            try:
                bid = int(self.path.split("/")[-1])
            except ValueError:
                self._send_json(400, {"error": "Invalid booking ID"})
                return
            if bid not in store.bookings:
                self._send_json(404, {"error": "Booking not found"})
                return
            del store.bookings[bid]
            self._send_json(204, {})

    server = ThreadingHTTPServer((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]
