import requests
import time
import pandas as pd
import numpy as np
import cloudscraper
import random
def loadDataframe(path):
    return pd.read_csv(path+".csv")

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
                    time.sleep(20)
                return self.make_request(url)
        else:
            headers={"User-Agent":"Mozilla/5.0"}
            res =self.scraper.post(self.proxy,data=url,headers=headers,verify=False)
            if res.status_code!=200:
                return self.make_request(url,wait=True)

        return res
connection=Connection()
def get_url(gameId):
    return f"https://www.chess.com/games/downloadPgn?game_ids={gameId}"
def saveDataFrame(df,path):
    df.to_csv(f'{path}.csv',index=False)

def downloadGame(gameId,folder):
    try:
        res = connection.make_request(get_url(gameId))
        open(f"{folder}/{gameId}.pgn", 'wb').write(res.content)

    except Exception as e:
        print(e)
df = loadDataframe('gameIds/chess_games_df')
try:
    for i,id in enumerate(df.values):
        index=df[df.values==id].index
        df.drop(index,axis=0,inplace=True)
        downloadGame(gameId=id[0],folder="games")
        print(f"Number of downloaded games: {i+1}",end="\r")
        time.sleep(random.uniform(1,4))
except:
    print()
    print("\n-----------------------------------ENDED-----------------------------------")
    saveDataFrame(df,"chess_games")
connection = Connection()