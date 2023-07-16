import pandas as pd

from src.bots.base_trade_bot import OrderType, TradeBot


class TradeBotSimpleMovingAverage(TradeBot):
    def __init__(self):

        super().__init__()

    def calculate_simple_moving_average(self, stock_history_df, number_of_days):

        if stock_history_df is None:
            print("ERROR: stock_history_df cannot be null")
            return 0

        if stock_history_df.empty:
            print("ERROR: stock_history_df cannot be empty")
            return 0

        if not number_of_days or number_of_days <= 0:
            print("ERROR: number_of_days must be a positive number.")
            return 0

        stock_history_df["close_price"] = pd.to_numeric(stock_history_df["close_price"], errors="coerce")

        n_day_stock_history = stock_history_df.tail(number_of_days)

        n_day_moving_average = round(n_day_stock_history["close_price"].mean(), 2)

        return n_day_moving_average

    def make_order_recommendation(self, ticker):

        if not ticker:
            print("ERROR: ticker cannot be a null value")
            return None

        stock_history_df = self.get_stock_history_dataframe(ticker)

        moving_average_200_day = self.calculate_simple_moving_average(stock_history_df, 200)


        moving_average_50_day = self.calculate_simple_moving_average(stock_history_df, 50)

        if moving_average_50_day > moving_average_200_day:
            return OrderType.BUY_RECOMMENDATION

        elif moving_average_50_day < moving_average_200_day:
            return OrderType.SELL_RECOMMENDATION

        else:
            return OrderType.HOLD_RECOMMENDATION
