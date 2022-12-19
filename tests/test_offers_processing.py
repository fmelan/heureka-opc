from pytest_mock import mocker

from heurekaopc import offers_processing
from heurekaopc.offers_processing import find_linked_product, set_product_to_offer, process_offer


def test_find_linked_product(mongodb):
    # TODO setup, teardown
    offers_processing.db = mongodb

    assert "offers" in mongodb.list_collection_names()

    # no found product

    product_id, offer_ids = find_linked_product([])
    assert product_id is None
    assert len(offer_ids) == 0

    product_id, offer_ids = find_linked_product(
        ["nonexistent1", "nonexistent2", "nonexistent3"]
    )
    assert product_id is None
    assert len(offer_ids) == 0

    # found product, one offer has the product_id
    product_id, offer_ids = find_linked_product(
        ["ed87340d-3703-45b1-a7f8-5fa7d22fc9e9", "631aa5a8-9b5d-4ae2-945a-00a0a539b101"]
    )
    assert product_id == "prod1"
    assert offer_ids == ["ed87340d-3703-45b1-a7f8-5fa7d22fc9e9"]

    # found id but no product_id
    product_id, offer_ids = find_linked_product(
        ["38495bd1-afe9-4cd0-bf9d-eca162e75542"]
    )
    assert product_id is None
    assert len(offer_ids) == 0


def test_set_product_to_offer(mongodb):
    # TODO setup, teardown
    offers_processing.db = mongodb

    # two existing offers, one should be created
    offer_ids = [
        "631aa5a8-9b5d-4ae2-945a-00a0a539b101",
        "38495bd1-afe9-4cd0-bf9d-eca162e75542",
        "new-offer-id-2123154989",
    ]

    set_product_to_offer("prod2", offer_ids)

    o1 = mongodb.offers.find_one({"id": "631aa5a8-9b5d-4ae2-945a-00a0a539b101"})
    assert o1
    assert o1["product_id"] == "prod2"

    o2 = mongodb.offers.find_one({"id": "38495bd1-afe9-4cd0-bf9d-eca162e75542"})
    assert o2
    assert o2["product_id"] == "prod2"

    o3 = mongodb.offers.find_one({"id": "new-offer-id-2123154989"})
    assert o3
    assert o3["product_id"] == "prod2"

    assert len(list(mongodb.offers.find({"product_id": "prod2"}))) == 3


