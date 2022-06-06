# Twitter statistics - Fun with Kusto!

## Installation
### Twitter setup
1. Go to https://developer.twitter.com/ and create your own app.
2. From the 'Keys and tokens' page, under Authentication Tokens, copy your `Bearer Token`.
3. Add an environment variable to where you're running your code, named `TwitterToken` and give it that copied value.
4. Choose a Twitter username to query (it doesn't have to be yourself!) and put it in the `USER_ALIAS` field in main.py

### Kusto setup
5. Go to https://dataexplorer.azure.com/freecluster/ and create yourself a free Kusto cluster.
6. Inside it, create a database called `FollowerData`.
7. Then, go to "My Cluster (Preview)" and copy out the "Cluster URI" and "Data ingestion URI" values to `kusto_handler.py` (under KUSTO_URI, KUSTO_INGEST_URI)
8. In `Kusto-commands.txt` you'll find control commands to create four tables: Users, Follows, Tweets, Likes. Copy those.
9. In the Kusto website, go to "Query", paste those commands, and run them (one by one).

## Getting the data
10. Run `main.py`; it will start outputting messages as it queries Twitter and ingests into Kusto. Note that you may get rate-limited in some of these API calls; code will automatically sleep and retry until it finishes querying.
11. You can get more data on other users as well, and use it to cross-reference with yours.

## Query the data
12. To query, you can simply play with the data however you wish in the Query tab. Kusto has a rich KQL language; you can also join between tables. Refer to Kusto docs for more reference. 

## Visualize the data 
13. In Kusto website, go to "Dashboards (Preview)".
14. Once you have your queries, you can add tiles as you wish.
15. `Kusto-commands.txt` contains some suggested queries (you'll still need to visualize those when you build the tile).

## Notes
16. The current code only queries up to your most recent 3200 tweets. It's a Twitter API limitation that can be extended (by adding time filters on the main query), but does not exist in current version.
