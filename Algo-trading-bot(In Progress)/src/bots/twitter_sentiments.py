import pandas as pd
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.bots.base_trade_bot import OrderType, TradeBot
from src.utilities import TwitterCredentials

MINIMUM_CONSENSUS_BUY_SCORE = 0.05
MINIMUM_CONSENSUS_SELL_SCORE = -0.05


class TradeBotTwitterSentiments(TradeBot):
    def __init__(self):


        super().__init__()


        twitter_credentials = TwitterCredentials()
        auth = tweepy.AppAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        self.twitter_api = tweepy.API(auth)


        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def retrieve_tweets(self, ticker, max_count=100):

        searched_tweets = []

        if not ticker:
            print("ERROR: param ticker cannot be a null value")
            return searched_tweets

        if max_count <= 0:
            print("ERROR: max_count must be a positive number.")
            return searched_tweets


        company_name = self.get_company_name_from_ticker(ticker)
        query = f"#{company_name} OR ${ticker}"


        public_tweets = tweepy.Cursor(
            self.twitter_api.search_tweets,
            q=query,
            lang="en",
            result_type="recent",
            tweet_mode="extended",
        ).items(max_count)


        searched_tweets = []

        for tweet in public_tweets:
            try:
                searched_tweets.append(tweet.retweeted_status.full_text)

            except AttributeError:
                searched_tweets.append(tweet.full_text)

        return searched_tweets

    def analyze_tweet_sentiments(self, tweets):


        if not tweets:
            print("ERROR: param tweets cannot be a null value")
            return 0

        column_names = ["tweet", "sentiment_score"]
        tweet_sentiments_df = pd.DataFrame(columns=column_names)

        for tweet in tweets:
            score = self.sentiment_analyzer.polarity_scores(tweet)["compound"]
            tweet_sentiment = {"tweet": tweet, "sentiment_score": score}
            tweet_sentiments_df = pd.concat(
                [tweet_sentiments_df, pd.DataFrame([tweet_sentiment])],
                ignore_index=True,
            )

        average_sentiment_score = tweet_sentiments_df["sentiment_score"].mean()

        return average_sentiment_score

    def make_order_recommendation(self, ticker):


        if not ticker:
            print("ERROR: param ticker cannot be a null value")
            return None

        public_tweets = self.retrieve_tweets(ticker)
        consensus_score = self.analyze_tweet_sentiments(public_tweets)

        if consensus_score >= MINIMUM_CONSENSUS_BUY_SCORE:
            return OrderType.BUY_RECOMMENDATION

        elif consensus_score <= MINIMUM_CONSENSUS_SELL_SCORE:
            return OrderType.SELL_RECOMMENDATION

        else:
            return OrderType.HOLD_RECOMMENDATION
