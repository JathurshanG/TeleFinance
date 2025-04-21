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
            allHistorical.append(hist)
        allHistorical = pd.concat(allHistorical,ignore_index=True)
        allHistorical.to_csv('files/History.csv',index=False,sep=",")
        return allHistorical
    
    def CalculsOfKpi(self) :
    # On renomme le DataFrame pour coller à ce que l'utilisateur a dit
        dta = self.get_history()

        # On regroupe par date pour le portefeuille complet
        dta_portfolio = dta.groupby('Date')['price'].sum().reset_index()
        dta_portfolio.rename(columns={'price': 'total_portfolio_value'}, inplace=True)

        # Dates et durée
        dta_portfolio['Date'] = pd.to_datetime(dta_portfolio['Date'])
        dta_portfolio.sort_values('Date', inplace=True)
        days = (dta_portfolio['Date'].iloc[-1] - dta_portfolio['Date'].iloc[0]).days
        years = days / 365.25

        # KPI 1: Rendement total
        initial = dta_portfolio['total_portfolio_value'].iloc[0]
        final = dta_portfolio['total_portfolio_value'].iloc[-1]
        total_return = (final - initial) / initial

        # KPI 2: Rendement annualisé
        annualized_return = (1 + total_return)**(1 / years) - 1

        # KPI 3: Rendement mensuel moyen
        dta_portfolio['Month'] = dta_portfolio['Date'].dt.to_period('M')
        monthly_returns = dta_portfolio.groupby('Month')['total_portfolio_value'].last().pct_change().dropna()
        mean_monthly_return = monthly_returns.mean()

        # KPI 4: Volatilité annualisée
        daily_returns = dta_portfolio['total_portfolio_value'].pct_change().dropna()
        volatility_annualized = daily_returns.std() * np.sqrt(252)

        # KPI 5: Max Drawdown
        cum_max = dta_portfolio['total_portfolio_value'].cummax()
        drawdown = (dta_portfolio['total_portfolio_value'] - cum_max) / cum_max
        max_drawdown = drawdown.min()

        # KPI 6: Sharpe ratio (sans risque = 0)
        sharpe_ratio = annualized_return / volatility_annualized if volatility_annualized != 0 else np.nan

        # KPI 7: Mar ratio
        mar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else np.nan

        Text =  {
            "Rendement total (%)": round(total_return * 100, 2),
            "Rendement annualisé (%)": round(annualized_return * 100, 2),
            "Rendement mensuel moyen (%)": round(mean_monthly_return * 100, 2),
            "Volatilité annualisée (%)": round(volatility_annualized * 100, 2),
            "Max Drawdown (%)": round(max_drawdown * 100, 2),
            "Ratio de Sharpe": round(sharpe_ratio, 2),
            "Ratio de Mar": round(mar_ratio, 2),
            "Durée analysée (années)": round(years, 2)
        }

        return Text