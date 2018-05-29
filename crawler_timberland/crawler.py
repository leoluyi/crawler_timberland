import requests
from pyquery import PyQuery as pq
from datetime import datetime
import time


def upsert_timberland(db, collection, product_number='product_number', sleep_sec=None):
    with requests.Session() as sess:
        sess.headers = {'User-Agent': 'Mozilla/5.0'}
        want_cates = list(_get_categories(session=sess).values())
        product_urls = get_product_urls_by_cates(want_cates, session=sess)
        print(f'Got {len(product_urls)} product urls')

        # product_numbers = db.distinct[product_number]

        for _, product_url in enumerate(product_urls):
            out = get_products_info([product_url], session=sess)[0]
            if _ % 20 == 0:
                print(f'Upsert {out["product_number"]}: {out["product_url"]} ...')
            db[collection].replace_one({product_number: out[product_number]}, out, upsert=True)
            if sleep_sec:
                time.sleep(sleep_sec)


def get_products_info(urls, normalize=True, session=None):
    '''Get products info.'''

    def _normalize_product(prod_layout):
        '''List of normalized products.'''
        out = []
        for color in prod_layout['color_variants']:
            out.append({**color,
                        **{k: v for (k, v) in prod_layout.items() if k != 'color_variants'}})

        return out

    out_list = []
    for url in urls:
        out = _get_product_info(url)
        if normalize:
            out = _normalize_product(out)

        out_list.extend(out)

    return out_list


def _get_product_info(prod_url, is_color_variant=False, session=None):

    def _get_color_variant(doc):
        doc_colors = doc('.color-select li a:not(.active)')
        # print(doc_colors)
        urls = [i.attr('href') for i in doc_colors.items()]

        color_variants = []
        for url in urls:
            color_variants.append(_get_product_info(url, is_color_variant=True))

        return color_variants

    def _get_color(doc):
        color = doc('div.color-variant > div.color > b').text()
        product_number = doc('div.color-variant > div.style > b').text()
        img_urls = [i.attr('href') for i in doc('.product-image-slider a').items()]
        return {'product_number': product_number, 'color': color, 'product_url': prod_url, 'img_urls': img_urls}

    if session:
        res = requests.get(prod_url, session=session)
    else:
        res = requests.get(prod_url)

    doc = pq(res.text)

    if is_color_variant:
        return _get_color(doc)
    else:
        series_name = doc('h1.entry-title').text().strip()
        color_variants = [_get_color(doc)]
        color_variants.extend(_get_color_variant(doc))
        description = doc('div.description-content').text().strip()
        _cates = [i.text().strip() for i in doc('.separator+ a').items()]
        cate1 = _cates[1]
        cate2 = _cates[2]
        cate3 = _cates[3] if len(_cates) == 5 else None
        price = doc('span.product-price').text().strip()
        price = int(price.split('TWD')[-1].split('.')[0].replace(',', ''))
        features = doc('.feature-content').text().strip()

    return {
        'series_name': series_name,
        'color_variants': color_variants,
        'description': description,
        'cate1': cate1,
        'cate2': cate2,
        'cate3': cate3,
        'price': price,
        'features': features,
        'data_time': datetime.utcnow().isoformat(),
    }


def get_product_urls_by_cates(cate_urls, session=None):
    out_list = []
    for url in cate_urls:
        out_list.extend(_get_cate_pagination(url))

    return out_list


def _get_cate_pagination(cat_url, session=None, verbose=False):

    def _get_single_page_products(url, referer=cat_url, session=None):
        try:
            if session:
                res = requests.get(url, session=session, headers={'Referer': referer})
            else:
                res = requests.get(url, headers={'Referer': referer})
        except:
            print(f'Error in getting URL: {url}')
            raise

        doc = pq(res.text)
        doc_items = doc('.entry-header > h1 > a')
        items_url = [i.attr('href') for i in doc_items.items()]

        if verbose:
            print(f'Get {url} ...')
            print(doc_items.text())

        return items_url, _get_max_page(doc)

    def _get_max_page(doc):
        nums = doc('[class="page-numbers"]').text()
        max_num = int(max(nums)) if nums else None
        return max_num

    out_list, max_page = _get_single_page_products(cat_url)  # first_page
    if max_page:
        page_links = [cat_url + 'page/' + str(page_num) + '/' for page_num in range(2, max_page + 1)]

        for page in page_links:
            out_list.extend(_get_single_page_products(page)[0])

    return list(set(out_list))


def _get_categories(url_base="http://www.timberland.com.tw", session=None):
    res = requests.get(url_base)
    doc = pq(res.text)
    doc_categories = doc('.sub-menu .sub-menu .menu-item-object-product_category a')
    categories = [(i.text(), i.attr('href')) for i in doc_categories.items()]

    for i, (key, val) in enumerate(categories):
        sex = val.rsplit('/', maxsplit=2)[-2].split('-')[0]
        key = '{sex}-{key}'.format(sex=sex, key=key.replace(' ', ''))
        categories[i] = (key, val)

    return dict(categories)
