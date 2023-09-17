from DatabasePackage.database_module import DbModule
from ShopeePackage.shopee_module import ShopeeModule


class App:
    def __init__(self):
        self.db = DbModule()
        self.sh = ShopeeModule()

    def testGetOrderList(self):
        listOfOrders = []

        return listOfOrders

    def syncShopeeExsOrderData(self):
        return

    def syncShopeeNewOrderdata(self):
        currUnixTS = int(dt.now(tz.utc).timestamp())
        PROCESS_NAME = "Sync New Orders"

        # Logging
        self.db.Log(PROCESS_NAME, "Process BEGIN")

        # Get Sync Date
        sync_info = self.db.getProcessSyncDate()
        start_period = (
            sync_info["initial_sync"]
            if sync_info["last_synced"] is None
            else sync_info["last_synced"]
        )
        end_period = currUnixTS
        self.db.Log(
            PROCESS_NAME, f"StartPeriod : {start_period} | EndPeriod : {end_period}"
        )

        if start_period > end_period:
            self.db.Log(
                PROCESS_NAME, "initial/last sync time is bigger than current time"
            )
            self.db.Log(PROCESS_NAME, "Process END")
            return

        #


def create():
    app = App()
    app.syncShopeeNewOrderdata()


def update():
    app = App()
    app.syncShopeeExsOrderData()
