from pathlib import Path
import hmac
import os

from flask import Flask, jsonify, request, send_from_directory

from database import create_order, init_db, list_orders, update_order_status


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

# Initialize SQLite schema for both Flask and Gunicorn startup.
init_db()


ALLOWED_ORDER_STATUSES = {
    "NEW",
    "PROCESSING",
    "COMPLETED",
    "CANCELLED",
}

ALLOWED_CONTACT_METHODS = {
    "messenger",
    "viber",
    "sms",
}


def admin_authorized():
    auth = request.authorization

    expected_username = os.environ.get("ADMIN_USERNAME", "")
    expected_password = os.environ.get("ADMIN_PASSWORD", "")

    if not expected_username or not expected_password:
        return False

    if not auth:
        return False

    username_ok = hmac.compare_digest(
        auth.username or "",
        expected_username,
    )
    password_ok = hmac.compare_digest(
        auth.password or "",
        expected_password,
    )

    return username_ok and password_ok


@app.before_request
def protect_admin_routes():
    if request.path == "/admin" or request.path.startswith("/api/admin/"):
        if not admin_authorized():
            return (
                jsonify({
                    "ok": False,
                    "error": "Admin authentication required."
                }),
                401,
                {
                    "WWW-Authenticate": 'Basic realm="Miguel Lechon Admin"'
                },
            )


@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/admin")
def admin():
    return send_from_directory(BASE_DIR, "admin.html")


@app.get("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(BASE_DIR / "css", filename)


@app.get("/js/<path:filename>")
def js_files(filename):
    return send_from_directory(BASE_DIR / "js", filename)


@app.get("/images/<path:filename>")
def image_files(filename):
    return send_from_directory(BASE_DIR / "images", filename)


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "service": "miguel-lechon-api",
    })


@app.post("/api/orders")
def create_order_api():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "ok": False,
            "error": "JSON request body is required."
        }), 400

    customer_name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    event_date = str(data.get("eventDate", "")).strip()
    preferred_order = str(data.get("size", "")).strip()
    notes = str(data.get("notes", "")).strip()
    contact_method = str(
        data.get("contactMethod", "messenger")
    ).strip().lower()

    if not customer_name:
        return jsonify({
            "ok": False,
            "error": "Customer name is required."
        }), 400

    if not phone:
        return jsonify({
            "ok": False,
            "error": "Phone number is required."
        }), 400

    if contact_method not in ALLOWED_CONTACT_METHODS:
        return jsonify({
            "ok": False,
            "error": "Invalid contact method."
        }), 400

    order_id = create_order(
        customer_name=customer_name,
        phone=phone,
        event_date=event_date,
        preferred_order=preferred_order,
        notes=notes,
        contact_method=contact_method,
    )

    return jsonify({
        "ok": True,
        "message": "Order inquiry received.",
        "order": {
            "id": order_id,
            "status": "NEW",
        },
    }), 201


@app.get("/api/orders")
def get_orders():
    if not admin_authorized():
        return (
            jsonify({
                "ok": False,
                "error": "Admin authentication required."
            }),
            401,
            {
                "WWW-Authenticate": 'Basic realm="Miguel Lechon Admin"'
            },
        )

    return jsonify({
        "ok": True,
        "orders": list_orders(),
    })



@app.patch("/api/admin/orders/<int:order_id>/status")
def update_admin_order_status(order_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "ok": False,
            "error": "JSON request body is required."
        }), 400

    status = str(data.get("status", "")).strip().upper()

    if status not in ALLOWED_ORDER_STATUSES:
        return jsonify({
            "ok": False,
            "error": "Invalid order status."
        }), 400

    updated = update_order_status(
        order_id=order_id,
        status=status,
    )

    if not updated:
        return jsonify({
            "ok": False,
            "error": "Order not found."
        }), 404

    return jsonify({
        "ok": True,
        "message": "Order status updated.",
        "order": {
            "id": order_id,
            "status": status,
        },
    }), 200

@app.get("/api/admin/orders")
def get_admin_orders():
    return jsonify({
        "ok": True,
        "orders": list_orders(),
    })


if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        debug=False,
    )
