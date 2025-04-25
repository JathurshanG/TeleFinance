from utils.finance_data import fetch_history, fetch_basic_info
from utils.io_tools import load_csv, save_csv
import pandas as pd

class DailyRecap:
    def __init__(self, asset_file='data/raw/ActualAsset.csv', history_file='data/raw/History.csv', info_file='data/raw/informations.csv'):
        self.asset_file = asset_file
        self.history_file = history_file
        self.info_file = info_file
        self.data = load_csv(self.asset_file)
        self.data['date'] = pd.to_datetime(self.data['date']).dt.date

    def get_history(self) -> pd.DataFrame:
        all_historical = []
        for _, row in self.data.iterrows():
            hist = fetch_history(row['asset'], pd.to_datetime(row['date']), row['price'])
            all_historical.append(hist)

        all_historical = pd.concat(all_historical, ignore_index=True)
        latest_dates = all_historical.groupby('ticket', as_index=False).agg({"Date": "max"}).rename(columns={"Date": "maxDate"})
        all_historical = all_historical.merge(latest_dates, on="ticket", how="left")
        all_historical['LatestDate'] = all_historical['Date'] == all_historical['maxDate']
        all_historical.drop(columns=['maxDate'], inplace=True)

        save_csv(all_historical, self.history_file)
        return all_historical

    def get_basic_info(self) -> pd.DataFrame:
        basic_info_list = []
        for asset in self.data['asset']:
            info = fetch_basic_info(asset)
            basic_info_list.append(info)

        basic_info_df = pd.concat(basic_info_list, ignore_index=True)
        save_csv(basic_info_df, self.info_file)
        return basic_info_df
