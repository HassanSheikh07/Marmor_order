from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "It works on Railway!"}
    
WC_API_URL = "https://testingmarmorkrafts.store/wp-json/wc/v3"
WC_CONSUMER_KEY = "ck_fb05462837d9679c0f6c8b11ccbac57d09c79638"
WC_CONSUMER_SECRET = "cs_cd485ed45fc41da284d567e0d49cb8a272fbe4f1"

@app.get("/order-status-1/{order_id}")
def get_order_status(order_id: int, request: Request):
    # Step 1: Check if the request includes logged-in user's email
    user_email = request.headers.get("X-User-Email")
    if not user_email:
        return JSONResponse(
            status_code=401,
            content={"error": "Please log in to view your order status."}
        )

    # Step 2: Fetch order details from WooCommerce API
    url = f"{WC_API_URL}/orders/{order_id}"
    response = requests.get(url, auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))

    if response.status_code != 200:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": "Failed to fetch order details"}
        )

    order_data = response.json()

    # Step 3: Check if the order belongs to the logged-in user
    order_email = order_data.get("billing", {}).get("email", "")
    if order_email.lower() != user_email.lower():
        return JSONResponse(
            status_code=403,
            content={"error": "You are not authorized to access this order."}
        )

    # Step 4: Extract tracking number if available
    tracking_number = "Not available"
    for meta_item in order_data.get("meta_data", []):
        if meta_item.get("key") == "_wc_shipment_tracking_items":
            tracking_items = meta_item.get("value", [])
            if tracking_items:
                tracking_number = tracking_items[0].get("tracking_number", "Not available")
            break

    # Step 5: Return safe and filtered order info
    formatted_response = {
        "@context": "https://schema.org",
        "@type": "Order",
        "order_number": order_data["number"],
        "status": order_data["status"],
        "currency": order_data["currency"],
        "total": order_data["total"],
        "shipping_method": order_data["shipping_lines"][0]["method_title"] if order_data.get("shipping_lines") else "N/A",
        "billing_address": order_data["billing"],
        "shipping_address": order_data["shipping"],
        "tracking_number": tracking_number,
        "order_date": order_data["date_created"],
        "line_items": [
            {"name": item["name"], "quantity": item["quantity"], "price": item["price"]}
            for item in order_data["line_items"]
        ],
    }

    return JSONResponse(content=formatted_response)