def test_process_offer(mongodb, mocker):
    # TODO setup, teardown
    offers_processing.db = mongodb

    # add one new offer without product link
    mocker.patch("heurekaopc.offers_processing.offer_matches", return_value=[])
    process_offer({'id': '0a10d511-6a65-444d-9628-3c6993ba7dbd', 'category': 'Tabletop games', 'name': 'Ravensburger Minecraft', 'description': 'Tuto strategickou stolní hru určenou nejen pro všechny fanoušky Minecraftu mohou hrát dva až čtyři hráči ve věku od 10 let. Balení hry obsahuje 64 dřevěných bloků, 64 stavebních karet a karet s příšerami, 36 kartiček se zbraněmi, 4 herní plány, 4 herní žetony, 4 hráčské skiny, 4 stojánky na figurky, 12 přehledových karet, 1 podložku pod bloky, 1 konstrukční oporu a návod.', 'parameters': {'genre': 'strategic', 'publisher': 'Ravensburger', 'age_from': '10', 'number_of_players': '2-4', 'year': '2019', 'game_length': '30m'}})
    # offer exists
    offer = mongodb.offers.find_one({"id": "0a10d511-6a65-444d-9628-3c6993ba7dbd"})
    assert offer
    assert offer["id"] == "0a10d511-6a65-444d-9628-3c6993ba7dbd"
    assert len(list(mongodb.offers.find({}))) == 4

    # add one new offer which will be linked to 3 other offers, existing product
    # API returns the offer itself as well

    # set product for 0a10d511-6a65-444d-9628-3c6993ba7dbd
    mongodb.offers.update_one(
        {"id": "0a10d511-6a65-444d-9628-3c6993ba7dbd"},
        {"$set": {"product_id": "prod2"}}
    )

    mocker.patch("heurekaopc.offers_processing.offer_matches", return_value=[
        "38495bd1-afe9-4cd0-bf9d-eca162e75542", # existing before
        "0a10d511-6a65-444d-9628-3c6993ba7dbd", # added recently
        "feaa400a-d304-4f55-b045-51b1daec8e0c", # will be added by process_offer
        "29e0b669-a670-476b-808a-e21a449d1c0f"  # linked but not existent in database
    ])
    process_offer({'id': 'feaa400a-d304-4f55-b045-51b1daec8e0c', 'category': 'LEGO', 'name': 'LEGO Harry Potter - Roxfort (71043)', 'description': 'Üdvözlünk az egyedülálló LEGO® Harry Potter™ 71043 Roxfort kastélyban! Építsd meg és állítsd ki ezt a részletesen kidolgozott mini LEGO® Harry Potter TM Roxfort kastély modellt, mely több mint 6000 elemből áll! Fedezd fel a rendkívül részletesen kidolgozott kamrákat, tornyokat és tantermeket, valamint számos rejtett funkciót és a Harry Potter filmek jeleneteit is! Népesítsd be a kastélyt 27 mikrofigurával, melyek között Harry, Hermione és Ron figurája is szerepel, továbbá rengeteg jellegzetes kiegészítő és tárgy lenyűgöző választéka is vár rád! A varázslatos építési élményt pedig kiegészítheted Hagrid kunyhójával és a Fúriafűzzel.\n\n\n\nÍgy is ismerheti: Harry Potter Roxfort 71043, HarryPotterRoxfort71043, Harry Potter Roxfort (71043), HarryPotter-Roxfort71043, Harry Potter - Roxfort ( 71043)', 'parameters': {'minimum age': 16, 'set': 'Harry Potter', 'number of pieces': 6020}})

    # existing before - now updated product_id
    offer384 = mongodb.offers.find_one({"id": "38495bd1-afe9-4cd0-bf9d-eca162e75542"})
    assert offer384
    assert offer384["product_id"] == "prod2"
    # added recently
    offeroa1 = mongodb.offers.find_one({"id": "0a10d511-6a65-444d-9628-3c6993ba7dbd"})
    assert offeroa1
    assert offeroa1["product_id"] == "prod2"

    # the processed offer - check that it is created with all data
    offerfeaa = mongodb.offers.find_one({"id": "feaa400a-d304-4f55-b045-51b1daec8e0c"})
    assert offerfeaa
    assert offerfeaa["product_id"] == "prod2"
    assert offerfeaa["name"] == 'LEGO Harry Potter - Roxfort (71043)'

    # the new linked offer - check that it is created - only id of product
    offer29e0 = mongodb.offers.find_one({"id": "29e0b669-a670-476b-808a-e21a449d1c0f"})
    assert offer29e0
    assert offer29e0["product_id"] == "prod2"
    assert "name" not in offer29e0

    # check that no other data were harmed - check count, different product_id
    assert len(list(mongodb.offers.find())) == 6
    offered87 = mongodb.offers.find_one({"id": "ed87340d-3703-45b1-a7f8-5fa7d22fc9e9"})
    assert offered87
    assert offered87["product_id"] == "prod1"

    # process the offer 29e0b669-a670-476b-808a-e21a449d1c0f
    # check data update
    # correctly - API should return matches but we are testing only data update
    mocker.patch("heurekaopc.offers_processing.offer_matches", return_value=[])
    process_offer({'id': '29e0b669-a670-476b-808a-e21a449d1c0f', 'category': 'Books', 'name': 'Harry Potter a Kámen mudrců - J. K. Rowlingová', 'description': 'Harryho Pottera Vám zajisté nemusím představovat, neboť je to taková knižní legenda a téměř už i klasika. Pro mnoho z Vás je to dokonce kniha, na které jste vyrostli.\n\nKdyž byl Harrymu jeden rok, tak přišel o své rodiče. Ten - o kom se nemluví - zavraždil Harryho rodiče a chtěl zabít i jeho samotného, jenže nějakým zázrakem chlapec přežil a na čele mu zůstala jizva v podobě blesku. Chlapec deset let vyrůstal u strýce a tety Dursleyových a jejich syna Dudleyho. Bylo by pravdě podobné, že když se jedná o přímé příbuzné, že bude o chlapce postaráno dobře, ale Harry doslova trpěl a je div, že z něho vyrostl bystrý a hodný chlapec.\n\nNezná svou minulost, nezná své rodiče, bylo mu jen řečeno, že zemřeli při nehodě. Neví z jaké rodiny pochází a ani neví, co mu bylo dáno do vínku. Ví, že je jiný, že se občas stanou zvláštní věci, ale ani ve snu by ho nenapadlo, že v den svých jedenáctých narozenin zjistí pravdu, která mu navždy změní život. A i přesto, že se teta se strýcem snaží všemožně zabránit tomu, aby se Harry dozvěděl skutečnost o sobě i svých rodičích, se jednoho dne objeví sova se zvláštním dopisem z Bradavic - ze školy čar a kouzel, jejímž ředitelem je Albus Brumbál.\n\nK příběhu asi netřeba více dodávat, kdo by jej neznal? Věřím, že není nikdo, i třeba těch, kteří knihy nečetli a kdo by nevěděl kdo je Harry Potter. Víte, že letos je to dvacet let od vydání první knihy od skvělé autorky J.K. Rowling?', 'parameters': {'author': 'J.K. Rowling', 'genre': 'for children', 'publisher': 'Albatros', 'number of pages': '336', 'year': '2017', 'language': 'czech'}})

    # still same count of offers
    assert len(list(mongodb.offers.find())) == 6
    offer29e0 = mongodb.offers.find_one({"id": "29e0b669-a670-476b-808a-e21a449d1c0f"})
    assert offer29e0["name"] == 'Harry Potter a Kámen mudrců - J. K. Rowlingová'

    # new product creation - should add 2 offers with new product_id
    mocker.patch("heurekaopc.offers_processing.offer_matches", return_value=[
        "94fe7882-dd86-424f-b487-706b174d8d4e",
        "id123456"
    ])
    process_offer({'id': '94fe7882-dd86-424f-b487-706b174d8d4e', 'category': 'Books', 'name': 'Harry Potter a Fénixův řád - Rowlingová Joanne Kathleen', 'description': 'Albatros Harry Potter a Fénixův řád (2017)\n\nČeká na tebe napínavé čtení o kouzelníkovi Harry Potterovi, který bojuje se zlem a proti tomu o kom se nesmí mluvit. Po jeho boku, ale stojí přátelé Ron Weasley a Hermiona Grangerová, kteří mu zásadně pomáhají.\n\nDo Bradavic přišly temné časy. Po útoku mozkomorů na bratrance Dudleyho Harry ví, že Voldemort udělá cokoli, jen aby ho našel. Mnozí jeho návrat popírají, ale Harry přesto není sám: na Grimmauldově náměstí se schází tajný řád, který chce bojovat proti temným silám. Harry se musí od profesora Snapea naučit, jak se chránit před Voldemortovými útoky na jeho duši. Jenže Pán zla je den ode dne silnější a Harrymu dochází čas…\nAutor: J. K. Rowlingová\nPřeklad: Vladimír Medek\nVěk: 9+\nPočet stran: 800\nJazyk: čeština\nRozměry: 14 x 20,5 cm\nZemě původu: ČR', 'parameters': {'author': 'J.K. Rowling', 'genre': 'for children', 'publisher': 'Albatros', 'number of pages': '800', 'year': '2018', 'language': 'czech'}})

    offer123456 = mongodb.offers.find_one({"id": "id123456"})
    assert offer123456
    product_id = offer123456["product_id"]
    assert product_id
    assert product_id not in ["prod1", "prod2"]

    offer94fe = mongodb.offers.find_one({"id": "94fe7882-dd86-424f-b487-706b174d8d4e"})
    assert offer94fe
    assert offer94fe["product_id"] == product_id

    assert len(list(mongodb.offers.find())) == 8
