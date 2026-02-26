from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
async def get_users():
    return {"message": "List of users"}

@router.get("/{user_id}")
async def get_user(user_id: str):
    return {"message": f"User with ID {user_id}"}

# Note: The create_user enpoint does not exist, because of the authentication system. Users are created through the /auth/register endpoint.

@router.put("/{user_id}")
async def update_user(user_id: str):
    return {"message": f"User with ID {user_id} updated"}

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    return {"message": f"User with ID {user_id} deleted"}
