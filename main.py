import hmac 
import time
import requests
import hashlib

timest=int(time.time())

host="https://partner.shopeemobile.com"

access_token = "random string"

partner_id =80001

partner_key = "test....."

shop_id =209920

path ="/api/v2/example/shop level/get"

base_string = f"{partner_id}{path}{timest}{access_token}{shop_id}"

sign = hmac.new( partner_key,base_string,hashlib.sha256).hexdigest() 
print(sign)
