
def create_base_string(partner_id, api_path, ts, access_token=None, custom_id=None):
    # custom_id can be shop_id/merchant_id
    base_string = f"{partner_id}{api_path}{ts}{access_token if access_token else ''}{custom_id if custom_id else ''}"
    return base_string