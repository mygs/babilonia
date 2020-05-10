#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os, certifi, re, json, requests, datetime
import pandas as pd
from Models import *
from sqlalchemy import create_engine

URL={"CEAGESP":"http://www.ceagesp.gov.br/entrepostos/servicos/cotacoes/#cotacao",
    "STMARCHE":"https://www.marche.com.br/categorias/verduras"}

# Create a session
HOME = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HOME, '../server/app/config.json'), "r") as config_json_file:
    cfg = json.load(config_json_file)
engine = sqlalchemy.create_engine(cfg["SQLALCHEMY_DATABASE_URI"])
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()


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
    dates =  ceagesp_dates(URL["CEAGESP"])
    print(dates)

    for date in dates:
        data = {"cot_grupo": "VERDURAS", "cot_data":date}
        soup = BeautifulSoup(requests.post(url, data).text, 'html.parser')

        table_html = soup.find('table',{"class": "contacao_lista" })
        if table_html is not None:
            table_data = [[cell.text.strip() for cell in row("td")]
                                     for row in table_html("tr")]
            df = pd.DataFrame(table_data[2:], columns=['Produto','Classificacao','Unidade','Menor','Comun','Maior','Quilo'])
            date = datetime.datetime.strptime(date, '%d/%m/%Y')
            date = datetime.date.strftime(date, "%Y-%m-%d")
            price = Prices(SOURCE="CEAGESP", DATE=date, DATA= df.to_json(orient='records') )
            session.merge(price)
            session.commit()
            print (price.toJson())

#ceagesp()

def stmarche():
    html = urlopen(URL["STMARCHE"], cafile=certifi.where())
    pattern = re.compile('.*product-mini.*')
    soup = BeautifulSoup(html, 'html.parser')
    products = soup.findAll('div',pattern)
    for product in products:
        pjson = json.loads(product['data-json'])
        print(pjson)
#stmarche()
