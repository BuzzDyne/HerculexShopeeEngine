from DatabasePackage.database_module import DbModule
from ShopeePackage.shopee_module import ShopeeModule, ShopeeAPIError


class App:
    def __init__(self):
        self.db = DbModule()
        syncData = self.db.getProcessSyncData()
        self.sh = ShopeeModule(syncData['access_token'], syncData['refresh_token'])

    def testGetOrderList(self):
        listOfOrders = []

        return listOfOrders

    def syncShopeeExsOrderData(self):
        return

    def syncShopeeNewOrderdata(self):
        PROCESS_NAME = "Sync New Orders"

        # Logging
        self.db.Log(PROCESS_NAME, "Process BEGIN")

        # Get Active Order
        try:
            order_sn_list = [item['order_sn'] for item in self.sh.getActiveOrders()]

            order_details_response = self.sh.getOrderDetail(order_sn_list)


        except ShopeeAPIError as e:
            print("Shopee API Error:", str(e))
        except Exception as e:
            print("An unexpected error occurred:", str(e))


def create():
    app = App()
    app.syncShopeeNewOrderdata()


def update():
    app = App()
    app.syncShopeeExsOrderData()
