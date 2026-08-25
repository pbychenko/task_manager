
from httpx import AsyncClient

task_data = {"title": "new task", "description": "new_task_description"}

class TestTaskCreate:
    async def test_create_task(self, async_client: AsyncClient, task: dict):  
        assert task["title"] == task_data["title"]
        assert task["description"] == task_data["description"]
        assert task["completed"] is False
        assert task["creator_id"] is not None

    async def test_create_task_without_autorization(self, async_client: AsyncClient):
        response = await async_client.post(
            "/tasks/",
            json=task_data  
        )
        body = response.json()
    
        assert response.status_code == 401        
        assert body["detail"] == "Not authenticated"


class TestUpdateTask:
    async def test_update_task_positive_case(self, async_client: AsyncClient, auth_headers: dict, task: dict):
        new_task_data = {"title": "new task1", "description": "new_task_description1", "completed": True}
        task_id = task["id"]  

        response = await async_client.put(
            f"/tasks/{task_id}",
            json=new_task_data,
            headers=auth_headers
        )

        assert response.status_code == 200

        updated_task = response.json()
        assert updated_task["title"] == new_task_data["title"]
        assert updated_task["description"] == new_task_data["description"]
        assert updated_task["completed"] == True


    async def test_update_task_negative_cases(self, async_client: AsyncClient, auth_headers: dict, task: dict):
            new_task_data = {"title": "new task1", "description": "new_task_description1", "completed": True}
            task_id = task['id']
    
            # проверка редактирования несуществующей задачи
            response = await async_client.put(
                f"/tasks/{task_id + 1}",
                json=new_task_data,
                headers=auth_headers
            )
    
            assert response.status_code == 404
            assert response.json()["detail"] == f"Task {task_id + 1} not found"
    
            # проверка редактирования creator_id
            second_user = {"username": "test2", "password": "password2"}
            response = await async_client.post("/users/register/", json=second_user)
            second_user_id = response.json()["id"]
            response = await async_client.put(
                f"/tasks/{task_id}",
                json={"creator_id": second_user_id},
                headers=auth_headers
            )
        
            assert response.status_code == 422

            # проверка редактирования без авторизации
            response = await async_client.put(
                "/tasks/{task_id}",
                json=new_task_data
            )    

            assert response.status_code == 401        
            assert response.json()["detail"] == "Not authenticated"

class TestDeleteTask:
    async def test_delete_task_positive_case(self, async_client: AsyncClient, auth_headers: dict, task: dict):
        task_id = task['id']
        response = await async_client.delete(
            f"/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204


    async def test_delete_task_negative_cases(self, async_client: AsyncClient, auth_headers: dict, task: dict):
            task_id = task['id'] 
    
            # проверка удаления несуществующей задачи
            response = await async_client.delete(
                f"/tasks/{task_id + 1}",
                headers=auth_headers
            )
    
            assert response.status_code == 404
            assert response.json()["detail"] == f"Task {task_id + 1} not found"
    
            # проверка удаления задачи другим юзером
            second_user = {"username": "test2", "password": "password2"}
            response = await async_client.post("/users/register/", json=second_user)
            second_login = await async_client.post("/users/login/", json=second_user)
            second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
            response = await async_client.delete(
                f"/tasks/{task_id}",
                headers=second_headers
            )
        
            assert response.status_code == 403
            assert response.json()["detail"] == "You do not have permission to delete this task"

            # проверка удаления задачи без авторизации
            response = await async_client.delete(
                f"/tasks/{task_id}",
            )
    
            assert response.status_code == 401        
            assert response.json()["detail"] == "Not authenticated"


class TestGetTask:
    async def test_get_tasks_positive(self, async_client: AsyncClient, auth_headers: dict, task: dict):
        task_id_1 = task["id"]
        creator_id = task["creator_id"]

        new_task_data = {"title": "new task1", "description": "new_task_description1"}

        response = await async_client.post(
            "/tasks/",
            json=new_task_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200

        task_id_2 = response.json()["id"]
        response = await async_client.get(
            f"/tasks/",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()

        default_data = {'completed': False, 'creator_id': creator_id, 'executor_id': None}
        expected_tasks = [{'id': task_id_1, **task_data, **default_data}, {'id': task_id_2, **new_task_data, **default_data}]
                          
        assert tasks == expected_tasks

        response = await async_client.get(
            f"/tasks/{task_id_2}",
            headers=auth_headers
        )

        task = response.json()

        assert task == {'id': task_id_2, **new_task_data, **default_data}


    async def test_get_tasks_negative_cases(self, async_client: AsyncClient, auth_headers: dict, task: dict):
            task_id = task["id"] 
    
            # проверка посмотреть несуществующую задачу
            response = await async_client.get(
                f"/tasks/{task_id + 1}",
                headers=auth_headers
            )
    
            assert response.status_code == 404
            assert response.json()["detail"] == f"Task with id={task_id + 1} not found"
    
            
            # проверка посмотреть задачу без авторизации
            response = await async_client.get(
                f"/tasks/{task_id}",
            )
    
            assert response.status_code == 401        
            assert response.json()["detail"] == "Not authenticated"

            response = await async_client.get(
                f"/tasks/",
            )
    
            assert response.status_code == 401        
            assert response.json()["detail"] == "Not authenticated"