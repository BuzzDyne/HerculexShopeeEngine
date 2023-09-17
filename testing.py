from ShopeePackage.shopee_module import ShopeeModule
from DatabasePackage.database_module import DbModule

db = DbModule()
res = db.getProcessSyncDate()
sh = ShopeeModule(res["access_token"], res["refresh_token"])

# Create a dictionary to store the counts of unique ("error", "message") combinations
error_message_counts = {}

for i in range(100):
    resJson = sh.getAllOrders()

    # Check if both "error" and "message" keys are present in the response
    if "error" in resJson and "message" in resJson:
        error_value = resJson["error"]
        message_value = resJson["message"]

        # Create a tuple to represent the combination of "error" and "message" values
        error_message_combo = (error_value, message_value)

        # Update the counts for the combination
        if error_message_combo in error_message_counts:
            error_message_counts[error_message_combo] += 1
        else:
            error_message_counts[error_message_combo] = 1

    print(".", end="")

print("")

# Print the unique ("error", "message") combinations and their counts
for combo, count in error_message_counts.items():
    error_value, message_value = combo
    print(f"Count: {count}; Error: '{error_value}'; Message: '{message_value}'")
