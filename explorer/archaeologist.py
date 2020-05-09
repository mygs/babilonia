#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import certifi
import re
import json

def stmarche():
    url = "https://www.marche.com.br/categorias/verduras"
    html = urlopen(url, cafile=certifi.where())

    pattern = re.compile('.*product-mini.*')

    soup = BeautifulSoup(html, 'html.parser')
    products = soup.findAll('div',pattern)
    for product in products:
        pjson = json.loads(product['data-json'])
        print(pjson)

#stmarche()
