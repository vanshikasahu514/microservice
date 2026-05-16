from flask import Flask, request, jsonify, Response
import requests
import os

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8001")
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://localhost:8002")

app = Flask(__name__)

# USER_SERVICE_URL = "http://localhost:8001"
# PRODUCT_SERVICE_URL = "http://localhost:8002"


def proxy_request(target_url):
    query_string = request.query_string.decode()
    if query_string:
        target_url = f"{target_url}?{query_string}"

    headers = {key: value for key, value in request.headers if key != 'Host'}

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            json=request.get_json(silent=True),
            data=request.form or None,
            timeout=10
        )
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Service unavailable. Please try later."}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Service timed out."}), 504


# ── USER SERVICE ──────────────────────────────────────
# FIX: do alag routes — list ke liye aur detail ke liye

@app.route('/api/users/', methods=['GET', 'POST'])
@app.route('/api/users', methods=['GET', 'POST'])
def users_list():
    target_url = f"{USER_SERVICE_URL}/api/users/"
    print(f"[Gateway] → User Service LIST: {request.method} {target_url}")
    return proxy_request(target_url)

@app.route('/api/users/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_service_proxy(subpath):
    target_url = f"{USER_SERVICE_URL}/api/users/{subpath}"
    print(f"[Gateway] → User Service: {request.method} {target_url}")
    return proxy_request(target_url)


# ── PRODUCT SERVICE ───────────────────────────────────

@app.route('/api/products/', methods=['GET', 'POST'])
@app.route('/api/products', methods=['GET', 'POST'])
def products_list():
    target_url = f"{PRODUCT_SERVICE_URL}/api/products/"
    print(f"[Gateway] → Product Service LIST: {request.method} {target_url}")
    return proxy_request(target_url)

@app.route('/api/products/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def product_service_proxy(subpath):
    target_url = f"{PRODUCT_SERVICE_URL}/api/products/{subpath}"
    print(f"[Gateway] → Product Service: {request.method} {target_url}")
    return proxy_request(target_url)


# ── CATEGORIES ────────────────────────────────────────

@app.route('/api/categories/', methods=['GET', 'POST'])
@app.route('/api/categories', methods=['GET', 'POST'])
def categories_list():
    target_url = f"{PRODUCT_SERVICE_URL}/api/categories/"
    print(f"[Gateway] → Categories LIST: {request.method} {target_url}")
    return proxy_request(target_url)

@app.route('/api/categories/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def category_service_proxy(subpath):
    target_url = f"{PRODUCT_SERVICE_URL}/api/categories/{subpath}"
    print(f"[Gateway] → Categories: {request.method} {target_url}")
    return proxy_request(target_url)


# ── HEALTH CHECK ──────────────────────────────────────

@app.route('/health', methods=['GET'])
def health_check():
    status = {"gateway": "ok", "services": {}}
    for name, url in [("user_service", USER_SERVICE_URL), ("product_service", PRODUCT_SERVICE_URL)]:
        try:
            requests.get(f"{url}/admin/", timeout=2)
            status["services"][name] = "ok"
        except:
            status["services"][name] = "unreachable"
    return jsonify(status)


@app.route('/')
def index():
    return jsonify({
        "message": "Microservices API Gateway",
        "version": "1.0",
        "routes": {
            "Register":  "POST /api/users/register/",
            "Login":     "POST /api/users/login/",
            "Profile":   "GET  /api/users/profile/",
            "Products":  "GET  /api/products/",
            "Categories":"GET  /api/categories/",
            "Health":    "GET  /health"
        }
    })


if __name__ == '__main__':
    app.run(port=5000, debug=True)