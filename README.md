# Delivery Partner Integration

This is a custom Frappe application for integrating Delivery platforms (like Swiggy/Zomato) with ERPNext.

Compatible with ERPNext/Frappe v15.

## Architecture
This app contains the following integration flows:
- Sync incoming orders -> ERPNext Sales Orders
- Sync menu/items -> ERPNext Item Master
- Update order statuses
