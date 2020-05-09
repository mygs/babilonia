#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import certifi

url = "https://www.marche.com.br/categorias/verduras"
html = urlopen(url, cafile=certifi.where())


soup = BeautifulSoup(html, 'lxml')
type(soup)


title = soup.title
print(title)
