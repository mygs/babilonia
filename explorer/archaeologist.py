#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import certifi, re, json, requests
import pandas as pd


def ceagesp_dates(url):
    html = urlopen(url)
    pattern = re.compile("var Grupos = ")
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script',text=pattern)
    script=str(script)
    group = script[script.find("var Grupos = "):script.find(";")]
    group = json.loads(group.replace('var Grupos = ', ''))
    return group['VERDURAS']

def ceagesp():
    url = "http://www.ceagesp.gov.br/entrepostos/servicos/cotacoes/#cotacao"
    data = {"cot_grupo": "VERDURAS", "cot_data": ceagesp_dates(url)[0]}
    soup = BeautifulSoup(requests.post(url, data).text, 'html.parser')

    table_html = soup.find('table',{"class": "contacao_lista" })
    if table_html is not None:
        table_data = [[cell.text.strip() for cell in row("td")]
                                 for row in table_html("tr")]
        df = pd.DataFrame(table_data[2:], columns=['Produto','Classificacao','Uni|Peso','Menor','Comun','Maior','Quilo'])
        print (df.to_json(orient='records'))
    else:
        print("None!!!!!")

ceagesp()

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
