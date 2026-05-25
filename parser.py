import json

from typing import Any, Dict, List, Optional

def extract_product_data(product_json,location_data,url):
    try:
        schema_path=product_json.get('RESPONSE', {}).get('pageData', {}).get('seoData', {}).get('schema', [])
        if not schema_path or not isinstance(schema_path, list) or not schema_path[0] or not isinstance(schema_path[0], dict):
            print("Schema path is missing or not a list")
            return 'not found'
        stock=None
        sku = schema_path[0].get('sku')
        product_name = schema_path[0].get('name')
        try:
            q_type=product_json.get('RESPONSE', {}).get('pageData', {}).get('pageContext', {}).get('fdpEventTracking', {}).get('events', {}).get('psi', {}).get('swa', [])[0].get('attributeName')
            if q_type=='quantity':
                quantity=product_json.get('RESPONSE', {}).get('pageData', {}).get('pageContext', {}).get('fdpEventTracking', {}).get('events', {}).get('psi', {}).get('swa', [])[0].get('attributeValue')
                if quantity:
                    product_name=product_name+' '+quantity
        except Exception as e:
            quantity=''
            q_type = None

        brand = schema_path[0].get('brand', {}).get('name')
        pls=product_json.get('RESPONSE', {}).get('pageData', {}).get('pageContext', {}).get('fdpEventTracking', {}).get('events', {}).get('psi', {}).get('pls', {})
        if pls.get('unserviceabilityReason'):
            stock='No'
        else:
            stock_avaliblity_status = pls.get('availabilityStatus')
            if stock_avaliblity_status=='IN_STOCK':
                stock='Yes'
            else:
                stock='No'
        return{
            'sku':sku,
            'pincode':location_data['pincode'],
            'locality':location_data['locality'],
            'city':location_data['city'],
            'state':location_data['state'],
            'url':url,
            'product_name':product_name,
            'brand':brand,
            'stock_avaliblity_status':stock,
            'EAN_code':location_data['ean_code'],
            'pls':pls,
            'quantity':quantity if quantity else 'N/A',
            'product_data':{**parse_full_product_data(product_json),'sku':sku,
                            'pincode':location_data['pincode'],
                            'locality':location_data['locality'],
                            'city':location_data['city'],
                            'state':location_data['state'],
                            'url':url,
                            'product_name':product_name,
                            'brand':brand,
                            'stock_avaliblity_status':stock,
                            'EAN_code':location_data['ean_code']
                            }
        }
    except Exception as e:
        print(f"Error extracting product data: {e}")
        return 'not found'


