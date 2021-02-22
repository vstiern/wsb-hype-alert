"""Reddit API using praw"""

import praw
import requests
import pandas as pd
from configparser import ConfigParser

from src.db_functions import (get_all_control_tickers, insert_ticker_mentions, 
                              get_all_mention_ids, get_most_recent_submission)


class RedditCollector:
    """Reddit object that will handle all api authentication, calls and data formatting."""
    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.new_ticker_updates = 0
        self.ticker_control = get_all_control_tickers()
        self.current_mention_ids = get_all_mention_ids()
        self.reddit = praw.Reddit(client_id = self.client_id, client_secret = self.client_secret, 
                                  user_agent = self.user_agent, username=username, password=password)

    def update_new_data(self, subreddit, submission_limit, comment_limit):
        """Get new submissions posted after most recent id available in db."""
        print(f"Collecting new data submissions from: r/{subreddit}/new...")
        most_recent_submission = get_most_recent_submission()
        submissions = self.reddit.subreddit(subreddit).new(limit=submission_limit, 
                                                           params={"after": most_recent_submission})
        # get submissions and comments that contain valid tickers
        ticker_submissions = self.control_new_ticker_data(submissions, comment_limit)
        updates = 0
        for row in ticker_submissions:
            updates += insert_ticker_mentions(**row)
        print(f"New data inserted from r/{subreddit}/new. New ticker mentions added: {updates}")

    def update_data(self, subreddit, page_sorting, submission_limit, comment_limit):
        """Get new data from subreddit"""
        # get submission as per page sorting
        print(f"Collecting new data submissions from: r/{subreddit}/{page_sorting}...")
        if page_sorting == 'hot':
            submissions = self.reddit.subreddit(subreddit).hot(limit=submission_limit)
        elif page_sorting == 'new':
            submissions = self.reddit.subreddit(subreddit).new(limit=submission_limit)
        else:
            print(f"Subreddit page sorting type not recognized: {page_sorting}") 
            raise ValueError
        
        # get submissions and comments that contain valid tickers
        ticker_submissions = self.control_new_ticker_data(submissions, comment_limit)
        updates = 0
        for row in ticker_submissions:
            updates += insert_ticker_mentions(**row)
        print(f"New data inserted from r/{subreddit}/{page_sorting}. New ticker mentions added: {updates}")

    def control_new_ticker_data(self, submissions, comment_limit):
        """Iterate through comments in submissions for ticker mentions"""
        new_ticker_mentions = list()
        print(f"Updating new ticker mentions...")
        for submission in submissions:
            if not submission.stickied: 
                submission.comments.replace_more(limit=comment_limit)                                # get comments for submission
                for comment in submission.comments.list():
                    try:
                        tickers = self.filter_valid_tickers(comment)                           
                        new_mention = self.filter_new_ticker_mentions(submission, tickers, comment)
                        if new_mention is not None:
                            new_ticker_mentions.append(new_mention) 
                            if self.new_ticker_updates % 50 == 0:                                               
                                print(f"Updating new ticker mentions. Current updates: {self.new_ticker_updates}")
                    except Exception as e:
                        print(f"Couldn't assess comment. Error: {e}")
                        continue
        return new_ticker_mentions

    def filter_valid_tickers(self, comment):
        """Check if comment continas valid tickers. Return lists with valid tickers."""
        words = comment.body.split()                                                   # combine title and body split by whitespace
        possible_tickers = [w for w in words if w.startswith('$')]                     # cashtags
        possible_tickers.extend([w for w in words if len(w) > 1 and len(w) < 6])       # most ticker 1-5 characters
        clean_tickers = [w.strip('$') for w in possible_tickers]                       # remove cashtags 
        valid_tickers = [c for c in clean_tickers if c in self.ticker_control]         # compare against control table
        unique_tickers = list(set(valid_tickers))
        return unique_tickers

    def filter_new_ticker_mentions(self, submission, tickers, comment):
        """Check that new tickers not already in db and return relevant data."""
        for ticker in tickers:                                                          # for each ticker in comment
            data_dict = self.get_data_dictionary(submission, comment, ticker)           # get datapoints for comment
            if data_dict["mention_id"] not in self.current_mention_ids:                 # control mention_id not already in db
                self.new_ticker_updates += 1                                            # update counter 
                return data_dict                                                        
            else:
                return None

    def get_data_dictionary(self, submission, comment, ticker):
        """Get dictionary with all key datapoints from comment."""
        data = {
            "mention_id": comment.id + "|" + ticker,
            "submission_id": submission.id,
            "submission_timestamp": submission.created_utc,
            "comment_id": comment.id,
            "author_id": comment.author.name,
            "timestamp": comment.created_utc, 
            "score": comment.score,
            "source": comment.subreddit.name,
            "ticker": ticker
        }
        return data

    
        
    