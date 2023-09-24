from DatabasePackage.database_module import DbModule
from ShopeePackage.shopee_module import ShopeeModule, ShopeeAccessTokenExpired


class App:
    def __init__(self):
        self.db = DbModule()
        syncData = self.db.getProcessSyncDate()
        self.sh = ShopeeModule(syncData["access_token"], syncData["refresh_token"])
        self._refreshAccessToken()

    def _refreshAccessToken(self):
        access, refresh = self.sh.getNewTokens()

        self.db.setShopeeTokens(access, refresh)

        self.sh.acccessToken = access
        self.sh.refreshToken = refresh

    def testGetOrderList(self):
        listOfOrders = []

        return listOfOrders

    def syncShopeeExsOrderData(self):
        return

    def syncShopeeNewOrderdata(self):
        PROCESS_NAME = "Sync New Orders"

        # Logging
        self.db.Log(PROCESS_NAME, "Process BEGIN")

        # Get On Process Shopee Orders
        success = False
        while not success:
            try:
                list_of_shopee_active_orders = self.sh.getActiveOrders()
                success = True
            except ShopeeAccessTokenExpired as e:
                self._refreshAccessToken()

        # Test
        self.sh.getOrderDetail(list_of_shopee_active_orders)

        # Logging
        self.db.Log(PROCESS_NAME, "Process END")


def create():
    app = App()
    app.syncShopeeNewOrderdata()
