import time
import mysql.connector

from _cred import Credentials


class DbModule:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            host=Credentials["host"],
            user=Credentials["user"],
            password=Credentials["password"],
            database=Credentials["database"],
        )

        self.cursor = self.cnx.cursor()

    def _insertOrder(self, orderData):
        sql = """
            INSERT INTO order_tm (
                ecommerce_code, ecom_order_id, buyer_id, ecom_order_status,
                pltf_deadline_dt, feeding_dt
            ) VALUES (
                %s, %s, %s, %s,
                FROM_UNIXTIME(%s),%s
            )
        """

        param = (
            "S",
            orderData.get("order_sn"),
            orderData.get("buyer_user_id"),
            orderData.get("order_status"),
            orderData.get("ship_by_date"),
            time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.cursor.execute(sql, param)
        self.cnx.commit()

        return self.cursor.lastrowid

    def _insertOrderItem(self, ecom_order_id, itemData):
        sql = """
            INSERT INTO orderitem_tr (
                ecom_order_id, ecom_product_id, product_name, quantity, product_price
            ) VALUES (%s, %s, %s, %s, %s)
        """

        discounted_price = itemData.get("model_discounted_price")

        if (
            discounted_price is not None
            and discounted_price < itemData["model_original_price"]
        ):
            final_price = discounted_price
        else:
            final_price = itemData["model_original_price"]

        param = (
            ecom_order_id,
            itemData.get("item_id"),
            itemData.get("item_name"),
            itemData.get("model_quantity_purchased"),
            final_price,
        )

        self.cursor.execute(sql, param)
        self.cnx.commit()

    def _insertOrderTracking(self, order_id, activity_msg):
        sql = """
            INSERT INTO ordertracking_th (
                order_id, activity_msg, user_id
            ) VALUES (
                %s, %s, %s
            )
        """

        param = (order_id, activity_msg, "1")

        self.cursor.execute(sql, param)
        self.cnx.commit()

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

    def processInsertOrder(self, single_order_detail):
        ecom_order_id = single_order_detail.get("order_sn")

        for item in single_order_detail.get("item_list"):
            self._insertOrderItem(ecom_order_id, item)

        order_id = self._insertOrder(single_order_detail)
        self._insertOrderTracking(order_id, "Inserted data from Shopee to system")
        return

    def processUpdateOrder(
        self,
        curr_db_order_id,
        new_shopee_order_status,
        str_currdatetime,
        isUpdateShippedDate,
    ):
        if isUpdateShippedDate:
            sql = """
                UPDATE order_tm
                SET
                    ecom_order_status = %s,
                    last_updated_ts = %s,
                    shipped_dt = %s
                WHERE id = %s AND ecommerce_code = "S"
            """
            val = (
                new_shopee_order_status,
                str_currdatetime,
                str_currdatetime,
                curr_db_order_id,
            )

            self.cursor.execute(sql, val)
        else:
            sql = """
                UPDATE order_tm
                SET
                    ecom_order_status = %s,
                    last_updated_ts = %s
                WHERE id = %s AND ecommerce_code = "S"
            """
            val = (
                new_shopee_order_status,
                str_currdatetime,
                curr_db_order_id,
            )

            self.cursor.execute(sql, val)

        # Insert Tracking
        activity_msg = (
            f"Order #{curr_db_order_id} status updated to {new_shopee_order_status}"
        )
        self._insertOrderTracking(curr_db_order_id, activity_msg)
        return

    def getProcessSyncDate(self):
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

    def setLastSynced(self, input_unixTS):
        sql = """
            UPDATE hcxprocesssyncstatus_tm
            SET
                last_synced = %s
            WHERE platform_name = "SHOPEE"
        """

        val = (input_unixTS,)

        self.cursor.execute(sql, val)
        self.cnx.commit()

    def setShopeeTokens(self, access_token, refresh_token):
        sql = """
            UPDATE hcxprocesssyncstatus_tm
            SET
                access_token = %s,
                refresh_token = %s
            WHERE platform_name = "SHOPEE"
        """

        val = (
            access_token,
            refresh_token,
        )

        self.cursor.execute(sql, val)
        self.cnx.commit()

    def getOrderIDsByEcomIDs(self, list_of_ecoms_id):
        keys = ["id", "ecom_order_id", "ecom_order_status"]
        format_string = ",".join(["%s"] * len(list_of_ecoms_id))

        sql = (
            """
            SELECT 
                id, 
                ecom_order_id,
                ecom_order_status
            FROM order_tm
            WHERE ecommerce_code = "S"
            AND ecom_order_id IN (%s)
        """
            % format_string
        )
        self.cursor.execute(sql, tuple(list_of_ecoms_id))
        res = self.cursor.fetchall()

        res_dict = [dict(zip(keys, values)) for values in res]

        return res_dict

    def getOrderNeedToBeUpdated(self, listStr_NotIn_Ecoms_id):
        keys = ["id", "ecom_order_id", "ecom_order_status"]
        format_string = ",".join(["%s"] * len(listStr_NotIn_Ecoms_id))

        sql = (
            """
            SELECT 
                id, 
                ecom_order_id,
                ecom_order_status
            FROM order_tm
            WHERE ecommerce_code = "S"
            AND ecom_order_status = "READY_TO_SHIP"
            AND ecom_order_id NOT IN (%s)
            
        """
            % format_string
        )
        self.cursor.execute(sql, tuple(listStr_NotIn_Ecoms_id))
        res = self.cursor.fetchall()

        res_dict = [dict(zip(keys, values)) for values in res]

        return res_dict
