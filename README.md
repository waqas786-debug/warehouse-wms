# Warehouse Management System (WMS)

A full-stack **Warehouse Management System (WMS)** built with **Flask**, **SQLAlchemy**, **Flask-WTF**, and **Bootstrap 5** for the Web Engineering (CSE601330) project. The application provides end-to-end warehouse operations, multi-tier storage tracking, inbound procurement, outbound order fulfillment, fleet dispatch management, and a self-service Customer Order & Live Tracking Portal.

## Key Features
- **Role-Based Authentication & Sessions:** Session-backed login with `@login_required` access control, CSRF protection via Flask-WTF, and Post-Redirect-Get (PRG) form workflows.
- **42-Model Relational Database Schema:** Normalized SQLAlchemy ORM architecture covering RBAC (`users`, `roles`, `permissions`), facility hierarchy (`warehouses`, `zones`, `aisles`, `racks`, `shelves`, `storage_bins`), catalog (`products`, `product_categories`, `units_of_measure`), inbound (`purchase_orders`, `goods_received_notes`, `putaway_tasks`), inventory (`bin_stocks`, `inventory_batches`, `stock_adjustments`), outbound (`customer_orders`, `pick_lists`, `packing_boxes`), and fleet logistics (`shipping_carriers`, `delivery_vehicles`, `dispatch_manifests`, `shipments`, `proof_of_deliveries`).
- **Inventory & Low-Stock Monitoring:** Real-time bin-level stock tracking and aggregate product-level reorder alerts.
- **Inbound & Outbound Fulfillment:** Purchase order receiving, pick-list execution with automatic bin stock deduction, and direct handoff to fleet assignment.
- **Fleet Logistics & Proof of Delivery (POD):** Carrier and vehicle assignment, manifest generation, and delivery confirmation (`Completed` status update).
- **Customer Self-Service Portal:** Customers can place new orders and track real-time fulfillment progress across a 4-stage visual tracking timeline (`Placed` -> `Picked & Dispatched` -> `In-Transit` -> `Delivered`) with carrier and POD details.

## Setup & Installation
1. Clone the repository and create a virtual environment:
   ```bash
   git clone https://github.com/waqas786-debug/warehouse-wms.git
   cd warehouse-wms
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Environment variables (optional, defaults configured in `config.py`):
   ```bash
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="sqlite:///warehouse.db"
   ```
4. Seed the database and run the app:
   ```bash
   python seed.py
   python verify_schema.py
   python run.py
   ```

## Live Deployment
Hosted on PythonAnywhere: https://yellomellow.pythonanywhere.com
