from enum import Enum

import pandas as pd
import pyotp
import robin_stocks.robinhood as robinhood

from src.utilities import RobinhoodCredentials


class OrderType(Enum):
    BUY_RECOMMENDATION = 1
    SELL_RECOMMENDATION = 0
    HOLD_RECOMMENDATION = -1


class TradeBot:
    def __init__(self):

        robinhood_credentials = RobinhoodCredentials()
        totp = None

        if robinhood_credentials.mfa_code == "":
            print(
                "WARNING: MFA code is not supplied. Multi-factor authentication will not be attempted. If your "
                "Robinhood account uses MFA to log in, this will fail and may lock you out of your accounts for "
                "some period of time."
            )

        else:
            totp = pyotp.TOTP(robinhood_credentials.mfa_code).now()

        robinhood.login(robinhood_credentials.user, robinhood_credentials.password, mfa_code=totp)

    def robinhood_logout(self):


        robinhood.logout()

    def get_current_positions(self):


        return robinhood.account.build_holdings()

    def get_current_cash_position(self):


        return float(robinhood.profiles.load_account_profile(info="buying_power"))

    def has_sufficient_funds_available(self, amount_in_dollars):

        if not amount_in_dollars:
            return False

        available_funds = self.get_current_cash_position()

        return available_funds >= amount_in_dollars

    def get_current_market_price(self, ticker):

        if not ticker:
            return 0.00

        return float(robinhood.stocks.get_latest_price(ticker, includeExtendedHours=False)[0])

    def get_company_name_from_ticker(self, ticker):


        if not ticker:
            return ""

        return robinhood.stocks.get_name_by_symbol(ticker)

    def get_stock_history_dataframe(self, ticker, interval="day", time_span="year"):

        if (
            not ticker
            or interval not in {"5minute", "10minute", "hour", "day", "week"}
            or time_span not in {"day", "week", "month", "3month", "year", "5year"}
        ):
            return pd.DataFrame()

        stock_history = robinhood.stocks.get_stock_historicals(ticker, interval=interval, span=time_span)

        return pd.DataFrame(stock_history)

    def get_equity_in_position(self, ticker):


        portfolio = self.get_current_positions()

        if ticker in portfolio:
            position = portfolio[ticker]
            return float(position["equity"])

        return 0

    def has_sufficient_equity(self, ticker, amount_in_dollars):

        if not amount_in_dollars or amount_in_dollars <= 0:
            return False

        equity_in_position = self.get_equity_in_position(ticker)

        return equity_in_position >= amount_in_dollars

    def place_buy_order(self, ticker, amount_in_dollars):


        purchase_data = {}

        if not ticker or not amount_in_dollars:
            print("ERROR: Parameters cannot have null values.")
            return purchase_data

        if amount_in_dollars < 1:
            print("ERROR: A purchase cannot be made with less than $1.00 USD.")
            return purchase_data

        if self.has_sufficient_funds_available(amount_in_dollars):
            print(f"Buying ${amount_in_dollars} of {ticker}...")
            purchase_data.update(
                robinhood.orders.order_buy_fractional_by_price(
                    ticker,
                    amount_in_dollars,
                    timeInForce="gfd",
                    extendedHours=False,
                    jsonify=True,
                )
            )
            print(f"Successfully bought ${amount_in_dollars} of {ticker}.")

        return purchase_data

    def place_sell_order(self, ticker, amount_in_dollars):


        sale_data = {}

        if not ticker or not amount_in_dollars:
            print("ERROR: Parameters cannot have null values.")
            return sale_data

        if amount_in_dollars < 1:
            print("ERROR: A sale cannot be made with less than $1.00 USD.")
            return sale_data

        # Must have enough equity for the sale
        if self.has_sufficient_equity(ticker, amount_in_dollars):
            print(f"Selling ${amount_in_dollars} of {ticker}...")
            sale_data.update(
                robinhood.orders.order_sell_fractional_by_price(
                    ticker,
                    amount_in_dollars,
                    timeInForce="gfd",
                    extendedHours=False,
                    jsonify=True,
                )
            )
            print(f"Successfully sold ${amount_in_dollars} of {ticker}.")

        return sale_data

    def buy_with_available_funds(self, ticker):

        if not ticker:
            return {}

        available_funds = self.get_current_cash_position()

        return self.place_buy_order(ticker, available_funds)

    def sell_entire_position(self, ticker):


        if not ticker:
            return {}

        equity_in_position = self.get_equity_in_position(ticker)

        return self.place_sell_order(ticker, equity_in_position)

    def liquidate_portfolio(self):


        compiled_sale_information = []
        portfolio = self.get_current_positions()

        for ticker in portfolio.keys():
            sale_information = self.sell_entire_position(ticker)
            compiled_sale_information.append(sale_information)

        return compiled_sale_information

    def make_order_recommendation(self, ticker):

        return OrderType.HOLD_RECOMMENDATION

    def trade(self, ticker, amount_in_dollars):

        transaction_data = {}

        action = self.make_order_recommendation(ticker)

        if action == OrderType.BUY_RECOMMENDATION:
            purchase_details = self.place_buy_order(ticker, amount_in_dollars)
            transaction_data.update(purchase_details)

        elif action == OrderType.SELL_RECOMMENDATION:
            sale_details = self.place_sell_order(ticker, amount_in_dollars)
            transaction_data.update(sale_details)

        else:
            print(f"Conditions are not met for either a purchase or a sale of {ticker}.")

        return transaction_data
