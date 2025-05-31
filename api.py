from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import logging
import uuid , json

# === Flask App Config ===
app = Flask(__name__)
app.secret_key = 'Africa-0000111'  # Replace with a strong secret key to sign session data
CORS(app)

# === Cloudinary Config ===
cloudinary.config(
    cloud_name='dgchvnotv',       # 🔁 Replace with your Cloudinary cloud name
    api_key='396858126569313',    # 🔁 Replace with your API key
    api_secret='qHrrlf7uLApRR7nyp5PlfXKaiZ4'  # 🔁 Replace with your API secret
)
SERVICE_ACCOUNT_INFO = json.loads("""
{
  "type": "service_account",
  "project_id": "africa-457409",
  "private_key_id": "4544f81742344928ebb7ec5dc023f8840a1462f3",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDINKklNHqJF0qG\\nGU9IYCIXP3F1bHrZCkLaYtWglPOS2HKQ0qnjKSNxX1NMWDRU1KqYotWnY0obbpUd\\nmXiXiOFf1uhuDtzFfXzNd94wF1owJapzol4amRMV+5Zlm/XAB5F4Cu2I+MAumV+P\\nwiUHp6ff8rPz3aXAp+syOzW3eZCuiN0ZXFDgPlVj/dRUEFka8cxgFqdpWY4AUV15\\nBnVifEOh71ColsS7DMSelQ7S3XNAjYo8OaGU1D3AsjS9ZonHKpfkximSl4TLvNrS\\nYD6fdQXn1/GfBV/ucOq3fI7wVWun/Xkd9LhOLP0X5Id1Onw+GLbgSXTE5bEhv07C\\nNvKlswLzAgMBAAECggEASzcJkvo3zPhMnbu1fwXq2NwTdp+WOaMywZQfGRDMv48E\\n36bdf4PNloLPKx/6LSKmouiOJzBUv6CYcgHd/eRFc7msIekAhUujTxgpB91GG0+T\\nTZUjEJAQzRHzi2H//jB5tOU6H1sA7KDfd4VjXxBcL/UhKU3Mv2f2oyz+fds0gXUs\\nf52uoZy4iLWGyj5DSsDNrcmTlfi4MJ1U7YdjU5S1ZViC7Z9Es9Nw/GGkPObejZkL\\nUuAyp7xdymK9GSpqIBL4iiy0Qm+odLnsye85WKaxaCf7lQKNeUO5mgWkVkAqkiMt\\nRIfRwvHRlIYvYabsZSh/vJqb6er0Nglso1GQr91qrQKBgQDs3fJsX7ruJZ/wch36\\njyIpRwEA35bKbiEY604UTprafS6+mvoiyXv1T3IBH9DwtZ/64pt2SBUfIsQIPdCH\\ne4fUPGdUcW6ZDxNYVerLYkhMhtr7K5XOnLcX0ose0RBgzX4jtbrbfZxG1k+v8NQS\\n/kZTlPKGJudsZEqZy4/2rgrtnQKBgQDYYJ0c5lTfktsElGWmewIDZzKdJhUxZ+g/\\n6EtGgePYDV/lzuSAWTyftis22MOug4Imd4qYfoDQE9DjwPxPsvrcRFGaPgd1N891\\nytmYW+oM0yx4ocFBUCIMhPjw8SriZN0X4380gPeOx2C4eOG5WE8Qe6XH3Z8hfNr2\\nstk+zCsVzwKBgQDdjpk0X7LlERJygPujo4CrpXu9ymYsgSi6O1c0TXYxSoiPxzyT\\nj21APwh/Hrh8fxbeQFp0H+aJ0iYVI2TLZXPexIVOii+OQXix1uOhTBQeaMGp0NH2\\nicYFJW317E3qjiwf0NuwdOTZqZquEpD8FxXHFnpnmzo6u/C/vJWzgoY8TQKBgQCw\\nRdT4zDPsh2jhzDsbay5ys0mqeHHfc/Tiy003vW1uf0bWorvIS+p1eiSuY9zWeNA4\\noj5IiRZLbTlJsdha3UY813NbIplUxwi9v2mRE6ASnp6mD7CukqeKZ3GeZ/o1wVHU\\nukLQ9Re4O3jyD5hkNCsFFJYzwrp2v45qV71fyVh4RQKBgDA8VJ+BlT1FF4ca0L8J\\nLXw+mQcLsOW8aKoRW9gYqEWPlsh+/vdF6D1/cRZMDjBpW9J4AjbXIGQd1TRvR7gf\\n1jnRopLJcdj7aVE3RAoLH9DtyJX4KOSSw/+SD/N4a+8kjObYJ6we3Z6hJz4eJ3fM\\nR4IpfQMkyv2rMBTOZkiWuAti\\n-----END PRIVATE KEY-----\\n",
  "client_email": "africaapi@africa-457409.iam.gserviceaccount.com",
  "client_id": "113920774812407890212",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/africaapi%40africa-457409.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
""")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
LOGIN_SPREADSHEET_ID = '1pQJ8-xFMfzVG19w9fFP-3Cb29k379oGXIVRm0bk1kI8'  # New sheet ID for login
INVENTORY_SPREADSHEET_ID = '1jJTfIlE_m-b8WMag6uXjgLniOeVKmiCg6ur577c0aDs'  # New sheet ID for karkhana
SHOP_SPREADSHEET_ID = '15T6weqATatNOE4gg6m2zP2L02eCYVOqpJJOxNQWnuLI'  # New sheet ID for shop
CUSTOMER_SPREADSHEET_ID = '1hFi9-Sp8KcE1jXDC9-1CsbBL98VqFvXOrSMxJesa0_c'
GUDAAM_SHEET_RANGE = 'Store1!A1'

