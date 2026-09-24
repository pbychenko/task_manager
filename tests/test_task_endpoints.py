from urllib import response

from httpx import AsyncClient


task_data = {"title": "new task", "description": "new_task_description"}

class TestTaskCreate:
    async def test_create_task(self, task: dict):
        assert task["title"] == task_data["title"]
        assert task["description"] == task_data["description"]
        assert task["status"] == "to_do"
        assert task["priority"] == "medium"
        assert task["creator_id"] is not None

    async def test_create_task_negative_cases(self, async_client: AsyncClient, regular_user_headers: dict, task: dict):
        # проверка создания задачи без авторизации
        response = await async_client.post("/tasks/", json={ **task_data, "project_id": task["project_id"] })
        body = response.json()

        assert response.status_code == 401
        assert body["detail"] == "Not authenticated"

        # проверка создания задачи обычным пользователем без роли "manager"
        response = await async_client.post("/tasks/", json={ **task_data, "project_id": task["project_id"] }, headers=regular_user_headers)

        assert response.json()["detail"] == "You do not have needed role permission"
        assert response.status_code == 403

    async def test_admin_can_create_task_in_manager_project(
        self,
        async_client: AsyncClient,
        admin_headers: dict,
        admin_user: dict,
        project: dict,
    ):
        response = await async_client.post(
            "/tasks/",
            json={**task_data, "project_id": project["id"]},
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json()["project_id"] == project["id"]
        assert response.json()["creator_id"] == admin_user["id"]

    async def test_manager_cannot_create_task_in_another_managers_project(
        self,
        async_client: AsyncClient,
        second_manager_headers: dict,
        project: dict,
    ):
        response = await async_client.post(
            "/tasks/",
            json={**task_data, "project_id": project["id"]},
            headers=second_manager_headers,
        )

        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You do not have permission to create a task in this project"
        )


