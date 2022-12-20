from fastapi import APIRouter

from heurekaopc.model import mongo_client

router = APIRouter()


@router.get("/", response_description="Get the ids of the products.")
async def list_products():
    with mongo_client() as db:
        return list(db.products.find())
