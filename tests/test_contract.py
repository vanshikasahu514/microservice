import pytest
import requests
import json
import os
import uuid

BASE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:8001')

def load_contract(name):
    contract_path = os.path.join(
        os.path.dirname(__file__),
        'contracts',
        f'{name}.json'
    )
    with open(contract_path) as f:
        return json.load(f)

def unique_user():
    """Har test run mein naya unique username — conflict nahi hoga"""
    uid = str(uuid.uuid4())[:8]
    return {
        "username": f"test_{uid}",
        "password": "testpass123",
        "email": f"test_{uid}@test.com"
    }

class TestUserServiceContract:

    def test_register_has_required_fields(self):
        contract = load_contract('user_service')
        payload = unique_user()

        resp = requests.post(
            f'{BASE_URL}/api/users/register/',
            json=payload
        )

        assert resp.status_code == contract['expected_response']['status_code'], \
            f"Expected 201, got {resp.status_code}. Response: {resp.text}"

        data = resp.json()
        for field in contract['expected_response']['required_fields']:
            assert field in data, f'Field missing: {field}'

    def test_register_field_types(self):
        contract = load_contract('user_service')
        payload = unique_user()

        resp = requests.post(
            f'{BASE_URL}/api/users/register/',
            json=payload
        )

        assert resp.status_code == 201, \
            f"Register failed: {resp.text}"

        data = resp.json()
        type_map = {'int': int, 'str': str, 'bool': bool}

        for field, expected_type in contract['expected_response']['field_types'].items():
            if field in data:
                assert type(data[field]) == type_map[expected_type], \
                    f'{field} wrong type! got {type(data[field]).__name__}'

    def test_login_returns_jwt_tokens(self):
        payload = unique_user()

        # Pehle register karo
        requests.post(f'{BASE_URL}/api/users/register/', json=payload)

        # Ab login karo
        resp = requests.post(f'{BASE_URL}/api/users/login/', json={
            'username': payload['username'],
            'password': payload['password']
        })

        assert resp.status_code == 200, \
            f"Login failed: {resp.text}"

        data = resp.json()
        assert 'access' in data, 'access token missing!'
        assert 'refresh' in data, 'refresh token missing!'
        assert isinstance(data['access'], str), 'access token string hona chahiye'
        assert len(data['access']) > 20, 'token too short!'

    def test_password_not_in_response(self):
        payload = unique_user()

        resp = requests.post(
            f'{BASE_URL}/api/users/register/',
            json=payload
        )

        assert resp.status_code == 201, \
            f"Register failed: {resp.text}"

        assert 'password' not in resp.json(), \
            'SECURITY BREACH! Password exposed in response!'