from heurekaopc.model import mongo_client
from heurekaopc.offer_matching_api import offer_matches


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

    with mongo_client() as db:
        offers = db.offers.find(
            {"id": {"$in": offer_ids}, "product_id": {"$exists": True}}
        )

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
    with mongo_client() as db:
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
            with mongo_client() as db:
                product_id = str(db.products.insert_one({}).inserted_id)
            set_product_to_offer(product_id, matching)
        # finally, set product_id to processed offer
        set_product_to_offer(product_id, [offer_id])


def process_message(offer_data: dict):
    """
    Processing of offer_data data. Stores data in database. Checks matching
    offers. Creates new products if offers are matching.
    param offer_data: offer_data data
    :return:
    """
    if "id" in offer_data:
        with mongo_client() as db:
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


def extract_params(params):
    """
    Returns a set of keys from the dict. If the value in dict
    is again dict, then it searches secursively.
    :param param: dict of params
    :return:
    """
    ret_val = set({})
    for key in params.keys():
        if isinstance(params[key], dict):
            ret_val = ret_val.union(extract_params(params[key]))
        else:
            ret_val.add(key)
    return ret_val


def compare_offer_parameters(offer_1: dict, offer_2: dict):
    """
    Compares two offers and returns the number of parameters they have in common
    and how many differ.
    :param offer_1:
    :param offer_2:
    :return: tuple (number of common parameters, number of parameters which differ)
    """
    params1 = extract_params(offer_1.get("parameters", {}))
    params2 = extract_params(offer_2.get("parameters", {}))

    return len(params1 & params2), len(params1.symmetric_difference(params2))


def compare_offers(offer_1_id: str, offer_2_id: str):
    with mongo_client() as db:
        return compare_offer_parameters(
            db.offers.find_one({"id": offer_1_id}),
            db.offers.find_one({"id": offer_2_id}),
        )
