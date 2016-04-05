# Goals:
# 1) Ingest a tweet and extract the hashtags and the created_at values.
# 2)  Check if the tweet is within 60 seconds of the newest tweet.
#       - If it is, append the tweet to the list of tweets.
#       - If it is not, write the most recent computation to the output file.
# 3)  Reorder the tweets.
# 4)  Check to see if the oldest tweet in the list is within 60 seconds of the newest tweet.
#       - If it is not, remove it from the list.
# 5) Keep checking until the oldest tweet is within 6 seconds.
# 6) Make a graph of the hashtag values.
# 7) Count the shared edges for each hashtag.
# 8) Write that number to the output file and return a new line.


# The imports we will need
from datetime import timedelta
from datetime import datetime
import json
import ast
import pdb 
import sys

delta = timedelta(seconds=60)

def run_tweets(tweet_input, tweet_output):
  # Set a last value variable that we will update.
  # If the newest tweet does not change the graph, we will default to this
  # Instead of going through all the logic.
  last_avg_edge_count = 0.0

  # Read in the tweet input data and make a list of dicts.
  with open(tweet_input, 'r') as input_file:
    tweets = [json.loads(tweet.strip()) for tweet in input_file]
  
  # Remove all rate limit dictionaries from the list.
  for tweet in tweets:
    if "limit" in tweet.keys():
      tweets.pop(tweets.index(tweet))

  # Set our initial list of tweets for computation
  tweet_list = []  

  # Create a list of computations to write to the output file
  results_list = []

  # Run all checks and compute the tweet
  for tweet in tweets:
    new_tweet = {
                  "timestamp": convert_created_at(tweet["created_at"]),
                  "tags": format_hashtags(tweet["entities"]["hashtags"])
                }
    avg_edge_count = check_and_compute_new_tweet(tweet_list, new_tweet)
    if avg_edge_count == None:
      results_list.append(last_avg_edge_count)
    else:
      results_list.append(avg_edge_count)
      last_avg_edge_count = avg_edge_count
  # Write results to the output file
  with open(tweet_output, 'w') as output_file:
    for result in results_list:
      output_file.write(str(result) + "\n")

# Function takes in the hashtag value and returns a list of the tags.
def format_hashtags(hash_string):
  hash_list = [item["text"] for item in hash_string]
  return hash_list

# Function to call on a new tweet
def check_and_compute_new_tweet(tweet_list, new_tweet, delta=delta):

  # Check the new tweet and if it fits the timeline append it to the list and compute the result.
  if is_tweet_within_window(tweet_list, new_tweet):
    # Add the new tweet to the list
    tweet_list.append(new_tweet)
    #Order the list of tweets so that we know most recent one is the last one.
    tweet_list = sorted(tweet_list, key=(lambda t: t["timestamp"]))
    # tweet_list = sorted(tweet_list, key=get_date_key)
    
    # Check each tweet in case the newest addition would eliminate them from the graph.
    newest_timestamp = tweet_list[-1]["timestamp"]
    tweet_list = list(filter(lambda x: x["timestamp"] > newest_timestamp - delta, tweet_list))

    result = compute_graph(tweet_list)
    last_result = result

    return result
  # If the graph would remain unchanged, we'll return none, which will return the last result
  else:
    return None

# Check to see if the new tweet was created within 60 seconds of the newest tweet in the list.
# Returns boolean.
def is_tweet_within_window(tweet_list, new_tweet, delta=delta):
  if len(tweet_list) == 0 or  new_tweet["timestamp"] > tweet_list[-1]["timestamp"] - delta:
    return True
  # If the tweet does not make it onto the list, just use the last result
  else:
    return False

# Function to convert the timestamp of the tweet into a datetime object.
def convert_created_at(created_at):
  return datetime.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y')

def compute_graph(tweet_list):
  # Create a list of lists to collect our hashtags.
  hashtag_sets = []
  for tweet in tweet_list:
    # Only include tweets with 2 or more hashtags in the graph.
    if len(tweet["tags"]) > 1:
      hashtag_sets.append(tweet["tags"])
    else:
      pass
  # Use a dictionary to track how many edges there are per node.
  # The key is each unique hashtag.
  # The value is a list of each hashtag with which it can be found in the same tweet.
  hashtag_graph = {}

  # Start by iterating through each set of hashtags.
  for hashtag_set in hashtag_sets:
    # For each hashtag found, update the respective value in the hashtag graph dictionary.
    for hashtag in hashtag_set:
      if hashtag in hashtag_graph.keys():
        hashtag_graph[hashtag] = hashtag_graph[hashtag] + [hashtag for hashtag in hashtag_set]
      else:
        hashtag_graph[hashtag] = [hashtag for hashtag in hashtag_set]
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
      print("Error: Key hashtag not present")
    # Add the edge counts
    edge_counts.append(len(v))
  # Return the average edges per node
  return float(sum(edge_counts))/len(edge_counts)


if __name__ == "__main__":
  run_tweets(sys.argv[1], sys.argv[2])
  