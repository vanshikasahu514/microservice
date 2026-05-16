import pytest
import requests
import json
import os

BASE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8001")

def load_contract(name):
    """JSON contract file load karo"""
    contract_path = os.path.join(
        os.path.dirname(__file__),
        "contracts",
        f"{name}.json"
    )
    with open(contract_path) as f:
        return json.load(f)


class TestUserServiceContract:
    """
    Ye tests ensure karte hain ki User Service
    wahi response deta hai jo Product Service expect karta hai.
    """

    def test_register_response_has_required_fields(self):
        """Contract: register response mein id, username, email hona chahiye"""
        contract = load_contract("user_service")

        payload = {
            "username": "contract_test_user",
            "password": "testpass123",
            "email": "contract@test.com"
        }

        resp = requests.post(
            f"{BASE_URL}/api/users/register/",
            json=payload
        )

        # Status code check
        assert resp.status_code == contract["expected_response"]["status_code"], \
            f"Expected {contract['expected_response']['status_code']}, got {resp.status_code}"

        data = resp.json()

        # Required fields check
        for field in contract["expected_response"]["required_fields"]:
            assert field in data, \
                f"Contract broken! Field '{field}' missing from response"

    def test_register_response_field_types(self):
        """Contract: field types sahi hone chahiye"""
        contract = load_contract("user_service")

        payload = {
            "username": "typecheck_user",
            "password": "testpass123",
            "email": "types@test.com"
        }

        resp = requests.post(
            f"{BASE_URL}/api/users/register/",
            json=payload
        )

        data = resp.json()
        type_map = {"int": int, "str": str, "bool": bool}

        for field, expected_type in contract["expected_response"]["field_types"].items():
            if field in data:
                actual_type = type(data[field])
                assert actual_type == type_map[expected_type], \
                    f"Contract broken! '{field}' should be {expected_type}, got {actual_type.__name__}"

    def test_login_returns_tokens(self):
        """Contract: login response mein access aur refresh token hona chahiye"""
        # Pehle register karo
        requests.post(f"{BASE_URL}/api/users/register/", json={
            "username": "login_contract_user",
            "password": "testpass123",
            "email": "login@test.com"
        })

        # Ab login karo
        resp = requests.post(
            f"{BASE_URL}/api/users/login/",
            json={"username": "login_contract_user", "password": "testpass123"}
        )

        assert resp.status_code == 200
        data = resp.json()

        # JWT tokens hone chahiye
        assert "access" in data, "Contract broken! 'access' token missing"
        assert "refresh" in data, "Contract broken! 'refresh' token missing"

        # Token string hona chahiye
        assert isinstance(data["access"], str), "access token string hona chahiye"
        assert len(data["access"]) > 20, "access token too short — invalid JWT"

    def test_no_password_in_response(self):
        """Contract: password kabhi response mein nahi aana chahiye (security)"""
        payload = {
            "username": "security_test_user",
            "password": "secretpass123",
            "email": "security@test.com"
        }

        resp = requests.post(
            f"{BASE_URL}/api/users/register/",
            json=payload
        )

        data = resp.json()
        assert "password" not in data, \
            "SECURITY CONTRACT BROKEN! Password exposed in response!"