class TestUpdateTask:
    async def test_update_task_positive_case(
        self, async_client: AsyncClient, manager_headers: dict, task: dict
    ):
        new_task_data = {
            "title": "new task1",
            "description": "new_task_description1",
            "priority": "high",
        }
        task_id = task["id"]

        response = await async_client.patch(
            f"/tasks/{task_id}", json=new_task_data, headers=manager_headers
        )

        assert response.status_code == 200

        updated_task = response.json()

        assert updated_task["title"] == new_task_data["title"]
        assert updated_task["description"] == new_task_data["description"]
        assert updated_task["priority"] == new_task_data["priority"]

    async def test_admin_can_update_task_in_manager_project(
        self,
        async_client: AsyncClient,
        admin_headers: dict,
        task: dict,
    ):
        new_task_data = {
            "title": "task updated by admin",
            "description": "admin can update tasks in manager projects",
            "priority": "high",
        }

        response = await async_client.patch(
            f"/tasks/{task['id']}",
            json=new_task_data,
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json()["title"] == new_task_data["title"]
        assert response.json()["description"] == new_task_data["description"]
        assert response.json()["priority"] == new_task_data["priority"]

    async def test_update_task_negative_cases(
        self, async_client: AsyncClient, manager_headers: dict, task: dict, second_manager_headers: dict
    ):
        new_task_data = {
            "title": "new task1",
            "description": "new_task_description1",
            "priority": "high",
        }
        task_id = task["id"]

        # проверка редактирования несуществующей задачи
        response = await async_client.patch(
            f"/tasks/{task_id + 1}", json=new_task_data, headers=manager_headers
        )

        assert response.status_code == 404
        assert response.json()["detail"] == f"Task {task_id + 1} not found"

        # проверка редактирования задачи другим менеджером
        response = await async_client.patch(
            f"/tasks/{task_id}", json=new_task_data, headers=second_manager_headers
        )

        assert response.json()["detail"] == "You do not have permission to update this task"
        assert response.status_code == 403

        # проверка редактирования без авторизации
        response = await async_client.patch(f"/tasks/{task_id}", json=new_task_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

class TestUpdateTaskStatus:
    async def test_update_task_status_by_manager(
        self, async_client: AsyncClient, manager_headers: dict, task: dict
    ):
        valid_status = {
            "status": "in_progress"
        }

        not_valid_status = {
            "status": "review"
        }

        task_id = task["id"]

        response = await async_client.patch(
            f"/tasks/{task_id}/status", json=not_valid_status, headers=manager_headers
        )

        assert response.status_code == 400
        assert response.json()["detail"] == f"Invalid status transition from {task['status']} to {not_valid_status['status']}"

        response = await async_client.patch(
            f"/tasks/{task_id}/status", json=valid_status, headers=manager_headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == valid_status["status"]

    async def test_admin_can_update_status_of_task_in_manager_project(
        self,
        async_client: AsyncClient,
        admin_headers: dict,
        task: dict,
    ):
        response = await async_client.patch(
            f"/tasks/{task['id']}/status",
            json={"status": "in_progress"},
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    async def test_update_task_status_by_regular_user(
            self, async_client: AsyncClient, manager_headers: dict, task: dict, regular_user_headers: dict, regular_user: dict
        ):
            valid_status = {
                "status": "in_progress"
            }
    
            task_id = task["id"]
    
            response = await async_client.patch(
                f"/tasks/{task_id}/status", json=valid_status, headers=regular_user_headers
            )
    
            assert response.status_code == 403
            assert response.json()["detail"] == "You do not have permission to update the status of this task"
    
            response = await async_client.patch(
                f"/tasks/{task_id}", json={"executor_id": regular_user["id"]}, headers=manager_headers
            )

            assert response.status_code == 200
            assert response.json()["executor_id"] == regular_user["id"]

            response = await async_client.patch(
                f"/tasks/{task_id}/status", json=valid_status, headers=regular_user_headers
            )
    
            assert response.status_code == 200
            assert response.json()["status"] == valid_status["status"]

    async def test_update_task_status_other_negative_cases(
        self, async_client: AsyncClient, manager_headers: dict, task: dict, second_manager_headers: dict
    ):
        valid_status = {
            "status": "in_progress"
        }
        task_id = task["id"]

        # проверка редактирования несуществующей задачи
        response = await async_client.patch(
            f"/tasks/{task_id + 1}/status", json=valid_status, headers=manager_headers
        )

        assert response.status_code == 404
        assert response.json()["detail"] == f"Task {task_id + 1} not found"

        # проверка редактирования задачи другим менеджером
        response = await async_client.patch(
            f"/tasks/{task_id}/status", json=valid_status, headers=second_manager_headers
        )

        assert response.json()["detail"] == "You do not have permission to update the status of this task"
        assert response.status_code == 403

        # проверка редактирования без авторизации
        response = await async_client.patch(f"/tasks/{task_id}/status", json=valid_status)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


class TestDeleteTask:
    async def test_delete_task_positive_case(
        self, async_client: AsyncClient, manager_headers: dict, task: dict
    ):
        task_id = task["id"]
        response = await async_client.delete(f"/tasks/{task_id}", headers=manager_headers)

        assert response.status_code == 204

    async def test_admin_can_delete_task_in_manager_project(
        self,
        async_client: AsyncClient,
        admin_headers: dict,
        task: dict,
    ):
        response = await async_client.delete(
            f"/tasks/{task['id']}",
            headers=admin_headers,
        )

        assert response.status_code == 204

    async def test_delete_task_negative_cases(
        self, async_client: AsyncClient, manager_headers: dict, task: dict, second_manager_headers: dict
    ):
        task_id = task["id"]

        # проверка удаления несуществующей задачи
        response = await async_client.delete(
            f"/tasks/{task_id + 1}", headers=manager_headers
        )

        assert response.status_code == 404
        assert response.json()["detail"] == f"Task {task_id + 1} not found"

        # проверка удаления задачи другим юзером
        response = await async_client.delete(
            f"/tasks/{task_id}", headers=second_manager_headers
        )

        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You do not have permission to delete this task"
        )

        # проверка удаления задачи без авторизации
        response = await async_client.delete(
            f"/tasks/{task_id}",
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


class TestGetTask:
    async def test_get_tasks_positive(
        self, async_client: AsyncClient, regular_user_headers: dict, task: dict, manager_headers: dict
    ):
        task_id = task["id"]
        creator_id = task["creator_id"]
        new_task_data = {"title": "new task1", "description": "new_task_description1"}

        response = await async_client.post(
            "/tasks/", json={ **new_task_data, "project_id": task["project_id"] }, headers=manager_headers
        )

        assert response.status_code == 200

        
        new_task_id = response.json()["id"]
        response = await async_client.get("/tasks/", headers=regular_user_headers)

        assert response.status_code == 200

        tasks = response.json()
        default_data = {
            "priority": "medium",
            "creator_id": creator_id,
            "executor_id": None,
            "status": "to_do",
            "project_id": task["project_id"]
        }
        expected_tasks = [
            {"id": task_id, **task_data, **default_data},
            {"id": new_task_id, **new_task_data, **default_data},
        ]

        assert sorted(tasks, key=lambda item: item["id"]) == sorted(
            expected_tasks,
            key=lambda item: item["id"]
        )

        response = await async_client.get(f"/tasks/{new_task_id}", headers=regular_user_headers)
        new_task = response.json()

        assert new_task == {"id": new_task_id, **new_task_data, **default_data}

    async def test_get_tasks_negative_cases(
        self, async_client: AsyncClient, regular_user_headers: dict, task: dict
    ):
        task_id = task["id"]

        # проверка посмотреть несуществующую задачу
        response = await async_client.get(f"/tasks/{task_id + 1}", headers=regular_user_headers)

        assert response.status_code == 404
        assert response.json()["detail"] == f"Task with id={task_id + 1} not found"

        # проверка посмотреть задачу без авторизации
        response = await async_client.get(
            f"/tasks/{task_id}",
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

        response = await async_client.get(
            "/tasks/",
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
