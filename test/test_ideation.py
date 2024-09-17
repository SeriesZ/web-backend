import pytest
from httpx import AsyncClient

from conftest import client, create_user_and_get_auth_token


@pytest.mark.anyio
class TestIdeation:
    ideation = {
        "title": "Test Ideation",
        "content": "This is a test idea",
        "image": "http://example.com/image.jpg",
        "theme": "BioIndustry",
        "presentation_date": "2024-01-01T00:00:00",
        "close_date": "2024-01-31T00:00:00",
    }

    async def test_create_ideation(self, client: AsyncClient):
        headers = await create_user_and_get_auth_token(client)

        # 아이디어 생성
        response = await client.post("/ideations", json=self.ideation, headers=headers)

        assert response.status_code == 200
        assert response.json()["title"] == self.ideation["title"]
        assert response.json()["close_date"] == self.ideation["close_date"]

    async def test_get_ideation(self, client: AsyncClient):
        headers = await create_user_and_get_auth_token(client)

        # 아이디어 생성
        create_response = await client.post("/ideations", json=self.ideation, headers=headers)
        ideation_id = create_response.json()["id"]

        # 아이디어 조회
        response = await client.get(f"/ideations/{ideation_id}", headers=headers)

        assert response.status_code == 200
        assert response.json()["title"] == self.ideation["title"]

        # 아이디어 다시 조회 (view_count 증가 확인)
        headers = await create_user_and_get_auth_token(client, email="test2@test.com", password="password")
        response = await client.get(f"/ideations/{ideation_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["view_count"] == 1

        response = await client.get(f"/ideations/{ideation_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["view_count"] == 2

    async def test_update_ideation(self, client: AsyncClient):
        headers = await create_user_and_get_auth_token(client)

        # 아이디어 생성 (테스트를 위한)
        create_response = await client.post("/ideations", json=self.ideation, headers=headers)
        ideation_id = create_response.json()["id"]

        # 업데이트 시에는 전체 필드에서 변경된 필드 바꿔서 요청
        updated_ideation = self.ideation.copy()
        updated_ideation["title"] = "Updated Test Idea"
        updated_ideation["content"] = "Updated content."

        # 아이디어 업데이트
        response = await client.put(f"/ideations/{ideation_id}", json=updated_ideation, headers=headers)

        assert response.status_code == 200
        assert response.json()["title"] == updated_ideation["title"]
        assert response.json()["content"] == updated_ideation["content"]

    async def test_delete_ideation(self, client: AsyncClient):
        headers = await create_user_and_get_auth_token(client)

        # 아이디어 생성
        create_response = await client.post("/ideations", json=self.ideation, headers=headers)
        ideation_id = create_response.json()["id"]

        # 아이디어 삭제
        response = await client.delete(f"/ideations/{ideation_id}", headers=headers)

        assert response.status_code == 204

        response = await client.get(f"/ideations/{ideation_id}", headers=headers)

        assert response.status_code == 404
