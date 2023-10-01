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
        # self.sh.refreshToken = refresh

    def separateOrderIDFoundInDbOrNot(self, listDict_shopeeID, listDict_dbID):
        # Extract order_sn values from Shopee orders
        shopee_order_sns = [order["order_sn"] for order in listDict_shopeeID]

        # Extract ecom_order_id values from DB orders
        db_order_ids = [db_order["ecom_order_id"] for db_order in listDict_dbID]

        # Initialize lists to store IDs
        FoundInDB = []
        NotFoundInDB = []

        # Check if each Shopee order ID is in the DB list
        for shopee_order_sn in shopee_order_sns:
            if shopee_order_sn in db_order_ids:
                FoundInDB.append(shopee_order_sn)
            else:
                NotFoundInDB.append(shopee_order_sn)

        return FoundInDB, NotFoundInDB

    def testGetOrderList(self):
        listOfOrders = []

        return listOfOrders

    def syncShopeeNewOrderdata(self):
        PROCESS_NAME = "Sync New Orders"

        # Logging
        self.db.Log(PROCESS_NAME, "Process BEGIN")

        # Get On Process Shopee Orders
        success = False
        while not success:
            try:
                listStr_of_shopee_active_orders = self.sh.getActiveOrders()
                success = True
            except ShopeeAccessTokenExpired as e:
                self._refreshAccessToken()

        # Get Order Detail from Shopee
        listDict_shope_order_details = self.sh.getOrderDetail(
            listStr_of_shopee_active_orders
        )

        # Get Existing
        listDict_db_order_details = self.db.getOrderIDsByEcomIDs(
            listStr_of_shopee_active_orders
        )

        # Filter ShopeeIDs
        listStr_FoundInDB, listStr_NotFoundInDB = self.separateOrderIDFoundInDbOrNot(
            listDict_shope_order_details, listDict_db_order_details
        )

        print()
        # Process
        for o in listDict_shope_order_details:
            if o.get("order_sn") in listStr_NotFoundInDB:
                # New
                self.db.processInsertOrder(o)
            else:
            # Exisitng
            self.db.processUpdateOrder(o)
        # Logging
        self.db.Log(PROCESS_NAME, "Process END")


def create():
    app = App()
    app.syncShopeeNewOrderdata()


create()
