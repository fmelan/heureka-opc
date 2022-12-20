from fastapi import APIRouter

from heurekaopc.model import mongo_client
from heurekaopc.offers_processing import compare_offers

router = APIRouter()


@router.get("/{product_id}", response_description="Get offers by product id.")
async def list_offers_by_product(product_id: str):
    with mongo_client() as db:
        return list(db.offers.find({"product_id": product_id}))


@router.get("/", response_description="Get all offers data.")
async def list_all_offers():
    with mongo_client() as db:
        return list(db.offers.find())


@router.get(
    "/compare/{offer_1_id}/{offer_2_id}",
    response_description="Return the number of common and different parameters of two offers.",
)
async def compare_parameters(offer_1_id: str, offer_2_id: str):
    return compare_offers(offer_1_id, offer_2_id)
