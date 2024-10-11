import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.config import test_data
from app.models.user import User


@pytest.mark.asyncio
async def test_user_creation(admin_user: User, async_session: AsyncSession) -> None:
    admin: User | None = await async_session.get(User, admin_user.id)
    assert admin is not None
    assert admin.email == admin_user.email
    assert admin.name == admin_user.name


# Get all users(admin and normal user) - success
@pytest.mark.asyncio
async def test_get_all_users(
    admin_user: User, normal_user: User, admin_token: str, client: AsyncClient
) -> None:
    response = await client.get(
        "/user",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == 2
    assert users[0]["email"] == admin_user.email
    assert users[0]["name"] == admin_user.name
    assert users[1]["email"] == normal_user.email
    assert users[1]["name"] == normal_user.name


# Get all users by normal user - not authorised
@pytest.mark.asyncio
async def test_get_all_users_not_authorised(
    normal_user: User, user_token: str, client: AsyncClient
) -> None:
    response = await client.get(
        "/user",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Admin access required"}


# Get user (admin) by id - success
@pytest.mark.asyncio
async def test_get_admin_by_id(admin_user: User, admin_token: str, client: AsyncClient) -> None:
    response = await client.get(
        f'/user/user/{test_data["initial_user"]["admin"]["id"]}',
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["email"] == admin_user.email
    assert user["name"] == admin_user.name


# Get user (normal) by id - success
@pytest.mark.asyncio
async def test_get_user_by_id(
    admin_user: User, normal_user: User, admin_token: str, client: AsyncClient
) -> None:
    response = await client.get(
        f'/user/user/{test_data["initial_user"]["user"]["id"]}',
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["email"] == normal_user.email
    assert user["name"] == normal_user.name


# Get user by id - not found
@pytest.mark.asyncio
async def test_get_user_by_id_not_found(admin_token: str, client: AsyncClient) -> None:
    response = await client.get(
        "/user/user/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


# Get user by id - not authorised
@pytest.mark.asyncio
async def test_get_user_by_id_not_authorised(user_token: str, client: AsyncClient) -> None:
    response = await client.get(
        f'/user/user/{test_data["initial_user"]["admin"]["id"]}',
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Admin access required"}


@pytest.mark.asyncio
async def test_create_user(
    admin_user: User, normal_user: User, admin_token: str, client: AsyncClient
) -> None:
    print(test_data["create_user"])
    response = await client.post(
        "/user/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_data["create_user"],
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user["email"] == test_data["create_user"]["email"]
    assert user["name"] == test_data["create_user"]["name"]
