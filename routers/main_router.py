from routers.v1 import photo_router, person_router, auth_router, face_router, search_router
from routers.dependencies.auth_jwt import verify_jwt_token
from fastapi import APIRouter, Depends

secure_router = APIRouter(tags=["api_v1_secure"], dependencies=[Depends(verify_jwt_token)])
secure_router.include_router(person_router)
secure_router.include_router(photo_router)
secure_router.include_router(face_router)


router = APIRouter(prefix="/api/v1", tags=["api_v1"])
router.include_router(auth_router)
router.include_router(secure_router)
router.include_router(search_router)
