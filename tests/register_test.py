import asyncio

import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from alembic import command
from alembic.config import Config
from app.main import app

@pytest_asyncio.fixture(name='client') #стандартное создание асинхронного клиента для теста
async def async_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def alembic_test_data_seeding():
    config = Config('alembic_test.ini')
    await asyncio.to_thread(command.upgrade, config, 'head')
    yield # Код выше выполняется до теста, а ниже - после
    await asyncio.to_thread(command.downgrade, config, '5b61b82cba28')

class TestRegister:
    @pytest.mark.asyncio
    async def test_success_signup(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password1234','telegram_id': 1134534511,
                'city': 'City1'}
        response = await client.put("register/signup", data=data)
        assert 'username' in response.json()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_password_do_not_match(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password12534',
                'telegram_id': 1134534511, 'city': 'City1'}
        response = await client.put("register/signup", data=data)
        assert response.json()['detail'] == 'Passwords do not match'
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_short_password(self, client):
        data = {'username': 'human2', 'password': 'pass', 'password_confirmation': 'pass',
                'telegram_id': 1134534511, 'city': 'City1'}
        response = await client.put("register/signup", data=data)
        assert response.json()['detail'] == 'Password len must be between 8 and 64'
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_long_password(self, client):
        data = {'username': 'human2', 'password': 'pass' * 40, 'password_confirmation': 'pass' * 40,
                'telegram_id': 1134534511, 'city': 'City1'}
        response = await client.put("register/signup", data=data)
        assert response.json()['detail'] == 'Password len must be between 8 and 64'
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_name_taken(self, client):
        data = {'username': 'user1', 'password': 'password1234', 'password_confirmation': 'password1234',
                'telegram_id': 1134534511,
                'city': 'City1'}
        response = await client.put("register/signup", data=data)
        assert response.json()['detail'] == "username is already taken!"
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_telegram_id_taken(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password1234',
                'telegram_id': 591989105,
                'city': 'City1'}
        response = await client.put("register/signup", data=data)
        assert response.json()['detail'] == "telegram_id is already taken!"
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_city_not_found(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password1234',
                'telegram_id': 591989105,
                'city': 'City15'}
        response = await client.put("register/signup", data=data)
        assert response.status_code == 404
        assert response.json()['detail'] == "City not found"
