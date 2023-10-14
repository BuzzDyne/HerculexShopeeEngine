from datetime import datetime as dt
from datetime import timezone as tz

from DatabasePackage.database_module import DbModule
from ShopeePackage.shopee_module import ShopeeModule, ShopeeAccessTokenExpired


class App:
    def __init__(self):
        self.db = DbModule()
        syncData = self.db.getProcessSyncDate()
        self.sh = ShopeeModule(syncData["access_token"], syncData["refresh_token"])
        self._refreshAccessToken()

    def _call_ordelist(self):
        start_time = 1696129011
        end_time = 1697165824
        self.sh.getListOrders(start_time, end_time)

        return

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
        PROCESS_NAME = "Sync Orders"

        # Logging
        self.db.Log(PROCESS_NAME, "Process BEGIN")

        # Get On Process Shopee Orders
        listStr_shopee_active_orders = self.sh.getActiveOrders()

        # Get Order Detail from Shopee
        listDict_shope_order_details = self.sh.getOrderDetail(
            listStr_shopee_active_orders
        )

        self.db.Log(
            PROCESS_NAME,
            f"Got {len(listStr_shopee_active_orders)} current active orders from ShopeeAPI",
        )

        # Get Existing
        listDict_db_order_details = self.db.getOrderIDsByEcomIDs(
            listStr_shopee_active_orders
        )

        # Filter ShopeeIDs
        _, listStr_NotFoundInDB = self.separateOrderIDFoundInDbOrNot(
            listDict_shope_order_details, listDict_db_order_details
        )

        n_newOrders = 0
        n_updatedOrders = 0

        # Process Insert New Orders
        for o in listDict_shope_order_details:
            if o["order_sn"] in listStr_NotFoundInDB:
                self.db.processInsertOrder(o)
                n_newOrders += 1

        # Process Update Exs Orders
        # Get List of need to be updated order_sn from DB
        listDict_NeedToCheckDBOrders = self.db.getOrderNeedToBeUpdated(
            listStr_shopee_active_orders
        )

        listStr_NeedToCheckDBOrderIDs = [
            orderData["ecom_order_id"] for orderData in listDict_NeedToCheckDBOrders
        ]

        # Get the detail data from ShopeeAPI
        listDict_shope_order_details = self.sh.getOrderDetail(
            listStr_NeedToCheckDBOrderIDs
        )

        # Update to DB if Status has changed
        for order_to_check in listDict_NeedToCheckDBOrders:
            # Find the corresponding order details in listDict_shope_order_details
            matching_order = next(
                (
                    o
                    for o in listDict_shope_order_details
                    if o["order_sn"] == order_to_check["ecom_order_id"]
                ),
                None,
            )

            if matching_order:
                new_status = matching_order["order_status"]
                old_status = order_to_check["ecom_order_status"]
                if old_status != new_status:
                    # Call the update function as the status has changed
                    curr_dt = dt.now(tz.utc).strftime("%Y-%m-%d %H:%M:%S")
                    if old_status == "READY_TO_SHIP":
                        self.db.processUpdateOrder(
                            order_to_check["id"], new_status, curr_dt, True
                        )
                    else:
                        self.db.processUpdateOrder(
                            order_to_check["id"], new_status, curr_dt, False
                        )
                    n_updatedOrders += 1

        self.db.Log(
            PROCESS_NAME,
            f"Inserted ({n_newOrders}) new orders | Found ({len(listStr_shopee_active_orders) - n_newOrders}) orders already in DB with unchanged status | Checked ({len(listStr_NeedToCheckDBOrderIDs)}) existing orders | Updated ({n_updatedOrders}) orders",
        )
        # Update Sync Table
        currUnixTS = int(dt.now(tz.utc).timestamp())
        self.db.setLastSynced(currUnixTS)
        # Logging
        self.db.Log(PROCESS_NAME, "Process END")


def sync():
    app = App()
    # app._call_ordelist()
    app.syncShopeeNewOrderdata()


sync()
