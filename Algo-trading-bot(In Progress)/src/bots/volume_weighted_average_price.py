import pandas as pd

from src.bots.base_trade_bot import OrderType, TradeBot


class TradeBotVWAP(TradeBot):
    def __init__(self):

        super().__init__()

    def calculate_VWAP(self, stock_history_df):

        if stock_history_df is None:
            print("ERROR: stock_history_df cannot be null")
            return 0

        if stock_history_df.empty:
            print("ERROR: stock_history_df cannot be empty")
            return 0

        stock_history_df["close_price"] = pd.to_numeric(stock_history_df["close_price"], errors="coerce")
        stock_history_df["volume"] = pd.to_numeric(stock_history_df["volume"], errors="coerce")

        sum_of_volumes = stock_history_df["volume"].sum()
        dot_product = stock_history_df["volume"].dot(stock_history_df["close_price"])


        vwap = round(dot_product / sum_of_volumes, 2)

        return vwap

    def make_order_recommendation(self, ticker):


        if not ticker:
            print("ERROR: ticker cannot be a null value")
            return None

        stock_history_df = self.get_stock_history_dataframe(ticker, interval="5minute", time_span="day")

        vwap = self.calculate_VWAP(stock_history_df)

        current_price = self.get_current_market_price(ticker)

        if current_price < vwap:
            return OrderType.BUY_RECOMMENDATION

        elif current_price > vwap:
            return OrderType.SELL_RECOMMENDATION

        else:
            return OrderType.HOLD_RECOMMENDATION
