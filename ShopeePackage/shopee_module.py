import requests
import time
import datetime
import hmac
import hashlib
from _cred import ShopeeCred
from ShopeePackage import utils as u


class ShopeeModule:
    def __init__(self, accessToken, refreshToken):
        self.partnerId = ShopeeCred["partner_id"]
        self.partnerKey = ShopeeCred["partner_key"]
        self.shopId = ShopeeCred["shop_id"]
        self.baseURL = ShopeeCred["base_url"]

        self.nMaxRetry = 10

        self.acccessToken = accessToken
        self.refreshToken = refreshToken

    def _create_base_string(
        self, partner_id, api_path, ts, access_token=None, custom_id=None
    ):
        # custom_id can be shop_id/merchant_id
        base_string = f"{partner_id}{api_path}{ts}{access_token if access_token else ''}{custom_id if custom_id else ''}"
        return base_string

    def _call_shopee_api(self, url_path, dict_of_params):
        res = 1

        ts = int(time.time())
        base_string = self._create_base_string(
            self.partnerId, url_path, ts, self.acccessToken, self.shopId
        ).encode()
        sign = hmac.new(
            self.partnerKey.encode(), base_string, hashlib.sha256
        ).hexdigest()
        base_param = {
            "partner_id": self.partnerId,
            "timestamp": ts,
            "access_token": self.acccessToken,
            "shop_id": self.shopId,
            "sign": sign,
        }

        query_param = {**base_param, **dict_of_params}

        url = self.baseURL + url_path

        response = requests.get(url, query_param)
        response_json = response.json()

        return res

    def getActiveOrders(self):
        url_path = "/api/v2/order/get_shipment_list"
        currRetry = 0

        while currRetry < self.nMaxRetry:
            ts = int(time.time())
            base_string = self._create_base_string(
                self.partnerId, url_path, ts, self.acccessToken, self.shopId
            ).encode()
            sign = hmac.new(
                self.partnerKey.encode(), base_string, hashlib.sha256
            ).hexdigest()

            query_param = {
                "partner_id": self.partnerId,
                "timestamp": ts,
                "access_token": self.acccessToken,
                "shop_id": self.shopId,
                "sign": sign,
                "page_size": 100,
            }
            url = self.baseURL + url_path

            response = requests.get(url, query_param)
            response_json = response.json()

            # Retry if "Timestamp is expired."
            if (
                "error" in response_json
                and response_json["error"] == "error_param"
                and "message" in response_json
                and response_json["message"] == "Timestamp is expired."
            ):
                currRetry += 1
                continue
            else:
                break

        response_json

        return response


#
