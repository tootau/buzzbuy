import os, hashlib, requests, csv
from datetime import datetime

print("Iniciando o robô da Buzzbuy...")

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
    if not APP_KEY or not APP_SECRET: 
        print("Erro: Chaves ausentes.")
        return []
    params = {
        'method': 'aliexpress.affiliate.product.query',
        'app_key': APP_KEY, 'sign_method': 'md5',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json', 'v': '2.0',
        'tracking_id': TRACKING_ID,
        'category_ids': '44',
        'keywords': 'gadget smart',
        'target_currency': 'BRL', 'target_language': 'PT',
        'page_size': '20', 'page_no': '1'
    }
    params['sign'] = generate_signature(APP_SECRET, params)
    try:
        res = requests.post(API_URL, data=params).json()
        print("Resposta do AliExpress:", res) # Agora ele vai nos contar tudo que o site responder!
        resp_key = 'aliexpress_affiliate_product_query_response'
        if resp_key in res:
            return res[resp_key].get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])
    except Exception as e: 
        print("Erro:", e)
    return []

products = get_tech_products()

# Cria o arquivo CSV mesmo vazio, blindando contra erros no GitHub!
with open('produtos_automaticos.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Nome', 'Link', 'Imagem'])
    count = 0
    for p in products:
        nome = p.get('product_title', 'Produto Incrível').replace('<b>', '').replace('</b>', '')
        link = p.get('promotion_link', p.get('product_url', ''))
        imagem = p.get('product_main_image_url', '')
        if link and imagem: 
            writer.writerow([nome, link, imagem])
            count += 1
    print(f"Total salvos com sucesso: {count}")
