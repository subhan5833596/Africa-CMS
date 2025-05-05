from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import logging
import uuid

# === Flask App Config ===
app = Flask(__name__)
app.secret_key = 'your_secret_keys'  # Replace with a strong secret key to sign session data
CORS(app)

# === Cloudinary Config ===
cloudinary.config(
    cloud_name='dgchvnotv',       # 🔁 Replace with your Cloudinary cloud name
    api_key='396858126569313',    # 🔁 Replace with your API key
    api_secret='qHrrlf7uLApRR7nyp5PlfXKaiZ4'  # 🔁 Replace with your API secret
)

SERVICE_ACCOUNT_FILE = 'credential.json'
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
LOGIN_SPREADSHEET_ID = '1pQJ8-xFMfzVG19w9fFP-3Cb29k379oGXIVRm0bk1kI8'  # New sheet ID for login
INVENTORY_SPREADSHEET_ID = '1jJTfIlE_m-b8WMag6uXjgLniOeVKmiCg6ur577c0aDs'  # New sheet ID for karkhana
SHOP_SPREADSHEET_ID = '15T6weqATatNOE4gg6m2zP2L02eCYVOqpJJOxNQWnuLI'  # New sheet ID for shop
CUSTOMER_SPREADSHEET_ID = '1hFi9-Sp8KcE1jXDC9-1CsbBL98VqFvXOrSMxJesa0_c'
SHEET_RANGE = 'Sheet1!A1'

# === Auth ===
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
sheet_service = build('sheets', 'v4', credentials=creds)

# Route for Dashboard (Only accessible if logged in)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

# Route for Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required', 'status': 'error'}), 400

        try:
            # Fetch all data from the login sheet
            result = sheet_service.spreadsheets().values().get(
                spreadsheetId=LOGIN_SPREADSHEET_ID,
                range='Sheet1!A2:C'  # Fetch columns A, B, C (USERNAME, PASSWORD, STORE_ID)
            ).execute()

            values = result.get('values', [])

            if not values:
                return jsonify({'message': 'No data found in the sheet', 'status': 'error'}), 404

            # Search for matching credentials
            for row in values:
                stored_username = row[0]
                stored_password = row[1]
                store_id = row[2]

                if username == stored_username and password == stored_password:
                    # Store user data in session
                    session['username'] = username
                    session['store_id'] = store_id

                    return jsonify({'message': 'Login successful', 'status': 'success', 'store_id': store_id}), 200

            return jsonify({'message': 'Invalid credentials', 'status': 'error'}), 401

        except Exception as e:
            return jsonify({'message': str(e), 'status': 'error'}), 500

    # If it's a GET request, render the login page
    return render_template('login.html')

# Route for Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clears the session data (logs the user out)
    return jsonify({'message': 'Logged out successfully', 'status': 'success'}), 200

# Route to Check Login Status
@app.route('/check-login', methods=['GET'])
def check_login():
    # Check if the user is logged in by looking for session data
    if 'username' in session:
        return jsonify({'message': 'User is logged in', 'status': 'success', 'username': session['username'], 'store_id': session['store_id']}), 200
    else:
        return jsonify({'message': 'User is not logged in', 'status': 'error'}), 401

# Routes for Inventory, Customer, POS, Upload
@app.route('/inventory')
def inventory():
    if 'username' in session:
        return render_template('inventory.html')
    else:
        return redirect(url_for('login'))
    

@app.route('/shop')
def shop():
    if 'username' in session:
        return render_template('shop.html')
    else:
        return redirect(url_for('login'))

@app.route('/customer')
def customer():
    if 'username' in session:
        return render_template('customer.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/loan')
def loan():
    if 'username' in session:
        return render_template('loan.html')
    else:
        return redirect(url_for('login'))

@app.route('/pos')
def pos():
    if 'username' in session:
        return render_template('pos.html')
    else:
        return redirect(url_for('login'))

@app.route('/upload')
def upload():
    if 'username' in session:
        return render_template('product_upload.html')
    else:
        return redirect(url_for('login'))

# Optional: Serve a homepage if needed
@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/move_inventory')
def move_inventory():
    if 'username' in session:
        return render_template('move_inventory.html')
    else:
        return redirect(url_for('login'))

from datetime import datetime
def get_all_store_ids():
    # Assuming you fetch all store IDs from a database or an external service
    # Example return value
    return ['Store1', 'Store2', 'Store3']

