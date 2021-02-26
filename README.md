# Don't Believe the Hype - r/wallstreetbets Ticker Alert

This app collects and analyze data from the subreddit [www.reddit.com/r/wallstreetbets/](https://www.reddit.com/r/wallstreetbets/), a forum or subreddit on the social news website Reddit. The subreddit has gained a lot of popularity since the [GameStop short squeeze](https://en.wikipedia.org/wiki/GameStop_short_squeeze). Due to the forums ability to impact the market it could be of interest to know what finanical instruments, also known as tickers, is currently being discussed to anticipate increased volatility.

The ticker hype aleart dashboard consist of 3 different docker containers:

1. Postgres Database
2. Data-Collector
    * Data collection from [IEX Cloud API](https://iexcloud.io/) to get offical tickers. Using the [IEX Cloud Python SDK](https://pypi.org/project/iexfinance/).
    * Data collection from [Reddit API](https://www.reddit.com/r/wallstreetbets/) to get all tickers mentioned in comments. Using the [PRAW: The Python Reddit API Wrapper](https://praw.readthedocs.io/en/latest/index.html)
    * ETL process to filter out comments that contain offical tickers. 
    * Write data to Postgresql database.
3. Dashboard
    * Plotly Dash dashboard to show the most mentioned tickers.

<br/><br/>

## **Installation Guide**

### Requirements
The following utilities are prerequisites to installing the app:

- git
- Docker
- User accounts for both IEXCloud and Reddit (both available for free)


### 1. Clone Repository
Installation of the app requires cloning of the core repository. This uses Git. This will bring down all the necessary files and enter the app folder.
```
git clone https://github.com/vstiern/wsb-hype-alert.git
cd wsb-hype-alert
```

### 2. Install Docker
Install docker for your platform [Docker](https://docs.docker.com/get-docker/).


### 3. Get access to APIs
This app uses two apis. To get access to these services the user need to create a personal account. The client values/tokens need to be entered into the file `config.ini` under the correct header.

- #### Reddit 
1. Login to [Reddit](https://reddit.com).
2. Go to [Reddit Apps](https://reddit.com/prefs/apps/).
3. Select “script” as the type of app.
4. Name the app and give it a description.
5. Set the redirect url to be http://localhost:8080.
6. Enter the values of **client_id** and **client_secret** to the file `config.ini` under the [reddit] header. Also enter username and password for the users reddit account in this section.

<img src="./imgs/reddit_app.png" height=300, width="300">
<img src="./imgs/reddit_token.png" height=300, width="500">


- #### IEX Cloud
1. Login to [IEX Cloud](https://reddit.com).
2. Go to [API Tokens](https://iexcloud.io/console/tokens)
3. Enter the value of **PUBLISHABLE** to the file `config.ini` under the [iexfinance] header.
<img src="./imgs/iex_token.png" height=300, width="750">
<br/><br/>

### 4. Enter API keys to config
Open the data-collector config file `data_collector/config.ini` and fill in the respective fields 
from both IEX Cloud and Reddit.

<br/><br/>

## **Start application**
Finally, to start the app run the following command in the project directory. When all containers are up and running go to the dashboard url: http://127.0.0.1:8050/.
```
docker-compose up
```


## **The Dashboard**
The dashboard the shows the top 10 most mentioned tickers. The user can select what tickers to include and whether to see the number of times a ticker has been mentioned (count) or the aggregated score (upvotes - downvotes) for all the comments that mentions the ticker. By hovering over or clicking on a specific ticker in the top graph the graph below will show a breakdown by date and hour for the selected feature - count or score. Double click to reset the graph from zoom in. The dashboard will show new data from the subreddit every 5min. The new data will only be visable if its part of the top 10 most mentioned tickers.

<img src="./imgs/dashboard.png" width="500">

## **Notice**
The app is an early proof of concept and might not be very stable. Here are some things to keep in mind at this stage.

#### Cold Start
Notice that the first time using the app the there will not be any reddit data collected. The dashboard will pull new data from the database every 2min. The data-collector runs continously and more data will appear. The data stored in the database is saved loccally and can be accessed again after the app been closed and opened.

#### Reddit API
The rate of comment extraction might vary depending on usage of api account. The PRAW package currently handles all rate limits currently. Optimization to be improved. 

#### Reddit Data Extraction
The app only extracts mentioned tickers from comments and not the original submission. The data comes from the page sorting `hot`, which displays the most commented and upvoted submissions. The app extracts all comments from the current top submission. The app only counts unique ticker mention per comment.


## **Development**
This app has a lot of more potential and the following features are in the development pipeline:
1. Price data - Show intraday price data against count/score. This would allow the user to see how the market price is moving in accordance with the forums activity.
2. Sentiment analysis - Rather than just observing the number of comments that mentions a ticker, it would be interesting to analyze the context and to see whether the forum has a positive or negative sentiment to the price of a ticker. 
3. Use more sources - what tickers have been mentioned on other subreddits, Twitter and forums. The more sources we can analyze, the more hype and risk can be mitigated. 