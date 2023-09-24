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

    def getNewTokens(self):
        """Refreshes both access_token and refresh_token assuming refresh_token exists.

        return access_token, refresh_token"""

        api_path = "/api/v2/auth/access_token/get"
        url = self.baseURL + api_path

        ts = int(time.time())
        base_string = self._create_base_string(self.partnerId, api_path, ts).encode()
        sign = hmac.new(
            self.partnerKey.encode(), base_string, hashlib.sha256
        ).hexdigest()
        query_params = {
            "partner_id": self.partnerId,
            "timestamp": ts,
            "sign": sign,
        }
        request_body = {
            "partner_id": int(self.partnerId),
            "shop_id": int(self.shopId),
            "refresh_token": self.refreshToken,
        }

        response = requests.post(url, params=query_params, json=request_body)

        res_json = response.json()

        try:
            access = res_json["access_token"]
            refresh = res_json["refresh_token"]
        except KeyError as e:
            error_msg = f"Cannot find the field '{e}"
            raise ShopeeAPIError(error_msg)

        return access, refresh

    def _call_shopee_api(self, url_path, dict_of_params):
        """Makes iterative attempts to call ShopeeAPI given its url_path and dict of params.

        return response_json(dict), err_msg(str)"""
        currRetry = 0
        error_msg = None

        while currRetry < self.nMaxRetry:
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

            try:
                response = requests.get(url, query_param)

                response_json = response.json()
                # Check if access_token needed to be refreshed
                if (
                    response.status_code == 403
                    and response_json["message"] == "Invalid access_token."
                ):
                    raise ShopeeAccessTokenExpired()

                response.raise_for_status()  # Raise HTTPError for bad status codes

                if (
                    "error" in response_json
                    and response_json["error"] == "error_param"
                    and "message" in response_json
                    and response_json["message"] == "Timestamp is expired."
                ):
                    currRetry += 1
                    continue
                elif (
                    "error" in response_json
                    and response_json["error"] == ""
                    and "message" in response_json
                    and response_json["message"] == ""
                ):
                    break
                else:
                    error_msg = (
                        f"Shopee API request failed, response got: {response_json}"
                    )
                    raise ShopeeAPIError(error_msg)
            except requests.RequestException as e:
                # Handle network-related errors
                currRetry += 1
                error_msg = str(e)

        return response_json, error_msg

    def getActiveOrders(self):
        url_path = "/api/v2/order/get_shipment_list"

        params = {
            "page_size": 100,
        }

        res_json, err = self._call_shopee_api(url_path, params)
        if err is not None:
            print(err)

        return [order["order_sn"] for order in res_json["response"]["order_list"]]

    def getOrderDetail(self, order_ecom_id):
        url_path = "/api/v2/order/get_order_detail"

        params = {
            "order_sn_list": ",".join(order_ecom_id),
            "response_optional_fields": "buyer_user_id,buyer_username,estimated_shipping_fee",
        }

        res_json, err = self._call_shopee_api(url_path, params)

        return res_json


class ShopeeAPIError(Exception):
    pass


class ShopeeAccessTokenExpired(Exception):
    pass
