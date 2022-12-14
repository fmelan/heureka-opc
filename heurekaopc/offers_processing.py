from heurekaopc.model import (
    db,
)
from heurekaopc.offer_api import offer_matches


def find_linked_product(offer_ids: list) -> (int, list):
    """
    Searches database for product linked to any of the offers with provided
    offer_ids. We don't know if the offers are stored in database. This
    function will find out.
    :param: offer_ids: offer ids
    :return: tuple: (product_id or None, list of ids of offers stored in
    database and linked to the product)
    """
    product_id = None
    offers_linked = []

    offers = db.offers.find({"id": {"$in": offer_ids}, "product_id": {"$exists": True}})

    loffers = list(offers)
    if loffers:
        product_id = loffers[0]["product_id"]
        offers_linked = [o["id"] for o in loffers]

    return product_id, offers_linked


def set_product_to_offer(product_id: int, offer_ids):
    """
    Sets the product_id to offers. Check first that offers exists
    in database, if not, then create them.
    :param: product_id:
    :param: offer_ids: collection of offer ids
    :return:
    """
    stored_offers = list(db.offers.find({"id": {"$in": offer_ids}}))
    # update existing
    if stored_offers:
        db.offers.update_many(
            {"id": {"$in": [x["id"] for x in stored_offers]}},
            {"$set": {"product_id": product_id}},
        )
    # create new
    for new_offer_id in set(offer_ids) - set(o["id"] for o in stored_offers):
        db.offers.insert_one({"id": new_offer_id, "product_id": product_id})


def process_matching_offers(offer_id):
    matching = offer_matches(offer_id)
    if matching:
        product_id, offer_ids = find_linked_product(matching)
        if product_id:
            # set the link where is missing
            set_product_to_offer(product_id, list(set(matching) - set(offer_ids)))
        else:
            product_id = str(db.products.insert_one({}).inserted_id)
            set_product_to_offer(product_id, matching)
        # finally, set product_id to processed offer
        set_product_to_offer(product_id, [offer_id])


def process_offer(offer_data: dict):
    """
    Processing of offer_data data. Stores data in database. Checks matching
    offers. Creates new products if offers are matching.
    param offer_data: offer_data data
    :return:
    """
    offer = db.offers.find_one({"id": offer_data["id"]})
    if offer:
        # offer_data stored, update data
        db.offers.update_one({"id": offer["id"]}, {"$set": offer_data})
        offer_id = offer["id"]
    else:
        # new offer
        db.offers.insert_one(offer_data)
        offer_id = offer_data["id"]
        # process matching offers
    process_matching_offers(offer_id)