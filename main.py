import structlog
from fastapi import FastAPI

from heurekaopc.offers_processing import process_offer

log = structlog.get_logger()


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}



if __name__ == "__main__":

    offer = {
        "id": "ed87340d-3703-45b1-a7f8-5fa7d22fc9e9",
        "category": "Books",
        "name": "Harry Potter és a bölcsek köve (2016)",
        "description": 'A "Harry Potter és a bölcsek köve" c. könyvről részletesen:\nHarry Potter tizenegy éves, amikor megtudja, hogy ő bizony varázslónak született, és felvételt nyert a Roxfort Boszorkány- és Varázslóképző Szakiskolába.',
        "parameters": {
            "number of pages": "336",
            "weight": "380",
            "publisher": "Fizika",
        },
    }


    process_offer(offer)

    log.info("done")