#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

try:
    import urllib2
    import urllib
except ImportError:
    import urllib.request as urllib2
    import urllib

def query_stock(productCode):
    url = "https://d.uniqlo.cn/p/stock/stock/query/zh_CN"

    headers = {
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Authorization": "",
        "Content-Type": "application/json",
        "Origin": "https://www.uniqlo.cn",
        "Referer": "https://www.uniqlo.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    data = json.dumps({
        "distribution": "EXPRESS",
        "productCode": productCode,
        "type": "DETAIL"
    })

    req = urllib2.Request(url, data=data.encode('utf-8'), headers=headers)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())

    return result

def send_push(content):
    spt = os.environ.get('WXPUHER_APPTOKEN')
    if not spt:
        print("未设置 WXPUHER_APPTOKEN 环境变量")
        return

    url = 'https://wxpusher.zjiecode.com/api/send/message/simple-push'
    data = {
        "content": content,
        "summary": "<h1>获取到库存</h1>",
        "contentType": 1,
        "spt": spt
    }

    try:
        req = urllib2.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        response = urllib2.urlopen(req)
        result = json.loads(response.read())
        if result.get('success'):
            print("推送成功")
        else:
            print("推送失败:", result)
    except Exception as e:
        print("推送异常:", str(e))

def main():
    sku_env = os.environ.get('uniqlo_sku', 'u0000000063174007,u0000000063174006')
    sku_list = [s.strip() for s in sku_env.split(',') if s.strip()]

    productCode = os.environ.get('productCode', 'u0000000063174')

    stock_data = query_stock(productCode)

    if not stock_data.get('success') or not stock_data.get('resp'):
        print("请求失败或无数据")
        return

    stocks = stock_data['resp'][0]
    sku_stocks = stocks.get('skuStocks', {})
    express_stocks = stocks.get('expressSkuStocks', {})
    bpl_stocks = stocks.get('bplStocks', {})

    results = []
    for sku in sku_list:
        sku_stock = sku_stocks.get(sku, 0)
        express_stock = express_stocks.get(sku, 0)
        bpl_stock = bpl_stocks.get(sku, 0)

        if sku_stock > 0 and express_stock > 0 and bpl_stock > 0:
            line = "%s: skuStocks=%s, expressSkuStocks=%s, bplStocks=%s" % (
                sku, sku_stock, express_stock, bpl_stock)
            print(line)
            results.append(line)

    if results:
        content = "<br>".join(results)
        send_push(content)

if __name__ == '__main__':
    main()