def parse_full_product_data(json_data: Dict) -> Dict:
    if not isinstance(json_data, dict):
        return {}

    def _safe_get(data, *keys, default=None):
        current = data
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return current

    def _assign(target: Dict, key: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str) and not value.strip():
            return
        if isinstance(value, (list, dict)) and not value:
            return
        target[key] = value

    def _pick_first(*values):
        for value in values:
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, (list, dict)) and not value:
                continue
            return value
        return None

    result: Dict[str, Any] = {}

    response = json_data.get('RESPONSE', {}) if isinstance(json_data.get('RESPONSE', {}), dict) else {}
    page_data = response.get('pageData', {}) if isinstance(response.get('pageData', {}), dict) else {}
    page_meta = page_data.get('pageMeta', {}) if isinstance(page_data.get('pageMeta', {}), dict) else {}
    page_context = page_data.get('pageContext', {}) if isinstance(page_data.get('pageContext', {}), dict) else {}
    seo_data = page_data.get('seoData', {}) if isinstance(page_data.get('seoData', {}), dict) else {}
    seo = seo_data.get('seo', {}) if isinstance(seo_data.get('seo', {}), dict) else {}
    tracking_context = page_data.get('trackingContext', {}) if isinstance(page_data.get('trackingContext', {}), dict) else {}
    tracking_data_v2 = page_context.get('trackingDataV2', {}) if isinstance(page_context.get('trackingDataV2', {}), dict) else {}
    fdp_tracking = page_context.get('fdpEventTracking', {}) if isinstance(page_context.get('fdpEventTracking', {}), dict) else {}
    events = fdp_tracking.get('events', {}) if isinstance(fdp_tracking.get('events', {}), dict) else {}
    psi = events.get('psi', {}) if isinstance(events.get('psi', {}), dict) else {}
    swa = psi.get('swa', []) if isinstance(psi.get('swa', []), list) else []
    schema_list = seo_data.get('schema', []) if isinstance(seo_data.get('schema', []), list) else []
    schema = schema_list[0] if schema_list and isinstance(schema_list[0], dict) else {}
    dls_layouts = page_data.get('dlsLayouts', {}) if isinstance(page_data.get('dlsLayouts', {}), dict) else {}

    for source_key in (
        'baseImpressionId',
        'parentReqId',
        'widgetFetchDelayMs',
        'reusePrevPageFoldContext',
        'mergeTrackingContextForAllPageFold',
        'pageTTL',
        'backTTL',
        'hardTTL',
        'pageTitle',
        'pageId',
        'pageHash',
        'hasMorePages',
        'infinitePage',
    ):
        _assign(result, source_key, page_meta.get(source_key))

    _assign(result, 'prefetch_position', _safe_get(page_meta, 'prefetchPage', 'position'))
    _assign(result, 'prefetch_enabled', _safe_get(page_meta, 'prefetchPage', 'enablePrefetch'))

    
    _assign(result, 'productID', page_context.get('productId'))

    # for source_key in (
    #     'pageName',
    #     'navigationalPageName',
    #     'navigationalPageType',
    #     'pageType',
    # ):
    #     _assign(result, source_key, tracking_context.get(source_key))

    # _assign(result, 'tracking_mode', _safe_get(tracking_context, 'meta', 'sMode'))
    # _assign(result, 'login_status', _safe_get(tracking_context, 'tracking', 'loginStatus'))

    for source_key in (
        'serviceable',
        'sellerCount',
        'sellerRating',
        'codAvailable',
        'colorPickerAvailable',
    ):
        _assign(result, f'tracking_{source_key}', tracking_data_v2.get(source_key))

    

    
    _assign(result, 'schema_type', _pick_first(schema.get('@type'), schema.get('type')))
    _assign(result, 'schema_description', schema.get('description'))
    _assign(result, 'schema_url', schema.get('url'))
    _assign(result, 'schema_image', _pick_first(schema.get('image'), _safe_get(schema, 'image', 0)))
    _assign(result, 'schema_item_condition', schema.get('itemCondition'))
    _assign(result, 'schema_availability', _safe_get(schema, 'offers', 'availability'))
    _assign(result, 'schema_price', _safe_get(schema, 'offers', 'price'))
    _assign(result, 'schema_price_currency', _safe_get(schema, 'offers', 'priceCurrency'))
    _assign(result, 'schema_offer_url', _safe_get(schema, 'offers', 'url'))
    _assign(result, 'schema_rating_value', _safe_get(schema, 'aggregateRating', 'ratingValue'))
    _assign(result, 'schema_rating_count', _safe_get(schema, 'aggregateRating', 'ratingCount'))
    _assign(result, 'schema_review_count', _safe_get(schema, 'aggregateRating', 'reviewCount'))

    if isinstance(swa, list) and swa:
        first_swa = swa[0] if isinstance(swa[0], dict) else {}
        _assign(result, 'selected_attribute_name', first_swa.get('attributeName'))
        _assign(result, 'selected_attribute_value', first_swa.get('attributeValue'))


    if isinstance(schema, dict):
        schema_summary = {}
        for key in ('@type', 'type', 'name', 'description', 'url', 'itemCondition', 'image'):
            value = schema.get(key)
            if value is not None:
                schema_summary[key] = value
        if schema_summary:
            result['schema_summary'] = schema_summary

    return result




# # ======================= CLI Usage =======================
# if __name__ == "__main__":
#     import sys
#     import os
#     if len(sys.argv) > 1:
#         filepath = sys.argv[1]
#         if os.path.exists(filepath):
#             result = json.load(open(filepath, "r", encoding="utf-8"))
#             result = extract_product_data(result,None,None )
#             with open("parsed_product_data.json", "w", encoding="utf-8") as f:
#                 json.dump(result, f, indent=2, ensure_ascii=False)
#             print(json.dumps(result, indent=2, ensure_ascii=False))
#         else:
#             print(f"File not found: {filepath}")
#     else:
#         print("Usage: python parser.py <path_to_flipkart_json_file>")