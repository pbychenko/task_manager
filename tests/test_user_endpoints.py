from httpx import AsyncClient


class TestRegister:
    async def test_register_returns_created_user(self, async_client: AsyncClient):
        response = await async_client.post(
            "/users/register/",
            json={"username": "bob", "password": "bobs-password"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["username"] == "bob"
        assert "id" in body
        assert "password" not in body

    async def test_register_duplicate_username_returns_conflict(
        self, async_client: AsyncClient, regular_user: dict
    ):
        response = await async_client.post(
            "/users/register/",
            json={"username": regular_user["username"], "password": "irrelevant"},
        )

        assert response.status_code == 409


class TestLogin:
    async def test_login_with_correct_credentials_returns_token(
        self, async_client: AsyncClient, regular_user: dict
    ):
        response = await async_client.post(
            "/users/login/",
            json={
                "username": regular_user["username"],
                "password": regular_user["password"],
            },
        )

        assert response.status_code == 200
        body = response.json()

        assert body["token_type"] == "bearer"
        assert body["access_token"]

    async def test_login_with_wrong_password_returns_unauthorized(
        self, async_client: AsyncClient, regular_user: dict
    ):
        response = await async_client.post(
            "/users/login/",
            json={
                "username": regular_user["username"],
                "password": "wrong-password",
            },
        )

        assert response.status_code == 401

    async def test_login_with_unknown_username_returns_unauthorized(
        self, async_client: AsyncClient
    ):
        response = await async_client.post(
            "/users/login/",
            json={"username": "ghost", "password": "whatever"},
        )

        assert response.json()["detail"] == "Invalid username or password"
        assert response.status_code == 401


class TestGetUser:
    async def test_get_user_without_token_is_unauthorized(
        self, async_client: AsyncClient, regular_user: dict
    ):
        response = await async_client.get(f"/users/{regular_user['id']}/")

        assert response.status_code == 401

    async def test_get_user_by_id_with_token_for_different_roles(
        self, async_client: AsyncClient, regular_user: dict, regular_user_headers: dict, manager_headers: dict
    ):
        response = await async_client.get(
            f"/users/{regular_user['id']}/", headers=regular_user_headers
        )
        
        assert response.json()["detail"] == "You do not have needed role permission"
        assert response.status_code == 403

        response = await async_client.get(
            f"/users/{regular_user['id']}/", headers=manager_headers
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == regular_user["username"]


    async def test_get_nonexistent_user_returns_not_found(
        self, async_client: AsyncClient, manager_headers: dict
    ):
        response = await async_client.get("/users/999999/", headers=manager_headers)

        assert response.json()["detail"] == "User with id=999999 not found"
        assert response.status_code == 404


    async def test_get_users_list_with_different_roles(
        self, async_client: AsyncClient, regular_user: dict, regular_user_headers: dict, manager_headers: dict
    ):
        response = await async_client.get("/users/", headers=regular_user_headers)
        body = response.json()
                
        assert body["detail"] == "You do not have needed role permission"
        assert response.status_code == 403

        response = await async_client.get("/users/", headers=manager_headers)
        assert response.status_code == 200

        usernames = [u["username"] for u in response.json()]
        assert regular_user["username"] in usernames

    async def test_only_admin_can_change_user_role(
        self, async_client: AsyncClient, admin_headers: dict, manager_headers: dict, regular_user: dict
        ):
        response = await async_client.patch(
            f"/users/{regular_user['id']}/role",
            json={"role": "manager"},
            headers=manager_headers,
        )

        assert response.json()["detail"] == "You do not have needed role permission"
        assert response.status_code == 403


        response = await async_client.patch(
            f"/users/{regular_user['id']}/role",
            json={"role": "manager"},
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json()["role"] == "manager"
