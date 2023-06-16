import csv
import json
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsPositionBook

client = API(access_token='33a9e22e79a6afe67da0e568b0cca830-cf5e494dfe461d8704057859e229b74e')

r = InstrumentsPositionBook(instrument="GBP_USD")
client.request(r)
position_book = r.response

with open('positions_book.csv', 'w') as f:
    writer = csv.writer(f)
    # Write header row
    writer.writerow(['time', 'price', 'longCountPercent', 'shortCountPercent'])
    # Write data rows
    for bucket in position_book['positionBook']['buckets']:
        writer.writerow([
            position_book['positionBook']['time'],
            bucket['price'],
            bucket['longCountPercent'],
            bucket['shortCountPercent']
        ])