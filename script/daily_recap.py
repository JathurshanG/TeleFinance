import yfinance as yf
import pandas as pd
import numpy as np


class DailyRecap:
    def __init__(self):
        self.data = pd.read_csv('files/ActualAsset.csv')
    
    def get_history(self):
        data = self.data
        data["date"] = pd.to_datetime(data['date'])
        data['date'] = data['date'].dt.date        
        allHistorical =[]
        for i,idx in enumerate(data['asset']):
            ticker = yf.Ticker(idx)
            hist = ticker.history(start=data['date'][i]).reset_index()
            hist = hist[['Date','Close']]
            hist['ticket'] = idx
            hist['Date'] = hist['Date'].dt.date
            int =  data['price'][i] / hist[hist['Date'] == data["date"][i]]['Close']
            hist["price"] = hist['Close'] * int[0]
            hist.loc[hist['Date']==data['date'][i],"EntryDate"] = True
            allHistorical.append(hist)
        allHistorical = pd.concat(allHistorical,ignore_index=True)
        getMaxDate = allHistorical.groupby(['ticket'], as_index=False).agg({"Date": "max"})
        getMaxDate.rename(columns={"Date": "maxDate"}, inplace=True)
        allHistorical = allHistorical.merge(getMaxDate, how="left", on="ticket")
        allHistorical.loc[allHistorical['Date'] == allHistorical['maxDate'],"LatestDate"] = True
        allHistorical.drop(columns=['maxDate'],inplace=True)
        allHistorical.to_csv('files/History.csv',index=False,sep=",")
        return allHistorical
    
    def GetBasicInfo(self) :
        data = self.data
        basicInfo = []
        for i in data['asset']:
            info = yf.Ticker(i).info
            datas = pd.DataFrame({"ticker" : i,
                                  "shorName" : info["shortName"],
                                  "sector" : info['sector'],
                                  "currency" : info['currency'],
                                  'market' : info['market']
                                  },index=[0])
            basicInfo.append(datas)
        basicInfo = pd.concat(basicInfo,ignore_index=True)
        basicInfo.to_csv('files/informations.csv',index=False)
        return basicInfo