@app.route('/get-dashboard-data', methods=['GET'])
def get_dashboard_data():
    try:
        store_id = session.get('store_id')

        if not store_id:
            return jsonify({'message': 'Store ID is required. Please log in.'}), 400

        # Initialize variables
        total_products_in_shop = 0
        total_products_in_karkhana = 0
        total_customers = 0
        total_loan_money = 0

        if store_id == 'all':
            store_ids = get_all_store_ids()
        else:
            store_ids = [store_id]

        for store in store_ids:
            # 1. Count shop products
            shop_sheet_range = f'{store}!A2:A'
            shop_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=SHOP_SPREADSHEET_ID,
                range=shop_sheet_range
            ).execute()
            shop_values = shop_result.get('values', [])
            total_products_in_shop += len(shop_values)

            # 2. Count karkhana products
            karkhana_sheet_range = f'{store}!A2:A'
            karkhana_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=INVENTORY_SPREADSHEET_ID,
                range=karkhana_sheet_range
            ).execute()
            karkhana_values = karkhana_result.get('values', [])
            total_products_in_karkhana += len(karkhana_values)

            # 3. Total Customers & Loan Money
            customer_sheet_range = f'{store}!A2:F'
            customer_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=CUSTOMER_SPREADSHEET_ID,
                range=customer_sheet_range
            ).execute()
            customer_values = customer_result.get('values', [])
            total_customers += len(customer_values)

            for row in customer_values:
                amount_left = float(row[5]) if len(row) > 5 and row[5] else 0
                if amount_left > 0:
                    total_loan_money += amount_left

        dashboard_data = {
            'total_products_in_shop': total_products_in_shop,
            'total_products_in_karkhana': total_products_in_karkhana,
            'total_customers': total_customers,
            'loan_money': total_loan_money
        }

        return jsonify({'dashboard_data': dashboard_data}), 200

    except Exception as e:
        logging.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-products', methods=['GET'])
