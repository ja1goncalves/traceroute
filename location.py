import geoip2.database

reader = geoip2.database.Reader('./data/GeoLite2-City.mmdb')
response = reader.city('8.8.8.8')

print(response.country.iso_code)

reader.close()
