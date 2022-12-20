import asyncio

import structlog
from bson import ObjectId
from fastapi import FastAPI
from pydantic.json import ENCODERS_BY_TYPE

from heurekaopc.kafka import read_kafka_messages
from heurekaopc.offer_routes import router as offer_router
from heurekaopc.offers_processing import process_message
from heurekaopc.product_routes import router as product_router

log = structlog.get_logger()


app = FastAPI()

# encoding ObjectId in responses from API
ENCODERS_BY_TYPE[ObjectId] = str


@app.on_event("startup")
async def startup_events():
    asyncio.create_task(read_kafka_messages(msg_processor=process_message))
    pass


app.include_router(offer_router, tags=["offers"], prefix="/offer")
app.include_router(product_router, tags=["products"], prefix="/product")
