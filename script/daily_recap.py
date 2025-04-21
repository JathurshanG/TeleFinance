import yfinance as yf
import pandas as pd



class DailyRecap:
    def __init__(self):
        self.data = pd.read_csv('files/ActualAsset.csv')
    
    def get_history(self):
        data = self.data
        data["date"] = pd.to_datetime(data['date'])        
        allHistorical =[]
        for i,idx in enumerate(data['asset']):
            ticker = yf.Ticker(idx)
            hist = ticker.history(start=data['date'][i]).reset_index()
            hist = hist[['Date','Close']]
            hist['ticket'] = idx
            hist['Date'] = hist['Date'].dt.date
            allHistorical.append(hist)

        allHistorical = pd.concat(allHistorical,ignore_index=True)
        allHistorical.to_csv('files/History.csv',index=False,sep=",")
        return allHistorical

if __name__ == "__main__":
    daily_recap = DailyRecap()
    data = daily_recap.get_history()
    print(data)