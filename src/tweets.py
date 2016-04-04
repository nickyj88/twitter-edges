"""
Goals:
1) Ingest a tweet and extract the hashtags and the created_at values.
2)  Check if the tweet is within 60 seconds of the newest tweet.
      - If it is, append the tweet to the list of tweets.
      - If it is not, write the most recent computation to the output file.
3)  Reorder the tweets.
4)  Check to see if the oldest tweet in the list is within 60 seconds of the newest tweet.
      - If it is not, remove it from the list.
5) Keep checking until the oldest tweet is within 6 seconds.
6) Make a graph of the hashtag values.
7) Count the shared edges for each hashtag.
8) Write that number to the output file and return a new line.
"""

# The imports we will need
from datetime import timedelta
from datetime import datetime
import json
import sys

# Use a time delta object to evaluate whether tweets should be added to the graph.
delta = datetime.timedelta(seconds=60)

# Set the output destination file
output_file = open('./output.txt', 'w')

def run_tweets(tweet_input):
  # Set a last value variable that we will update.
  # If the newest tweet does not change the graph, we will default to this
  # Instead of going through all the logic.
  last_result = ''

  # Read in the tweet input data and make a list of dicts.
  tweets = [json.loads(tweet.strip()) for tweet in tweet_input]
  
  # Set our initial list of tweets for calculation
  tweet_list = []

  # Bring in the next tweet from the input data
  # Remove it from the list so we don't check it again.
  new_tweet = {tweet_input[-1]["created_at"]: tweet_input[-1]["hashtags"]}
  tweet_input.pop()
  
  # Run all checks and compute the tweets
  for tweet in tweets:
    check_and_compute_new_tweet(tweet_list, tweet)


# Function to convert the timestamp of the tweet into a datetime object.
def convert_created_at(tweet):
  return datetime.strptime(tweet["created_at"],'%a %b %d %H:%M:%S +0000 %Y')

# Use a function to access the first element of our created_at, hashtag tuples.
# This will allow us to sort the current_tweet list based on the created_at.
def get_date_key(item):
  return item[0]

# Check to see if the new tweet was created within 60 seconds of the newest tweet in the list.
# Returns boolean.
def check_tweet(tweet_list, new_tweet, delta=delta):
  if get_date_key(tweet_list[-1]) > new_tweet["created_at"] - delta:
    return True
  # If the tweet does not make it onto the list, just use the last result
  else:
    return False

def compute_graph(tweet_list):
  # Create a list of lists to collect our hashtags.
  hashtag_sets = []
  for tweet in tweet_list:
    # Only include tweets with 2 or more hashtags in the computation.
    if len(tweet[1]) > 1:
      hashtag_sets.append(tweet[1])
    else:
      pass

  # Use a dictionary to track how many edges there are per node.
  # The key is each unique hashtag.
  # The value is a list of each hashtag with which it can be found in the same tweet.
  hashtag_graph = {}

  # Start by iterating through each set of hashtags.
  for hashtag_list in hashtag_sets:
    # For each hashtag found, update the respective value in the hashtag graph dictionary.
    for hashtag in hashtag_list:
      if hashtag in hashtag_graph.keys():
        hashtag_graph[hashtag] = hashtag_graph[hashtag] + [hashtag for hashtag in hashtag_list]
      else:
        hashtag_graph[hashtag] = [hashtag for hashtag in hashtag_list]
  
  # Simplest way to compute the mean is to make a list of the lengths of each hashtag's edge list.
  edge_counts = []
  
  # Go through the key, value pairs to find the edges.
  for k, v in hashtag_graph.items():
    # Converting to a set and then back to a list is a quick way to get rid of duplicate hashtags.
    v = list(set(v))

    # Make sure to drop the key hashtag itself from the list.
    # If for any reason the hashtag does not end up in the list, use a try/except to handle popping a value that doesn't exist.
    try:
      v.pop(v.index(k))
    except:
      pass
    
    # Add the edge counts
    edge_counts.append(len(v))

  # Return the average edges per node
  return sum(edge_counts)/len(edge_counts)

# Function to call on a new tweet
def check_and_compute_new_tweet(tweet_list, new_tweet, delta=delta, output=output_file):

  # Check the new tweet and if it fits the timeline append it to the list and compute the result.
  if check_tweet(tweet_list, new_tweet) == False:
    # Add the new tweet to the list
    tweet_list.append([new_tweet["created_at"], new_tweet["hashtags"]])
    
    #Order the list of tweets so that we know most recent one is the last one.
    tweet_list = sorted(tweet_list, key=get_key)
    
    # Check each tweet in case the newest addition would eliminate them from the graph.
    for tweet in tweet_list:
      if tweet_list[0][0] < tweet_list[-1][0] - delta:
        tweet_list.pop(tweet_list.index(tweet))    

    result = compute_graph(tweet_list)
    output.write(str(result) + '\n')
    last_result = result

  # Otherwise, 
  else:
    output.write(str(last_value))

if __name__ == "__main__":
  run_tweets(sys.stdin)
  tweet_input.close()
  output_file.close()