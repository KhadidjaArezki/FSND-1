from os import environ

ebay_auth = {
    'token': 'AgAAAA**AQAAAA**aAAAAA**tARCYQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4aiDZaCqAWdj6x9nY+seQ**YakFAA**AAMAAA**2JrP0CUR9tOiRzuB7NUgF6SHxaHYQrhBd9zV+UpQJ05/Ed9lZZBcOqFg/4H1qLZD49m0WFqkv7gQP7nNuQSgV/bxGBEwu7Q1MF72nCPO3wLuGiWtky2LMF/Y5JtT/TlykDd3ZYVnh+bfqhSzH6NyTva77L9VyD2DxydPVSXxhbicwgjs66hv7U1Ccdy58IXYUTtfqtqUXpAuLfWrwQXt4EB/cUzvmQua7fqCuWgTy+xsDE6cJammOpJ+qDKXBvjfBcd8B+ylPHgj/+ZgLDdLX3tai3sBhUn9z7ZfCEvfNAasdU0tTXBBoH/Cd1fKBxOFN91mf2KJyX5Vi9RnDSgr2Th1v2GcddQiGfk7hpf05pBwxAIqQVaGZyNXRMURFsKVnraO4bQPDiqBhll5CxAangJGdt86jN8pmBice7uFXElosdm5u7R8wTh3lSV7jjL0rMXpl45NUl6tXlfWP2aVBzeHqus6vuhPSRa9vw1GCTSiIA1N+iffZp8xWIHhrMVRiuY18ZJqSxYW9UNvCrnJqbrHHkrWYv5FZrnqIPcDC5P4MOlvbGEA741XegKSG3t6dy43XNMu5HhMACguK1IHl7xz0IIwTFXrFYxd/dBXypTAEwijxpp6Lw6TSgtcfUxFi9VamRFQ/pVG+XzQh5WHP3AzHojBns64ddsrh3z/MaacTdGgovFU5a8+oCXx+8YTd+n3+O4Tev9ExGIQVVELg4u8Srpo1xL/tzOj1ZXa3ifAXLIApHeDrtYBwNZhlJVy',
    'appid': 'Khadidja-pricetra-SBX-f3633a1dd-428cb13a',
    'certid': 'SBX-3633a1dd0231-6ac0-42bb-aa93-72a3',
    'devid': '242e8a01-6fe5-4588-8ccb-7c4eb6e5618b'
}

# environ['database_owner'] = 'postgres'
# environ['database_password'] = '12345'
# environ['host'] = 'localhost:5432'
# environ['production_database_name'] = "capstone"
# environ['test_database_name'] = "capstone_test"
# environ['database_path'] = "postgresql://{}:{}@{}".format(
#                             environ['database_owner'],
#                             environ['database_password'],
#                             environ['host'])

environ['AUTH0_DOMAIN'] = 'fs-webdev.eu.auth0.com'
environ['ALGORITHMS'] = 'RS256'
environ ['API_AUDIENCE'] = 'coffeeshop'
