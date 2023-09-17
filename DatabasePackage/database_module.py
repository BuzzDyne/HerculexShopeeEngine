import time
import mysql.connector
from typing import Tuple, Dict, List

from _cred import Credentials
from DatabasePackage.constants import ORDER_STATUS_MESSAGES

from datetime import datetime as dt
from datetime import timezone as tz


class DbModule:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            host=Credentials["host"],
            user=Credentials["user"],
            password=Credentials["password"],
            database=Credentials["database"],
        )

        self.cursor = self.cnx.cursor()

    # region Logging
    def Log(self, activityType, desc):
        sql = """
            INSERT INTO globallogging_th (
                application_name, 
                activity_date,
                activity_type,
                description
            ) VALUES ('ShopeeEngine', %s, %s, %s)"""

        val = (time.strftime("%Y-%m-%d %H:%M:%S"), activityType, desc)

        self.cursor.execute(sql, val)
        self.cnx.commit()

    # endregion

    def getProcessSyncDate(self) -> Dict:
        sql = """
            SELECT 
                initial_sync, 
                last_synced,
                access_token, 
                refresh_token
            FROM hcxprocesssyncstatus_tm
            WHERE platform_name = "SHOPEE"
            LIMIT 1
        """

        self.cursor.execute(sql)
        res = self.cursor.fetchall()[0]

        return {
            "initial_sync": res[0],
            "last_synced": res[1],
            "access_token": res[2],
            "refresh_token": res[3],
        }

    def setTokpedLastSynced(self, input_unixTS):
        sql = """
            UPDATE hcxprocesssyncstatus_tm
            SET
                last_synced = %s
            WHERE platform_name = "SHOPEE"
        """

        val = (input_unixTS,)

        self.cursor.execute(sql, val)
        self.cnx.commit()
