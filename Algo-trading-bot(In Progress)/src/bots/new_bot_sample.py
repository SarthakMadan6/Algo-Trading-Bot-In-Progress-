import random

from src.bots.base_trade_bot import OrderType, TradeBot


class TradeBotSample(TradeBot):
    def __init__(self):

        super().__init__()

    def make_order_recommendation(self, ticker):

        if not ticker:
            print("ERROR: ticker cannot be a null value")
            return None

        random_choice = random.choice(
            [OrderType.BUY_RECOMMENDATION, OrderType.SELL_RECOMMENDATION, OrderType.HOLD_RECOMMENDATION]
        )

        return random_choice
