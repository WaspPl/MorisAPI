from fastapi import APIRouter

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("")
async def get_roles():
    return {"message": "List of roles"}
@router.get("/{role_id}")

async def get_role(role_id: str):
    return {"message": f"Role with ID {role_id}"}

@router.post("")
async def create_role():
    return {"message": "Role created"}

@router.put("/{role_id}")
async def update_role(role_id: str):
    return {"message": f"Role with ID {role_id} updated"}

@router.delete("/{role_id}")
async def delete_role(role_id: str):
    return {"message": f"Role with ID {role_id} deleted"}
