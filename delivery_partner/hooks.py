app_name = "delivery_partner"
app_title = "Delivery Partner"
app_publisher = "Balaji"
app_description = "Integration with Delivery Partners (Swiggy/Zomato)"
app_email = "balaji@example.com"
app_license = "mit"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/delivery_partner/css/delivery_partner.css"
# app_include_js = "/assets/delivery_partner/js/delivery_partner.js"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Item": {
        "on_update": "delivery_partner.api.sync_item_to_aggregators"
    },
    "Item Price": {
        "on_update": "delivery_partner.api.sync_item_price_to_aggregators"
    },
    "Sales Order": {
        "on_submit": "delivery_partner.api.notify_aggregator_order_accepted",
        "on_cancel": "delivery_partner.api.notify_aggregator_order_cancelled"
    }
}