# === Auth ===
creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
sheet_service = build('sheets', 'v4', credentials=creds)

# Route for Dashboard (Only accessible if logged in)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' in session:
        return render_template('adminDashboard.html')
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

@app.route('/soldProducts')
def soldProducts():
    if 'username' in session:
        return render_template('sold_products.html')
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
    return ['Store1', 'Store2']

@app.route('/get-dashboard-data', methods=['GET'])
def get_dashboard_data():
    try:
        store_id = session.get('store_id')

        if not store_id:
            return jsonify({'message': 'Store ID is required. Please log in.'}), 400

        # Initialize totals
        total_products_in_shop = 0
        total_products_in_gudaam = 0
        total_customers = 0
        total_sales = 0

        if store_id == 'all':
            store_ids = get_all_store_ids()
        else:
            store_ids = [store_id]

        for store in store_ids:
            # 1. Shop products (shop spreadsheet)
            shop_sheet_range = f'{store}!A2:A'
            shop_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=SHOP_SPREADSHEET_ID,
                range=shop_sheet_range
            ).execute()
            shop_values = shop_result.get('values', [])
            total_products_in_shop += len(shop_values)

            # 2. Gudaam products (inventory spreadsheet)
            gudaam_sheet_range = f'{store}!A2:A'
            gudaam_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=INVENTORY_SPREADSHEET_ID,
                range=gudaam_sheet_range
            ).execute()
            gudaam_values = gudaam_result.get('values', [])
            total_products_in_gudaam += len(gudaam_values)

            # 3. Total customers (customer spreadsheet)
            customer_sheet_range = f'{store}!A2:A'
            customer_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=CUSTOMER_SPREADSHEET_ID,
                range=customer_sheet_range
            ).execute()
            customer_values = customer_result.get('values', [])
            total_customers += len(customer_values)

        # 4. Total sales from 'sp - test' sheet
        sales_sheet_range = f'sp - {store}!D2:D'
        sales_result = sheet_service.spreadsheets().values().get(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=sales_sheet_range
        ).execute()
        sales_values = sales_result.get('values', [])

        for row in sales_values:
            try:
                amount = float(row[0]) if row and row[0] else 0
                total_sales += amount
            except ValueError:
                continue

        dashboard_data = {
            'total_products_in_shop': total_products_in_shop,
            'total_products_in_gudaam': total_products_in_gudaam,
            'total_customers': total_customers,
            'total_sales': total_sales
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
    store_ids = ['Store1'] if key == 'karkhana' else store_ids

    try:
        print(key,store_id)
        products = []
        low_stock = []
        total_inventory = 0  # This will now track only valid products

        ranges = [f'{store}!A2:F' for store in store_ids]
        print(ranges)
        result = sheet_service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges
        ).execute()

        value_ranges = result.get('valueRanges', [])

        for store, store_values in zip(store_ids, value_ranges):
            values = store_values.get('values', [])
            for idx, row in enumerate(values, start=2):
                # Ensure row has at least 5 columns and non-empty title/price
                if len(row) < 4 or not row[0].strip():
                    continue  # skip incomplete rows or blank title

                # Fill missing columns with empty strings
                while len(row) < 6:
                    row.append('')

                product_id, title, price, quantity, unit,size = row[:6]
                quantity = int(quantity) if quantity else 0
                unit = unit if unit else ''
                product = {
                    'id': idx,
                    'store_id': store,
                    'title': title,
                    'price': price,
                    'quantity': quantity,
                    'unit': unit,
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
    unit = data.get('unit')
    size = data.get('size')

    spreadsheet_id = INVENTORY_SPREADSHEET_ID if key == 'karkhana' else SHOP_SPREADSHEET_ID
    store_id = 'Store1' if key == 'karkhana' else store_id

    try:
        sheet_range = f'{store_id}!B{product_id}:F{product_id}'  # B to E matches title to size
        values = [[title, price, quantity,unit, size]]
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
    store_id = 'Store1' if key == 'karkhana' else store_id
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
    unit = request.form.get('unit')
    size = request.form.get('size')
    source = request.form.get('source')  # Get source from form (shop/karkhana)

    if not all([store_id, title, price, quantity, size, source]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Select the correct Spreadsheet ID based on the 'source' field (shop or karkhana)
        spreadsheet_id = SHOP_SPREADSHEET_ID if source == 'shop' else INVENTORY_SPREADSHEET_ID
        store_id = 'Store1' if source != 'shop' else store_id
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
                    existing_rows[idx] = [current_id, title, price, quantity,unit, size]
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
            existing_rows.append([next_id, title, price, quantity,unit, size])

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
            range=f'Store1!A2:F'
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
                    'unit': row[4] if len(row) > 5 else '-',
                    'size': row[5] if len(row) > 6 else '-',
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
        ksheet_range = f'Store1!A2:F'

        if location == 'karkhana':
            result = sheet_service.spreadsheets().values().get(
            spreadsheetId=INVENTORY_SPREADSHEET_ID,
            range=ksheet_range
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
                kupdate_range = f'Store1!D{rows.index(row) + 2}'
                print(update_range)
                if location == 'karkhana':
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=INVENTORY_SPREADSHEET_ID,
                        range=kupdate_range,
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
            sheet_range = f'{store}!A2:G'
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
                        'amount_total': row[4] if len(row) > 4 else "",
                        'amount_paid': row[5] if len(row) > 5 else "",
                        'amount_left': row[6] if len(row) > 6 else ""
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
            sheet_range = f'{store}!A2:G'  # A=Customer ID, B=Name, C=Phone, D=ItemsBought, E=Amount Paid, F=Amount Left
            result = sheet_service.spreadsheets().values().get(
                spreadsheetId=CUSTOMER_SPREADSHEET_ID,
                range=sheet_range
            ).execute()

            values = result.get('values', [])

            if not values:
                continue  # Skip if no data is found for this store

            for row in values:
                amount_left = row[6] if len(row) > 6 else "0"
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
                        'amount_total': row[4] if len(row) > 4 else "",
                        'amount_paid': row[5] if len(row) > 5 else "",
                        'amount_left': amount_left
                    })

        return jsonify({'customers': customers_on_loan}), 200

    except Exception as e:
        logging.error(f"Error fetching customers on loan: {e}")
        return jsonify({'error': str(e)}), 500

from datetime import datetime
@app.route('/add-customers', methods=['POST'])
def add_customers():
    store_id = session.get('store_id')
    if not store_id:
        return jsonify({'message': 'Store ID is required. Please log in.'}), 400

    try:
        data = request.get_json()
        print(data)

        required_fields = ['name', 'phone', 'location', 'items', 'amountPaid', 'amountLeft', 'amountTotal']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields.'}), 400
        location = data['location']
        # ✅ Validate items format
        if not isinstance(data['items'], dict):
            return jsonify({'message': "'items' must be a dictionary."}), 400

        items_list = []
        for key, item in data['items'].items():
            if not all(k in item for k in ['id', 'title', 'quantity', 'size', 'price']):
                return jsonify({'message': f"Invalid item format: {item}"}), 400
            items_list.append(item)

        # ✅ Next customer ID
        sheet_range = f'{store_id}!A2:A'
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        existing_customers = result.get('values', [])
        next_customer_id = len(existing_customers) + 2

        # ✅ Convert item data to JSON string for sheet
        import json
        items_bought_json = json.dumps(data['items'], indent=2)

        # ✅ Append to sheet
        customer_row = [
            next_customer_id,
            data['name'],
            data['phone'] or "-",
            items_bought_json,
            data['amountTotal'],
            data['amountPaid'],
            data['amountLeft']
        ]

        sheet_service.spreadsheets().values().append(
            spreadsheetId=CUSTOMER_SPREADSHEET_ID,
            range=f'{store_id}!A2:G',
            valueInputOption="USER_ENTERED",
            body={"values": [customer_row]}
        ).execute()

        # ✅ Update inventory using valid product id
        for item in items_list:
            product_id = int(item['id'])  # Now properly validated
            quantity_sold = int(item['quantity'])
            update_inventory(data['location'], store_id, product_id, quantity_sold)

        # ✅ Add to sold products
        date = datetime.now().strftime("%Y-%m-%d")
        for item in items_list:
            add_to_sold_products(
                store_id,
                location,
                date,
                item['title'],
                item['price'],
                item['quantity'],
                item['size']
            )

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
    amount_total = data.get('amountTotal')
    amount_paid = data.get('amountPaid')
    amount_left = data.get('amountLeft')

    spreadsheet_id = CUSTOMER_SPREADSHEET_ID

    try:
        sheet_range = f'{store_id}!B{product_id}:G{product_id}'

        # Step 1: Get existing row
        existing_row = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute().get('values', [[]])[0]

        # Step 2: Extract item bought from existing row (D column)
        item_bought = existing_row[2] if len(existing_row) > 2 else ""

        # Step 3: Update with preserved item_bought
        values = [[name, phone, item_bought, amount_total, amount_paid, amount_left]]

        # Step 4: Update the sheet
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
            sheet_range = f'Store1!A2:F'
        elif source_type == 'customer':
            spreadsheet_id = CUSTOMER_SPREADSHEET_ID
            sheet_range = f'{store_id}!A2:F'
        elif source_type == 'soldproduct':
            spreadsheet_id = CUSTOMER_SPREADSHEET_ID
            sheet_range = f'SP - {store_id}!A2:F'
        else:
            return jsonify({'message': 'Invalid type. Must be shop, karkhana, or customer.'}), 400

        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute()

        rows = result.get('values', [])
        print(rows)
        matches = []

        for row in rows:
            if not row or not row[0].strip():  # Skip if ID/customer_id is empty
                continue

            if source_type == 'customer':
                if len(row) > 3 and query in row[1].lower():
                    matches.append({
                        'customer_id': row[0],
                        'name': row[1] if len(row) > 1 else "",
                        'phone': row[2] if len(row) > 2 else "",
                        'items_bought': row[3] if len(row) > 3 else "",
                        'amount_total': row[4] if len(row) > 4 else "",
                        'amount_paid': row[5] if len(row) > 5 else "",
                        'amount_left': row[6] if len(row) > 6 else ""
                    })
            elif source_type == 'soldproduct':
                if len(row) > 1 and query in row[2].lower():
                    matches.append({
                        'id': row[0],
                        'title': row[2],
                        'date': row[1],
                        'amount': row[3],
                        'quantity': row[4],
                        'size': row[5]
                    })
            elif source_type == 'karkhana':
                if len(row) > 1 and query in row[1].lower():
                    matches.append({
                        'id': row[0],
                        'title': row[1],
                        'price': row[2] if len(row) > 2 else "",
                        'size': row[5] if len(row) > 5 else "-",
                        'unit': row[4] if len(row) > 4 else "-",
                        'quantity': row[3] if len(row) > 3 else "0"
                    })
            else:
                if len(row) > 1 and query in row[1].lower():
                    matches.append({
                        'id': row[0],
                        'title': row[1],
                        'price': row[2] if len(row) > 2 else "",
                        'size': row[5] if len(row) > 5 else "-",
                        'unit': row[4] if len(row) > 4 else "-",
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
            return jsonify({'message': 'No items provided'}), 400

        inventory_range = f'Store1!A2:F'
        inventory_result = sheet_service.spreadsheets().values().get(
            spreadsheetId=INVENTORY_SPREADSHEET_ID,
            range=inventory_range
        ).execute()
        inventory_rows = inventory_result.get('values', [])

        for item in items:
            product_id = str(item.get('id'))
            title = item.get('title', '').strip()
            size = item.get('size', '').strip()
            move_qty = int(item.get('quantity'))
            price = item.get('price', '').strip()
            unit = ''

            inventory_found = False

            for i, row in enumerate(inventory_rows):
                if len(row) >= 5 and row[0] == product_id:
                    current_qty = int(row[3])
                    price = row[2]
                    unit = row[4]  # Extract unit from inventory

                    new_qty = current_qty - move_qty
                    if new_qty < 0:
                        return jsonify({'message': f'Not enough stock for: {title}'}), 400

                    update_range = f'Store1!D{i+2}'
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=INVENTORY_SPREADSHEET_ID,
                        range=update_range,
                        valueInputOption='USER_ENTERED',
                        body={'values': [[new_qty]]}
                    ).execute()
                    inventory_found = True
                    break

            if not inventory_found:
                return jsonify({'message': f'Item {title} not found in inventory'}), 400

            shop_range = f'{store_id}!A2:F'
            shop_result = sheet_service.spreadsheets().values().get(
                spreadsheetId=SHOP_SPREADSHEET_ID,
                range=shop_range
            ).execute()
            shop_rows = shop_result.get('values', [])

            matched = False
            for j, row in enumerate(shop_rows):
                if len(row) >= 6 and row[1].strip().lower() == title.lower() and row[5].strip().lower() == size.lower():
                    current_shop_qty = int(row[3]) if row[3].isdigit() else 0
                    new_shop_qty = current_shop_qty + move_qty

                    update_range = f'{store_id}!D{j+2}'
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=SHOP_SPREADSHEET_ID,
                        range=update_range,
                        valueInputOption='USER_ENTERED',
                        body={'values': [[new_shop_qty]]}
                    ).execute()
                    matched = True
                    break

            if not matched:
                # id | title | price | qty | unit | size
                new_id = len(shop_rows) + 2
                new_row = [new_id, title, price, move_qty, unit, size]

                sheet_service.spreadsheets().values().append(
                    spreadsheetId=SHOP_SPREADSHEET_ID,
                    range=shop_range,
                    valueInputOption='USER_ENTERED',
                    body={'values': [new_row]}
                ).execute()

        return jsonify({'status': 'success', 'message': 'Items moved successfully.'}), 200

    except Exception as e:
        logging.error(f"Error in move-inventory-to-shop: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get-sold-products', methods=['GET'])
def get_sold_products():
    store_id = session.get('store_id')
    if not store_id:
        return jsonify({'message': 'Store ID is required. Please log in.'}), 400

    store_ids = get_all_store_ids() if store_id == 'all' else [store_id]
    spreadsheet_id = CUSTOMER_SPREADSHEET_ID

    try:
        sold_products = []
        total_sold = 0

        ranges = [f'SP - {store}!A2:G' for store in store_ids]
        result = sheet_service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=ranges
        ).execute()

        value_ranges = result.get('valueRanges', [])

        for store, store_values in zip(store_ids, value_ranges):
            values = store_values.get('values', [])
            for idx, row in enumerate(values, start=2):
                if len(row) < 7 or not row[0].strip():  # skip if title missing
                    continue

                sold_product_id, date, title, amount, quantity, size, source = row[:7]
                quantity = int(quantity) if quantity else 0
                amount = int(amount) if amount else 0

                product = {
                    'id': idx,
                    'store_id': store,
                    'date': date,
                    'title': title,
                    'amount': amount,
                    'quantity': quantity,
                    'size': size,
                    'source': source
                }

                sold_products.append(product)
                total_sold += amount  # If total = money. Use `quantity` if total = items sold

        if not sold_products:
            return jsonify({'message': 'No sold data found'}), 404

        return jsonify({
            'sold_products': sold_products,
            'total_sold': total_sold
        }), 200

    except Exception as e:
        logging.error(f"Error fetching sold products: {e}")
        return jsonify({'error': 'Something went wrong while fetching sold products.'}), 500
   
import time

def add_to_sold_products(store_ids, location,date, title, amount, quantity, size):
    spreadsheet_id = CUSTOMER_SPREADSHEET_ID
    try:
        
        range_name = f'SP - {store_ids}!A2:F'

        # Get existing rows to determine next ID
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        existing_rows = result.get('values', [])
        
        time.sleep(2)
        if len(existing_rows) == 0:
            next_id = 2
        else:
            next_id = len(existing_rows) + 2

        date = datetime.now().strftime("%Y-%m-%d")
        # Prepare data to insert
        values = [[next_id, date, title, amount, quantity, size if size else "-",location]]
        body = {'values': values}
        
        # Append row
        sheet_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        return jsonify({'status': 'success', 'message': 'Product added to sold list'}), 200

    except Exception as e:
        logging.error(f"Error adding sold product: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete-sold-product/<product_id>', methods=['DELETE'])
def delete_sold_product(product_id):
    store_id = session.get('store_id')

    spreadsheet_id = CUSTOMER_SPREADSHEET_ID
    try:    
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range = f'SP - {store_id}!A2:F'
        ).execute()
        values = result.get("values", [])

        row_index = None
        for i, row in enumerate(values, start=2):
            if row and row[0] == product_id:
                row_index = i
                break

        if row_index is None:
            return jsonify({'status': 'error', 'message': 'Entry not found'}), 404

        sheet_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"SP - {store_id}!A{row_index}:F{row_index}"
        ).execute()

        return jsonify({'status': 'success', 'message': 'Sold Product deleted successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500










import uuid


# In-memory DB (or use Mongo/Postgres)
events = []

@app.route("/track", methods=["POST"])
def track_event():
    data = request.json
    session_id = data.get("session_id", str(uuid.uuid4()))
    event_type = data.get("event_type", "unknown")
    url = data.get("url")
    referrer = data.get("referrer")
    email = data.get("email")
    user_agent = request.headers.get("User-Agent")
    ip = request.remote_addr
    timestamp = datetime.utcnow().isoformat()
    metadata = data.get("metadata", {})
    
    # GeoIP (you need GeoLite2-City.mmdb file from MaxMind)
    

    event_data = {
        "session_id": session_id,
        "email": email,
        "event_type": event_type,
        "url": url,
        "referrer": referrer,
        "timestamp": timestamp,
        "user_agent": user_agent,
        "ip": ip,
        "metadata": metadata
    }

    print("Tracked Event:", event_data)
    return jsonify({"success": True}), 200
@app.route('/events', methods=['GET'])
def get_events():
    return jsonify(events), 200

# === Start Flask App ===
if __name__ == '__main__':
    app.run(debug=True)