def get_products():
    key = request.args.get('karkhana')
    
    store_id = session.get('store_id')
    
    if not store_id:
        return jsonify({'message': 'Store ID is required. Please log in.'}), 400

    store_ids = get_all_store_ids() if store_id == 'all' else [store_id]
    spreadsheet_id = INVENTORY_SPREADSHEET_ID if key == 'karkhana' else SHOP_SPREADSHEET_ID

    try:
        print(key)
        products = []
        low_stock = []
        total_inventory = 0  # This will now track only valid products

        ranges = [f'{store}!A2:F' for store in store_ids]
        result = sheet_service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges
        ).execute()

        value_ranges = result.get('valueRanges', [])

        for store, store_values in zip(store_ids, value_ranges):
            values = store_values.get('values', [])
            for idx, row in enumerate(values, start=2):
                # Ensure row has at least 5 columns and non-empty title/price
                if len(row) < 5 or not row[0].strip():
                    continue

                product_id, title, price, quantity, size = row[:5]
                quantity = int(quantity) if quantity else 0

                product = {
                    'id': idx,
                    'store_id': store,
                    'title': title,
                    'price': price,
                    'quantity': quantity,
                    'size': size
                }
                products.append(product)
                total_inventory += 1  # Count only valid products

                if quantity < 1:
                    low_stock.append(product)

        if not products:
            return jsonify({'message': 'No data found in the sheets'}), 404

        return jsonify({
            'products': products,
            'total_inventory': total_inventory,
            'low_stock': low_stock
        }), 200

    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    store_id = session.get('store_id')
    key = request.args.get('karkhana')

    data = request.get_json()
    title = data.get('title')
    price = data.get('price')
    quantity = data.get('quantity')
    size = data.get('size')

    spreadsheet_id = INVENTORY_SPREADSHEET_ID if key == 'karkhana' else SHOP_SPREADSHEET_ID

    try:
        sheet_range = f'{store_id}!B{product_id}:E{product_id}'  # B to E matches title to size
        values = [[title, price, quantity, size]]
        print(values)
        sheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption='RAW',
            body={'values': values}
        ).execute()

        return jsonify({'status': 'success', 'message': 'Product updated successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
  
@app.route('/delete-product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    store_id = session.get('store_id')
    key = request.args.get('karkhana')

    spreadsheet_id = INVENTORY_SPREADSHEET_ID if key == 'karkhana' else SHOP_SPREADSHEET_ID

    try:
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{store_id}!A2:Z"
        ).execute()
        values = result.get("values", [])

        row_index = None
        for i, row in enumerate(values, start=2):
            if row and row[0] == product_id:
                row_index = i
                break

        if row_index is None:
            return jsonify({'status': 'error', 'message': 'Product not found'}), 404

        sheet_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{store_id}!A{row_index}:Z{row_index}"
        ).execute()

        return jsonify({'status': 'success', 'message': 'Product deleted successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/add-product', methods=['POST'])
def add_product():
    store_id = session.get('store_id')
    title = request.form.get('title')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    size = request.form.get('size')
    source = request.form.get('source')  # Get source from form (shop/karkhana)

    if not all([store_id, title, price, quantity, size, source]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Select the correct Spreadsheet ID based on the 'source' field (shop or karkhana)
        spreadsheet_id = SHOP_SPREADSHEET_ID if source == 'shop' else INVENTORY_SPREADSHEET_ID

        # Get all rows from the sheet (we need to check both ID and existing rows)
        sheet_data = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{store_id}!A:F'  # Get all columns, since we want to check the ID and other data
        ).execute()

        existing_rows = sheet_data.get('values', [])
        product_found = False
        next_id = None

        # Check if the product ID exists and find the correct next ID
        for idx, row in enumerate(existing_rows):
            # Skip header row (assuming the first row is a header)
            if idx == 0:
                continue

            if row and row[0].isdigit():  # Ensure that the ID is a valid number
                current_id = int(row[0])  # Convert the ID to an integer
                if current_id == next_id:
                    # Update the row if product ID exists (assuming ID is in column A)
                    existing_rows[idx] = [current_id, title, price, quantity, size]
                    product_found = True
                    break
            else:
                # Skip invalid rows
                continue

        if not product_found:
            # If product doesn't exist, find the max ID and calculate next_id
            existing_ids = [
                int(row[0]) for row in existing_rows if row and row[0].isdigit()
            ]  # Get all valid existing IDs
            next_id = max(existing_ids) + 1 if existing_ids else 1

            # Add new product to the next available row (append)
            existing_rows.append([next_id, title, price, quantity, size])

        # Write back the updated rows to the sheet (overwrite the entire range)
        body = {'values': existing_rows}
        sheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'{store_id}!A1',  # Start writing from the first row
            valueInputOption='RAW',
            body=body
        ).execute()

        return jsonify({
            'status': 'success',
            'message': 'Product added/updated',
            'product_id': next_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product-search', methods=['POST'])
def product_search():
    store_id = session.get('store_id')
    data = request.get_json()
    keyword = data.get('keyword', '').strip().lower()

    if not store_id:
        return jsonify({'error': 'Missing store_id or keyword'}), 400

    try:
        # Read all products from Google Sheet
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=INVENTORY_SPREADSHEET_ID,
            range=f'{store_id}!A2:F'
        ).execute()

        rows = result.get('values', [])
        matched_products = []

        for row in rows:
            title = row[2].lower() if len(row) > 2 else ''
            if keyword in title:
                product = {
                    'id': int(row[0]) if len(row) > 0 else None,
                    'title': row[1] if len(row) > 2 else '',
                    'price': float(row[2]) if len(row) > 3 else 0.0,
                    'quantity': int(row[3]) if len(row) > 4 else 0,
                    'size': row[4] if len(row) > 5 else '',
                }
                matched_products.append(product)

        # Return empty array if no products found, and indicate that there are no matches
        if not matched_products:
            return jsonify({'products': [], 'message': 'No products found matching your search'}), 200

        return jsonify({'products': matched_products}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()

    # 1. Validate the input data
    if not data.get('customerName') or not data.get('customerPhone'):
        return jsonify({'error': 'Customer name and phone are required'}), 400
    if data.get('moneyPaid') is None or data.get('remainingBalance') is None:
        return jsonify({'error': 'Money paid and remaining balance are required'}), 400
    if not data.get('products') or len(data['products']) == 0:
        return jsonify({'error': 'No products in the checkout data'}), 400

    customer_name = data['customerName']
    customer_phone = data['customerPhone']
    money_paid = data['moneyPaid']
    remaining_balance = data['remainingBalance']
    products = data['products']
    store_id = session.get('store_id')

    if not store_id:
        return jsonify({'error': 'Store ID is missing or session expired'}), 400

    # 2. Authenticate Google Sheets API
    try:
        # Update inventory first
        for product in products:
            product_id = product['id']
            quantity_sold = product['quantity']
            update_inventory(store_id, product_id, quantity_sold)

        # Optionally, store customer data (e.g., in a customer sheet)
        store_customer_data(store_id, customer_name, customer_phone, products, money_paid, remaining_balance)

        return jsonify({'message': 'Checkout successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def update_inventory(location,store_id, product_id, quantity_sold):
    try:
        # Get the current inventory for the product (dynamically use store_id as sheet name)
        sheet_range = f'{store_id}!A2:E'
        if location == 'karkhana':
            result = sheet_service.spreadsheets().values().get(
            spreadsheetId=INVENTORY_SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        else:
            result = sheet_service.spreadsheets().values().get(
            spreadsheetId=SHOP_SPREADSHEET_ID,
            range=sheet_range
        ).execute()
          # Assuming store_id is the sheet name
        

        rows = result.get('values', [])
        print(rows)
        for row in rows:
           
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == product_id:  # Check if product ID matches
                current_quantity = int(row[3])  # Column E (index 4) contains quantity
                new_quantity = current_quantity - quantity_sold
                if new_quantity < 0:
                    raise ValueError("Insufficient stock")

                # Update the quantity in the sheet (dynamically use store_id as sheet name)
                update_range = f'{store_id}!D{rows.index(row) + 2}'  # Row is 1-based, so add 2
                print(update_range)
                if location == 'karkhana':
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=INVENTORY_SPREADSHEET_ID,
                        range=update_range,
                        valueInputOption="USER_ENTERED",
                        body={"values": [[new_quantity]]}
                    ).execute()
                else:
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=SHOP_SPREADSHEET_ID,
                        range=update_range,
                        valueInputOption="USER_ENTERED",
                        body={"values": [[new_quantity]]}
                    ).execute()

                break
    except Exception as e:
        raise Exception(f"Error updating inventory: {e}")

def store_customer_data(store_id, name, phone, items_bought_list, amount_paid, remaining_balance):
    try:
        # Fetch existing data to count current customers
        sheet_range = f'{store_id}!A2:A'
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        existing_customers = result.get('values', [])
        customer_id = len(existing_customers) + 1  # Auto-increment customer ID

        # Prepare itemsBought string (Title x Quantity (Size))
        items_bought_str = ', '.join(
            f"{item['title']} x {item['quantity']} ({item['size']})" for item in items_bought_list
        )

        # If phone is empty, put '-'
        phone = phone if phone else "-"

        customer_data = [[
            customer_id,
            name,
            phone,
            items_bought_str,
            amount_paid,
            remaining_balance
        ]]

        # Append the data
        sheet_service.spreadsheets().values().append(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=f'{store_id}!A2:F',
            valueInputOption="USER_ENTERED",
            body={"values": customer_data}
        ).execute()

    except Exception as e:
        raise Exception(f"Error storing customer data: {e}")

@app.route('/get-customers', methods=['GET'])
def get_customers():
    store_id = session.get('store_id')

    if not store_id:
        return jsonify({'message': 'Store ID is required. Please log in.'}), 400

    try:
        if store_id == 'all':
            store_ids = get_all_store_ids()  # This should return a list of all store IDs
        else:
            store_ids = [store_id]

        customers = []

        for store in store_ids:
            sheet_range = f'{store}!A2:F'
            result = sheet_service.spreadsheets().values().get(
                spreadsheetId=CUSTOMER_SPREADSHEET_ID,
                range=sheet_range
            ).execute()

            values = result.get('values', [])

            if not values:
                continue

            for row in values:
                if len(row) > 0 and row[0].strip() != "":  # Only include rows with non-empty customer_id
                    customers.append({
                        'customer_id': row[0],
                        'name': row[1] if len(row) > 1 else "",
                        'phone': row[2] if len(row) > 2 else "",
                        'items_bought': row[3] if len(row) > 3 else "",
                        'amount_paid': row[4] if len(row) > 4 else "",
                        'amount_left': row[5] if len(row) > 5 else ""
                    })

        return jsonify({'customers': customers}), 200

    except Exception as e:
        logging.error(f"Error fetching customers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-customers-on-loan', methods=['GET'])
def get_onloan_customers():
    store_id = session.get('store_id')

    if not store_id:
        return jsonify({'message': 'Store ID is required. Please log in.'}), 400

    try:
        if store_id == 'all':
            store_ids = get_all_store_ids()  # This should return a list of all store IDs
        else:
            store_ids = [store_id]  # Use the specific store ID

        customers_on_loan = []

        # Loop through each store ID (either all or the specific one)
        for store in store_ids:
            sheet_range = f'{store}!A2:F'  # A=Customer ID, B=Name, C=Phone, D=ItemsBought, E=Amount Paid, F=Amount Left
            result = sheet_service.spreadsheets().values().get(
                spreadsheetId=CUSTOMER_SPREADSHEET_ID,
                range=sheet_range
            ).execute()

            values = result.get('values', [])

            if not values:
                continue  # Skip if no data is found for this store

            for row in values:
                amount_left = row[5] if len(row) > 5 else "0"
                print(row)
                # Safely convert to number for comparison
                try:
                    amount_left_num = float(amount_left)
                except:
                    amount_left_num = 0

                if amount_left_num > 0:
                    customers_on_loan.append({
                        'customer_id': row[0] if len(row) > 0 else "",
                        'name': row[1] if len(row) > 1 else "",
                        'phone': row[2] if len(row) > 2 else "",
                        'items_bought': row[3] if len(row) > 3 else "",
                        'amount_paid': row[4] if len(row) > 4 else "",
                        'amount_left': amount_left
                    })

        return jsonify({'customers': customers_on_loan}), 200

    except Exception as e:
        logging.error(f"Error fetching customers on loan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/add-customers', methods=['POST'])
def add_customers():
    store_id = session.get('store_id')

    if not store_id:
        return jsonify({'message': 'Store ID is required. Please log in.'}), 400

    try:
        data = request.get_json()
        print(data)
        required_fields = ['name', 'phone', 'location', 'items', 'amountPaid', 'amountLeft']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields.'}), 400

        if not isinstance(data['items'], list):
            return jsonify({'message': "'items' must be a list."}), 400
        for item in data['items']:
            if not isinstance(item, dict) or not all(k in item for k in ['id', 'title', 'quantity']):
                return jsonify({'message': f"Invalid item format: {item}"}), 400

        # --- 🔁 Update inventory for each product
        for item in data['items']:
            update_inventory(data['location'],store_id, int(item['id']), int(item['quantity']))

        # --- 🆔 Get next customer ID
        sheet_range = f'{store_id}!A2:A'
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        existing_customers = result.get('values', [])
        next_customer_id = len(existing_customers) + 1

        # --- 🛒 Format item summary
        items_bought_str = ', '.join(
            f"{item['title']} x {item['quantity']} x {item['size']}" for item in data['items']
        )

        # --- 📤 Append customer to sheet
        customer_row = [
            next_customer_id,
            data['name'],
            data['phone'] if data['phone'] else "-",
            items_bought_str,
            data['amountPaid'],
            data['amountLeft']
        ]

        sheet_service.spreadsheets().values().append(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=f'{store_id}!A2:G',
            valueInputOption="USER_ENTERED",
            body={"values": [customer_row]}
        ).execute()

        return jsonify({'message': 'Customer added and inventory updated successfully.'}), 200

    except Exception as e:
        logging.error(f"Error adding customer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-customer/<int:product_id>', methods=['PUT'])
def update_customer(product_id):
    store_id = session.get('store_id')

    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    items_bought = data.get('items_bought')
    amount_paid = data.get('amountPaid')
    amount_left = data.get('amountLeft')
    

    spreadsheet_id = CUSTOMER_SPREADSHEET_ID

    try:
        sheet_range = f'{store_id}!B{product_id}:F{product_id}'  # B to E matches title to size
        values = [[name, phone, items_bought, amount_paid, amount_left]]
        print(values)
        sheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption='RAW',
            body={'values': values}
        ).execute()

        return jsonify({'status': 'success', 'message': 'Customer updated successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
  
@app.route('/delete-customer/<product_id>', methods=['DELETE'])
def delete_customer(product_id):
    store_id = session.get('store_id')
    spreadsheet_id = CUSTOMER_SPREADSHEET_ID

    try:
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{store_id}!A2:Z"
        ).execute()
        values = result.get("values", [])

        row_index = None
        for i, row in enumerate(values, start=2):
            if row and row[0] == product_id:
                row_index = i
                break

        if row_index is None:
            return jsonify({'status': 'error', 'message': 'Customer not found'}), 404

        sheet_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{store_id}!A{row_index}:Z{row_index}"
        ).execute()

        return jsonify({'status': 'success', 'message': 'Customer deleted successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/search-product', methods=['GET'])
def search_product():
    try:
        query = request.args.get('q', '').lower()
        source_type = request.args.get('type', '').lower()
        store_id = session.get('store_id')

        if not store_id:
            return jsonify({'message': 'Store ID is required.'}), 400

        if not query or not source_type:
            return jsonify({'message': 'Query and type are required.'}), 400

        # Determine the correct spreadsheet
        if source_type == 'shop':
            spreadsheet_id = SHOP_SPREADSHEET_ID
            sheet_range = f'{store_id}!A2:F'
        elif source_type == 'karkhana':
            spreadsheet_id = INVENTORY_SPREADSHEET_ID
            sheet_range = f'{store_id}!A2:F'
        elif source_type == 'customer':
            spreadsheet_id = CUSTOMER_SPREADSHEET_ID
            sheet_range = f'{store_id}!A2:F'
        else:
            return jsonify({'message': 'Invalid type. Must be shop, karkhana, or customer.'}), 400

        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute()

        rows = result.get('values', [])
        matches = []

        for row in rows:
            if not row or not row[0].strip():  # Skip if ID/customer_id is empty
                continue

            if source_type == 'customer':
                if len(row) > 3 and query in row[1].lower():
                    matches.append({
                        'customer_id': row[0],
                        'name': row[1],
                        'phone': row[2],
                        'items': row[3],
                        'amount_paid': row[4],
                        'amount_left': row[5]
                    })
            else:
                if len(row) > 1 and query in row[1].lower():
                    matches.append({
                        'id': row[0],
                        'title': row[1],
                        'price': row[2] if len(row) > 2 else "",
                        'size': row[4] if len(row) > 4 else "",
                        'quantity': row[3] if len(row) > 3 else ""
                    })

        return jsonify({'results': matches}), 200

    except Exception as e:
        logging.error(f"Error searching product: {e}")
        return jsonify({'error': str(e)}), 500

# Move Inventory to Shop
@app.route('/move-inventory-to-shop', methods=['POST'])
def move_inventory_to_shop():
    try:
        store_id = session.get('store_id')
        data = request.get_json()
        items = data.get('items', [])

        if not items:
            return jsonify({'message': 'No items selected to move.'}), 400

        for item in items:
            product_id = item.get('product_id')
            title = item.get('title', '').strip()
            quantity_raw = item.get('quantity')

            try:
                quantity = int(quantity_raw)
            except (ValueError, TypeError):
                return jsonify({'message': f'Invalid quantity for item: {title}'}), 400

            # 1. Fetch inventory data
            inventory_range = f'{store_id}!A2:E'
            inventory_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=INVENTORY_SPREADSHEET_ID,
                range=inventory_range
            ).execute()
            rows = inventory_result.get('values', [])

            found = False
            for index, row in enumerate(rows):
                if len(row) > 4 and row[0] == product_id:
                    try:
                        current_quantity = int(row[3])
                    except (ValueError, TypeError):
                        return jsonify({'message': f'Invalid current quantity in inventory for {title}'}), 400

                    new_quantity = current_quantity - quantity
                    if new_quantity < 0:
                        return jsonify({'message': f'Insufficient quantity for {title}'}), 400

                    update_range = f'{store_id}!D{index + 2}'  # Adjust row index
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=INVENTORY_SPREADSHEET_ID,
                        range=update_range,
                        valueInputOption="USER_ENTERED",
                        body={"values": [[new_quantity]]}
                    ).execute()
                    found = True
                    break

            if not found:
                return jsonify({'message': f'Product {title} not found in inventory'}), 400

            # 2. Append to shop sheet
            shop_range = f'{store_id}!A2:E'
            shop_values = [product_id, title, "", quantity, ""]
            sheet_service.spreadsheets().values().append(
                spreadsheetId=SHOP_SPREADSHEET_ID,
                range=shop_range,
                valueInputOption="USER_ENTERED",
                body={"values": [shop_values]}
            ).execute()

        return jsonify({'status': 'success', 'message': 'Items moved successfully.'}), 200

    except Exception as e:
        logging.error(f"Error in move-inventory-to-shop: {e}")
        return jsonify({'error': str(e)}), 500



# === Start Flask App ===
if __name__ == '__main__':
    app.run('0.0.0.0',debug=True, port=5000)



