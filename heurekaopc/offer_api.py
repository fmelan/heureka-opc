import json

import httpx
import structlog

from settings import settings

log = structlog.get_logger()


def offer_matches(offer_id: str) -> [str]:
    """
    :param offer_id: id of the offer
    :return: The list of offer ids which are matching together.
    """
    log.info(f"Getting matching offers for {offer_id}")
    r = httpx.get(
        f"{settings.offer_api}/offer-matches/{offer_id}",
        headers={"Auth": settings.offer_api_token},
    )
    log.info(f"Response: {r.text}")

    if r.status_code > 202:
        if r.status_code == 404:
            return []
        else:
            msg = f"Got non 200(OK) HTTP response from API: {r.status_code}."
            log.error(msg)
            raise Exception(msg)

    return json.loads(r.content.decode("utf-8"))["matching_offers"]
