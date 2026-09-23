from httpx import AsyncClient


project_data = {"name": "new project", "description": "new_project_description"}

class TestProjectCreate:
    async def test_create_project(self, project: dict):
        assert project["name"] == project_data["name"]
        assert project["description"] == project_data["description"]
        assert project["owner_id"] is not None


    async def test_create_project_without_autorization_and_with_incorrect_role(self, async_client: AsyncClient, regular_user_headers: dict):
        response = await async_client.post("/projects/", json=project_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        response = await async_client.post("/projects/", json=project_data, headers=regular_user_headers)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have needed role permission"


class TestUpdateProject:
    async def test_update_project_positive_case(
        self, async_client: AsyncClient, manager_headers: dict, project: dict
    ):
        new_project_data = {
            "name": "new project1",
            "description": "new_project_description1",
        }
        project_id = project["id"]

        response = await async_client.patch(
            f"/projects/{project_id}", json=new_project_data, headers=manager_headers
        )

        assert response.status_code == 200

        updated_project = response.json()

        assert updated_project["name"] == new_project_data["name"]
        assert updated_project["description"] == new_project_data["description"]

    async def test_update_project_negative_cases(
        self, async_client: AsyncClient, manager_headers: dict, project: dict, second_manager_headers:dict
    ):
        new_project_data = {
            "name": "new project1",
            "description": "new_project_description1"
        }
        project_id = project["id"]

        # проверка редактирования несуществующего проекта
        response = await async_client.patch(
            f"/projects/{project_id + 1}", json=new_project_data, headers=manager_headers
        )

        assert response.status_code == 404
        assert response.json()["detail"] == f"Project {project_id + 1} not found"

        new_project_data2 = {
            "name": "new project2",
            "description": "new_project_description2"
        }

        response = await async_client.patch(
            f"/projects/{project_id}",
            json=new_project_data2,
            headers=second_manager_headers,
        )

        assert response.json()["detail"] == "You do not have permission to update this project"
        assert response.status_code == 403
        

        # проверка редактирования без авторизации
        response = await async_client.patch(f"/projects/{project_id}", json=new_project_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


class TestDeleteProject:
    async def test_delete_project_positive_case(
        self, async_client: AsyncClient, manager_headers: dict, project: dict
    ):
        project_id = project["id"]
        response = await async_client.delete(f"/projects/{project_id}", headers=manager_headers)

        assert response.status_code == 204

    async def test_delete_project_negative_cases(
        self, async_client: AsyncClient, manager_headers: dict, project: dict, second_manager_headers:dict
    ):
        project_id = project["id"]

        # проверка удаления несуществующего проекта
        response = await async_client.delete(
            f"/projects/{project_id + 1}", headers=manager_headers
        )

        assert response.status_code == 404
        assert response.json()["detail"] == f"Project {project_id + 1} not found"

        # проверка удаления проекта другим менеджером
        response = await async_client.delete(
            f"/projects/{project_id}", headers=second_manager_headers
        )

        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You do not have permission to delete this project"
        )

        # проверка удаления проекта без авторизации
        response = await async_client.delete(
            f"/projects/{project_id}",
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


class TestGetProject:
    async def test_get_projects_positive(
        self, async_client: AsyncClient, manager_headers: dict, project: dict
    ):
        project_id_1 = project["id"]
        owner_id = project["owner_id"]
        new_project_data = {"name": "new project1", "description": "new_project_description1"}

        response = await async_client.post(
            "/projects/", json=new_project_data, headers=manager_headers
        )

        assert response.status_code == 200

        project_id_2 = response.json()["id"]
        response = await async_client.get("/projects/", headers=manager_headers)

        assert response.status_code == 200

        projects = response.json()
        default_data = {
            "owner_id": owner_id
        }
        expected_projects = [
            {"id": project_id_1, **project_data, **default_data},
            {"id": project_id_2, **new_project_data, **default_data},
        ]

        assert sorted(projects, key=lambda item: item["id"]) == sorted(
            expected_projects,
            key=lambda item: item["id"]
        )

        response = await async_client.get(f"/projects/{project_id_2}", headers=manager_headers)
        project = response.json()

        assert project == {"id": project_id_2, **new_project_data, **default_data}

    async def test_get_projects_negative_cases(
        self, async_client: AsyncClient, manager_headers: dict, project: dict, regular_user_headers: dict
    ):
        project_id = project["id"]

        # проверка посмотреть несуществующий проект
        response = await async_client.get(f"/projects/{project_id + 1}", headers=manager_headers)

        assert response.status_code == 404
        assert response.json()["detail"] == f"Project with id={project_id + 1} not found"

        # проверка посмотреть проект без авторизации
        response = await async_client.get(
            f"/projects/{project_id}",
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        response = await async_client.get(
            "/projects/",
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        # проверка посмотреть проекты пользователем с некорректной ролью
        response = await async_client.get(
            f"/projects/", headers=regular_user_headers)

        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have needed role permission"
