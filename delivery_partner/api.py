import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def aggregator_webhook():
    import json
    data = frappe.request.get_data()
    
    if not data:
        return {"status": "error", "message": "No data received"}
        
    payload = json.loads(data)
    provider = frappe.request.headers.get("X-Provider", "Unknown") # E.g., Swiggy or Zomato
    
    # Store raw payload for processing
    log = frappe.get_doc({
        "doctype": "Aggregator Order Log",
        "provider": provider,
        "raw_payload": json.dumps(payload, indent=2),
        "status": "Pending",
        "order_id": payload.get("order_id") or payload.get("id")
    })
    log.insert(ignore_permissions=True)
    frappe.db.commit()
    
    # Enqueue background processing
    frappe.enqueue("delivery_partner.api.process_aggregator_order", log_name=log.name, now=True)
    
    return {"status": "success", "message": "Order Received"}

def process_aggregator_order(log_name):
    # Retrieve log and process creation of Sales Order
    log = frappe.get_doc("Aggregator Order Log", log_name)
    try:
        import json
        payload = json.loads(log.raw_payload)
        
        # 1. Fetch Aggregator Settings
        settings = frappe.get_single("Aggregator Settings")
        if not settings.default_customer:
            raise Exception("Default Customer is missing in Aggregator Settings.")
            
        provider = log.provider.lower()
        items = []
        customer_name = settings.default_customer
        
        # 2. Parse payload based on Provider (Swiggy vs Zomato)
        if provider == "zomato":
            # Example Zomato Payload Parsing
            # { "order_id": "123", "customer": {"name": "John", "phone": "123"}, "order_items": [{"item_id": "Z123", "quantity": 1, "price": 100}] }
            order_id = payload.get("order_id")
            for item in payload.get("order_items", []):
                aggregator_item_id = str(item.get("item_id"))
                qty = item.get("quantity")
                rate = item.get("price")
                
                # Find ERPNext Item mapped to this Zomato Item ID
                mapping = frappe.db.get_value("Aggregator Item Mapping", {"provider": "Zomato", "aggregator_item_id": aggregator_item_id}, "erpnext_item")
                if not mapping:
                    raise Exception(f"Item Mapping missing for Zomato ID: {aggregator_item_id}")
                    
                items.append({
                    "item_code": mapping,
                    "qty": qty,
                    "rate": rate
                })
                
        elif provider == "swiggy":
            # Example Swiggy Payload Parsing
            # { "id": "456", "customer_details": {"name": "Jane", "mobile": "456"}, "cart": {"items": [{"item_id": "S456", "qty": 2, "final_price": 200}]} }
            order_id = payload.get("id")
            for item in payload.get("cart", {}).get("items", []):
                aggregator_item_id = str(item.get("item_id"))
                qty = item.get("qty")
                rate = item.get("final_price")
                
                # Find ERPNext Item mapped to this Swiggy Item ID
                mapping = frappe.db.get_value("Aggregator Item Mapping", {"provider": "Swiggy", "aggregator_item_id": aggregator_item_id}, "erpnext_item")
                if not mapping:
                    raise Exception(f"Item Mapping missing for Swiggy ID: {aggregator_item_id}")
                    
                items.append({
                    "item_code": mapping,
                    "qty": qty,
                    "rate": rate
                })
        else:
            raise Exception(f"Unknown Provider: {provider}")
            
        # 3. Create the Sales Order in ERPNext
        if not items:
            raise Exception("No items found in the payload.")
            
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer_name,
            "po_no": f"{log.provider}-{order_id}",
            "items": items,
            # Adjust these generic defaults depending on the user's ERPNext config
        })
        so.insert(ignore_permissions=True)
        so.submit()
        
        log.db_set("status", "Processed")
        frappe.db.commit()
    except Exception as e:
        log.db_set("status", "Failed")
        log.db_set("error_log", str(e))
        frappe.db.commit()

def sync_item_to_aggregators(doc, method):
    # Hook on Item save to push updates to Swiggy/Zomato catalogs
    pass

def sync_item_price_to_aggregators(doc, method):
    # Hook on Item Price save to push price updates
    pass

def notify_aggregator_order_accepted(doc, method):
    # Optional logic: If a user accepts an order in ERPNext, hit Swiggy/Zomato API to mark as accepted
    pass

def notify_aggregator_order_cancelled(doc, method):
    # Logic to notify aggregator if the restaurant cancels the order
    pass
