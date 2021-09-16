from config import ebay_auth
from ebaysdk.finding import Connection
import requests
import urllib.request as request
from urllib.request import Request
import urllib.parse
import xmltodict
import json

def search_ebay(keywords, filters, page):
    category_id = filters['categoryId']
    location = filters['location']
    # Build item_filters list
    item_filters = []
    if filters['min_price'] != '' :
        item_filters.append(
            {
                'name': 'minPrice',
                'value': int(filters['min_price'])
            }
        )
    if filters['max_price'] != '':
        item_filters.append(
            {
                'name': 'maxPrice',
                'value': int(filters['max_price'])
            }
        )
    # Build request data
    request = {}
    request['keywords'] = keywords
    if item_filters != []:
        request['item_filters'] = item_filters
    if category_id != '':
        request['categoryId'] = category_id

    request['paginationInput'] = {
            'entriesPerPage': 1000,
            # 'pageNumber': page
        }
    # if location != '':
    #     siteid = location
    # else:
    siteid = "EBAY-US"
    api = Connection(domain='svcs.sandbox.ebay.com', config_file='ebay.yaml', siteid=siteid)

    print(request)
    response = api.execute('findItemsAdvanced', request)
    results = response.reply.searchResult
    print('count' +results._count)
    totalItems = int(results._count)
    if totalItems == 0:
        return [], 0

    else:
        search_results = []
        for item in results.item:
            item_object = {}
            item_object['product_store'] = 'ebay'
            item_object['product_name'] = item.title
            item_object['product_id'] = item.itemId
            item_object['product_link'] = item.viewItemURL 
            item_object['product_currency'] = item.sellingStatus.currentPrice._currencyId
            item_object['product_price'] =  item.sellingStatus.currentPrice.value
            try:
                item_object['product_image'] = item.galleryURL
            except Exception:
                item_object['product_image'] = ''
            search_results.append(item_object)
        return search_results, totalItems

def search_product(product_id):
    print('Inside getItem to update product price')
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
            <GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                <ItemID>{product_id}</ItemID>
                <RequesterCredentials>
                    <eBayAuthToken>{ebay_auth['token']}</eBayAuthToken>
                </RequesterCredentials>
            </GetItemRequest>"""
    # Ebay-us site_id
    siteid = '0'

    url = 'https://api.sandbox.ebay.com/ws/api.dll'
    req = Request(url)
    req.add_header('Content-Type', 'application/xml')
    req.add_header('X-EBAY-API-COMPATIBILITY-LEVEL','1201')
    req.add_header('X-EBAY-API-DEV-NAME', ebay_auth['devid'])
    req.add_header('X-EBAY-API-APP-NAME', ebay_auth['appid'])
    req.add_header('X-EBAY-API-CERT-NAME', ebay_auth['certid'])
    req.add_header('X-EBAY-API-SITEID', siteid)
    req.add_header('X-EBAY-API-CALL-NAME', 'GetItem')

    response = request.urlopen(req, data=xml.encode('utf-8'))
    content = response.read().decode('utf-8')
    response_json = json.loads(json.dumps(xmltodict.parse(content)))
    if response_json['GetItemResponse']['Ack'] == 'Failure':
        print('COULDN\'T UPDATE PRODUCT')
        return 'not found'
    else:
        current_price = response_json['GetItemResponse']['Item']['SellingStatus']['CurrentPrice']['#text']
        return float(current_price)

    # totalItems = int(results._count)
# request categories:
# $ curl http://open.api.ebay.com/Shopping?callname=GetCategoryInfo&appid=Khadidja-pricetra-SBX-f3633a1dd-428cb13a&callbackname=cb_listCategorie
# s&siteid=0&CategoryID=-1&version=729&IncludeSelector=ChildCategories&responseencoding=JSON

