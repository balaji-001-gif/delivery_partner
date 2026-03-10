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
        # TODO: Lookup Customer and Items, Create Sales Order/Sales Invoice
        log.db_set("status", "Processed")
    except Exception as e:
        log.db_set("status", "Failed")
        log.db_set("error_log", str(e))

def sync_item_to_aggregators(doc, method):
    pass

def sync_item_price_to_aggregators(doc, method):
    pass

def notify_aggregator_order_accepted(doc, method):
    pass

def notify_aggregator_order_cancelled(doc, method):
    pass
