import requests
import os

# Flask API URL
url = "http://127.0.0.1:5000/add-product"

# Product data
data = {
    'title': 'Sample Product',
    'price': '250',
    'quantity': '10',
    'size': 'L'
}

# Image path (make sure the file exists)
image_path = r'C:\Users\swagkicks\Downloads\sandals.png'
if not os.path.exists(image_path):
    print("Image not found:", image_path)
    exit()

# Prepare image file for upload
files = {
    'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/png')
}

# Send POST request
response = requests.post(url, data=data, files=files)

# Close file
files['image'][1].close()

# Print response
if response.status_code == 200:
    print("✅ Product added successfully!")
    print("📝 Response:", response.json())
else:
    print("❌ Failed to add product. Status Code:", response.status_code)
    print("Error:", response.json())



# import requests

# # Send GET request to fetch products
# response = requests.get('http://127.0.0.1:5000/get-products')

# # Print the response status code and content
# print(f"Status Code: {response.status_code}")
# print("Response Data:")
# print(response.json())
