import asyncio

import structlog
from fastapi import FastAPI

from heurekaopc.kafka import read_kafka_messages
from heurekaopc.offer_api import offer_matches
from heurekaopc.offers_processing import process_message

log = structlog.get_logger()


app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.on_event("startup")
async def startup_events():
    asyncio.create_task(read_kafka_messages(process_message))


@app.on_event("shutdown")
def shutdown_events():
    pass


if __name__ == "__main__":
    print(offer_matches("631aa5a8-9b5d-4ae2-945a-00a0a539b101")["matching_offers"])
