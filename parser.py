import json

def extract_product_data(product_json,location_data,url):
    
    sku = product_json.get('RESPONSE', {}).get('pageData', {}).get('seoData', {}).get('schema', [{}])[0].get('sku')
    product_name = product_json.get('RESPONSE', {}).get('pageData', {}).get('seoData', {}).get('schema', [{}])[0].get('name')
    brand = product_json.get('RESPONSE', {}).get('pageData', {}).get('seoData', {}).get('schema', [{}])[0].get('brand', {}).get('name')
    stock_avaliblity_status = product_json.get('RESPONSE', {}).get('pageData', {}).get('pageContext', {}).get('fdpEventTracking', {}).get('events', {}).get('psi', {}).get('pls', {}).get('availabilityStatus')
    stock=None
    if stock_avaliblity_status=='IN_STOCK':
        stock='yes'
    else:
        stock='no'
    return{
        'sku':sku,
        'pincode':location_data['pincode'],
        'locality':location_data['formatted_address'],
        'city':location_data['city'],
        'url':url,
        'product_name':product_name,
        'brand':brand,
        'stock_avaliblity_status':stock,
        'EAN_code':'NA',
    }
    