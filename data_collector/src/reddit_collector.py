"""Reddit Collector using praw sdk"""

import praw
from datetime import datetime

from src.database.queries import get_all_control_tickers
from src.database.inserts import (insert_author, insert_source,
                                  insert_submission, insert_comment,
                                  insert_ticker_mention)


class RedditCollector:
    """
    Reddit object that will handle all api
    authentication, calls and data formatting.
    """
    def __init__(self, client_id, client_secret,
                 user_agent, username, password):
        self.new_ticker_updates = 0
        self.ticker_control = get_all_control_tickers()
        print("Creating connection to Reddit...")
        self.reddit = praw.Reddit(client_id=client_id,
                                  client_secret=client_secret,
                                  user_agent=user_agent,
                                  username=username, password=password)

    def get_subreddit(self, subreddit_name):
        """
        Return reddit subreddit object.

        Args:
        :subreddit_name: name of subreddit -> r/{}.
        """
        print(f"Connecting to subreddit: r/{subreddit_name}...")
        return self.reddit.subreddit(subreddit_name)

    def get_submissions(self, subreddit_obj, subreddit_sorting,
                        top_sorting='all', limit=10):
        """
        Return submissions object from subreddit.

        Args:
        :subreddit_obj: praw subreddit object.
        :subreddit_sorting: string -> hot/new/top.
        :top_sorting: string when using top sorting -> all/year/month/day.
        :limit: int nr of submissions to collect.
        """
        subred = subreddit_obj.display_name
        print(f"Getting {limit} submissions from: r/{subred}/{subreddit_sorting}...")
        if subreddit_sorting == "hot":
            return subreddit_obj.hot(limit=limit)
        elif subreddit_sorting == "new":
            return subreddit_obj.new(limit=limit)
        elif subreddit_sorting == "top":
            return subreddit_obj.top(top_sorting, limit=limit)
        else:
            print(f"Subreddit sorting type not recognized: {subreddit_sorting}")
            raise ValueError

    def get_comments(self, submission_obj, limit=10):
        """
        Return list of comments objects from single submission object.

        Args:
        :submission_obj: praw single submission object.
        :limit: int nr of comments to collect.
        """
        # call for comments of submission
        print(f"Getting {limit} comments from submission: {submission_obj.id}")
        submission_obj.comments.replace_more(limit=limit)
        return submission_obj.comments.list()

    def convert_to_epoc_utc(self, timestamp):
        """Convert reddit timestamp to datetime object."""
        return datetime.fromtimestamp(int(timestamp))

    def get_submission_data(self, submission_obj):
        """
        Return target datapoints for single submission as dictionary.

        Args:
        :submission_obj: praw single submission object.
        """
        data = None
        try:
            data = {
                "submission_id": submission_obj.id,
                "timestamp": self.convert_to_epoc_utc(submission_obj.created_utc),
                "score": submission_obj.score,
                "nr_comments": submission_obj.num_comments,
                "author_id": submission_obj.author.id,
                "source": submission_obj.subreddit.name
            }
        except Exception as error:
            print(f"Couldn't access submission data: {error}. On to the next one...")
        return data

    def get_comment_data(self, comment_obj):
        """
        Return target datapoints for single comment as dictionary.

        Args:
        :comment_obj: praw single comment object.
        """
        data = None
        try:
            data = {
                "comment_id": comment_obj.id,
                "timestamp": self.convert_to_epoc_utc(comment_obj.created_utc),
                "score": comment_obj.score,
                "submission_id": comment_obj.submission.id,
                "author_id": comment_obj.author.id,
            }
        except Exception as error:
            print(f"Couldn't access comment data: {error}. On to the next one...")
        return data

    def filter_valid_tickers(self, comment_obj):
        """
        Check if comment continas valid tickers.
        Return lists with valid tickers.

        Args:
        :comment_obj: praw single comment object.
        """
        # combine title and body split by whitespace
        words = comment_obj.body.split()
        # cashtags
        possible_tickers = [w for w in words if w.startswith('$')]
        # most ticker 1-5 characters
        possible_tickers.extend([w for w in words if len(w) > 1 and len(w) < 6])
        # remove cashtags
        clean_tickers = [w.strip('$') for w in possible_tickers]
        # compare against control table
        valid_tickers = [c for c in clean_tickers if c in self.ticker_control]
        # get unique tickers
        unique_tickers = list(set(valid_tickers))
        return unique_tickers

    def get_comments_with_tickers(self, comments_list, submission_data):
        """
        Filter comments that mentions tickers.
        Return list of dictionary with comment data.

        Args:
        :comments_list: List of comment objects.
        :submission_data: dictionary with submission data
        """
        # filter each comment for ticker mentions
        ticker_comments = list()
        for i, comment in enumerate(comments_list):
            tickers = self.filter_valid_tickers(comment)
            # if tickers mentioned in text, get comment data
            if len(tickers) > 0:
                comment_data = self.get_comment_data(comment)

                # if comment data available, add tickers to dict and add to result list
                if comment_data is not None:
                    comment_data["tickers"] = tickers
                    ticker_comments.append(comment_data)

            # flush data to db when extracted 100 ticker comments, reset result list
            if len(ticker_comments) > 99:
                self.insert_new_data_to_db(ticker_comments, submission_data)
                ticker_comments = list()

            # print number of comments that been reviewed
            if i+1 % 100 == 0:
                print(f"Numbers of comments from submission assessed: {i}")

        # write any remaining ticker comments
        if len(ticker_comments) > 0:
            self.insert_new_data_to_db(ticker_comments, submission_data)

    def insert_new_data_to_db(self, ticker_comments, submission_data):
        """
        Insert new ticker mention data to database.

        Args:
        :ticker_comments: list of dictionaries with comment data
        :submission_data: dictionary with submission data
        """
        # submission related data
        insert_source(submission_data["source"])        # insert source table
        insert_author(submission_data["author_id"])     # insert author table
        insert_submission(**submission_data)            # insert submission table

        # for each comment
        updates = 0
        for comment_data in ticker_comments:
            insert_author(comment_data["author_id"])       # insert author
            comment_tickers = comment_data.pop("tickers")  # drop tickers from comment data
            insert_comment(**comment_data)                 # insert comment table

            # for each ticker in comment, insert new ticker mentions
            for ticker in comment_tickers:
                insert_ticker_mention(ticker, comment_data["comment_id"])
                updates += 1

        # print results
        print(f"Number of new ticker mentions writen to db: {updates}")

    def get_new_data(self, subreddit_name, subreddit_params, comment_params):
        """Get new comments from subreddit."""
        subreddit = self.get_subreddit(subreddit_name)
        submissions = self.get_submissions(subreddit, **subreddit_params)
        for i, submission in enumerate(submissions):
            submission_data = self.get_submission_data(submission)

            # if submission data available, get comments from submission
            if submission_data is not None:
                print(f"Extracting comments from submission: {submission_data['submission_id']}")
                comments = self.get_comments(submission, **comment_params)
                self.get_comments_with_tickers(comments, submission_data)

        # TODO!
        # How long should extraction for single submission run?
        # When number of new comments extraction is 0 -> go to next submission
        # Skip submission in table

        # TODO!
        # How to control all comments in submission have been extracted?
        # Get nr_comments from submission and track comments extraced comments until end reached?
        # Skip comments in table

