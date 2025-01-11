# import argparse
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import numpy as np
import random
import cloudscraper
from IPython.display import display, HTML
#------------------------------Parser args--------------------------------------------------
# def opcije():
#     parser=argparse.ArgumentParser()
#     parser.add_argument("-pg", "--page-num", dest="page_num", help="Broj stranice",required=False, default=0)
#     parser.add_argument("-sf", "--start_from", dest="start_from", help="Pocetni broj stranice",required=False, default=0)
#     parser.add_argument("-ni", "--number_of_iterations", dest="number_of_iterations", help="Broj kroz koliko ce stranica proci",required=True)
#     parser.add_argument("-nc", "--number_of_checkpoints", dest="number_of_checkpoints", help="Broj checkpointova",required=False, default=0)
#     parser.add_argument("--name", dest="csv_name", help="Ime csv faj;a",required=True)
#     odabir = parser.parse_args()
#     return odabir
#------------------------------Functions--------------------------------------------------
# odabir = opcije()
# start_from = int(odabir.start_from)
# page_num=int(odabir.page_num)+start_from
# number_of_iterations = int(odabir.number_of_iterations)
# number_of_checkpoints = int(odabir.number_of_checkpoints)
# if number_of_iterations%number_of_checkpoints != 0:
#     raise TypeError("Moraju se moc podjelit")
# csv_name = odabir.csv_name
# dataframe = pd.DataFrame({"title":[""],
#                           "link": [""],
#                           "article_class":[""],
#                           "article_class_name":[""],
#                           "num_of_comments":[0],
#                           "num_of_shares":[0],
#                           "picture_path":[""],
#                           "text":[""]})
last_link=None
pageNum=1
number_of_pages=10
proxies ={
    'http':"http://192.168.1.2:8888",
    'https':"https://192.168.1.2:8888",
    #'http':"socks5://194.28.194.146:1080",
   # 'https':"socks5://194.28.194.146:1080",
}
class Connection:
    def __init__(self):
        self._useProxy=True
        self.scraper = cloudscraper.create_scraper(browser={
        "browser": "chrome",
        "platform": "windows"},)
        self.i=-1
        self.proxy="http://192.168.1.2:5000/post-endpoint"
    def make_request(self,url,wait=False):
        headers={"User-Agent":"Mozilla/5.0"}
        self.i = 0 if self.i>=1 else self.i+1
        if self.i ==0:
            res =self.scraper.get(url,headers=headers)
            if res.status_code!=200:
                if wait:
                    time.sleep(30)
                return self.make_request(url)
        else:
            headers={"User-Agent":"Mozilla/5.0","bypass-tunnel-reminder":"False"}

            res =self.scraper.post(self.proxy,data=url,headers=headers,verify=False)
            if res.status_code!=200:
                return self.make_request(url,wait=True)

        return res


def get_url(pageNum):
    return f"https://www.chess.com/games?page={pageNum}"
connection = Connection()

def get_html(url):
    try:
        response = connection.make_request(url)
        html=response.text
        soup = BeautifulSoup(html, features="html.parser")
        return soup
    except Exception as e:
        print(e)

def get_links(url):
    try:
        soup = get_html(url)
        list = []
        for link in soup.find_all("a", class_="post-preview-image"):
            # if link.get("href").startswith("/"):
            #     list.append(f"https://www.klix.ba{link.get('href')}")
            list.append(link.get("href"))
        return list
    except:
        return []
def get_game_Ids(soup):
    try:
        ids=[]
        finder = soup.find_all("a",class_="master-games-clickable-link master-games-td-user")
        if finder != []:
            for a in finder:
                link = a.get("href")
                ids.append(link.split('/')[-1])

        # print(len(ids))
            return ids
        else:
            div = soup.find("div",class_="v5-section-content-wide").find_all("div")[-1]
            if(div.get_text().strip()=="Your search did not match any games. Please try a new search."):
                return False
    except Exception as e:
        print(e)
        return "Greska"

def get_search_link(soup):
    try:
        data= soup.find("nav",class_="ui_pagination-navigation").find_next("a")
        return data.get("href")
    except:
        return False

def appendAllGM():
    dataframe = pd.DataFrame({"links":[]})
    for i in range(1,64):
        links = get_links(get_url(i))
        for link in links:
            dataframe.loc[len(dataframe)] = {"links":link}
        time.sleep(0.1)
    saveDataFrame(dataframe,"links")

gameIds = pd.DataFrame({"games":[]})

def loadGames(link):
    global gameIds
    soup = get_html(link)
    searchLink = get_search_link(soup)
    playerPage = 1
    finishedAll=False
    while not finishedAll:
        findLink = searchLink+f'&page={playerPage}'
        #https://www.chess.com/games/downloadPgn?game_ids=15539659
        print(f"Current page: {playerPage}",end="\r")
        playerPage+=1
        soup = get_html(findLink)
        ids = get_game_Ids(soup)
        if ids==False:
            finishedAll=False
            print()
            break
        for id in ids:
            gameIds.loc[len(gameIds)]={"games":id}
        time.sleep(random.uniform(0.5,5))

def saveDataFrame(df,path):
    df.to_csv(f'{path}.csv',index=False)
def loadDataframe(path):
    return pd.read_csv(path+".csv")
#appendAllGM()

links_df = loadDataframe("linkovi")

def appendAllGames():
    global links_df
    for link in links_df.values:
        index=links_df[links_df.values==link].index
        if index[0]%10==0:
            saveDataFrame(gameIds,f"games3-{index[0]}")
        links_df.drop(index,axis=0,inplace=True)
        link=link[0]
        last_link=link
        print(link)
        loadGames(link)
        print("\n"+"-"*70)
try:
    appendAllGames()
except Exception as e:
    print("\n-----------------------------------ENDED-----------------------------------")
    print(e)
    print(f"Page num: {pageNum}, Last link: {last_link}")
    saveDataFrame(gameIds,"games3")
    saveDataFrame(links_df,"linkovi")