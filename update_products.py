import os, hashlib, requests, csv
from datetime import datetime

APP_KEY = os.environ.get('ALI_APP_KEY')
APP_SECRET = os.environ.get('ALI_APP_SECRET')
TRACKING_ID = os.environ.get('ALI_TRACKING_ID', 'buzzbuy01')
API_URL = 'https://api-sg.aliexpress.com/sync'

def generate_signature(secret, params):
    sorted_params = sorted(params.items())
    sign_str = secret
    for key, value in sorted_params:
        if key != 'sign': sign_str += str(key) + str(value)
    sign_str += secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def get_tech_products():
    if not APP_KEY or not APP_SECRET: return []
    params = {
        'method': 'aliexpress.affiliate.product.query',
        'app_key': APP_KEY, 'sign_method': 'md5',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json', 'v': '2.0',
        'tracking_id': TRACKING_ID,
        'category_ids': '44', # Eletrônicos
        'keywords': 'gadget smart',
        'target_currency': 'BRL', 'target_language': 'PT',
        'page_size': '20', 'page_no': '1'
    }
    params['sign'] = generate_signature(APP_SECRET, params)
    try:
        response = requests.post(API_URL, data=params).json()
        resp_key = 'aliexpress_affiliate_product_query_response'
        if resp_key in response:
            return response[resp_key].get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])
    except Exception as e: print("Erro:", e)
    return []

def save_to_csv(products, filename='produtos_automaticos.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nome', 'Link', 'Imagem'])
        for p in products:
            nome = p.get('product_title', 'Produto Incrível').replace('<b>', '').replace('</b>', '')
            link = p.get('promotion_link', p.get('product_url', ''))
            imagem = p.get('product_main_image_url', '')
            if link and imagem: writer.writerow([nome, link, imagem])

if __name__ == '__main__':
    products = get_tech_products()
    if products: save_to_csv(products)
