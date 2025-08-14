import praw
import pandas as pd



reddit = praw.Reddit(
    client_id="Dd3-kNRSQDyWIg9AxM_p8Q",
    client_secret="####################################",
    user_agent="Comment Extraction (by u/Express_String_7640)",
)
df1_posts = pd.DataFrame(columns=["post_id", "title", "author", "score", "num_comments",
                                   "created_utc", "subreddit","post_url", "selftext"])

df2_comments = pd.DataFrame(columns=["comment_id", "author", "score",
                                    "created_utc", "parent_id", "link_id","body"])



posts_ids = []		# put this next time (travel) instead of AskReddit
for post in reddit.subreddit("travel").new(limit=60):
    posts_ids.append(post.id)
    row = [
        post.id,
        post.title,
        post.author,
        post.score,
        post.num_comments,
        post.created_utc,
        post.subreddit,
        post.url,
        post.selftext,
    ]
    df1_posts.loc[len(df1_posts)] = row

    
print("###################################################################")
for post_id in posts_ids:
    submission = reddit.submission(post_id)

# to not encounter MoreComments error
    submission.comments.replace_more(limit=0)
    for top_level_comment in submission.comments:
        row = [
            top_level_comment.id,
            top_level_comment.author,
            top_level_comment.score,
            top_level_comment.created_utc,
            top_level_comment.parent_id,
            top_level_comment.link_id,
            top_level_comment.body
        ]
        df2_comments.loc[len(df2_comments)] = row
        print("########################")

df1_posts_cols = ["post_id", "title", "author", "score", "num_comments",
                                   "created_utc", "subreddit","post_url", "selftext"]
df1_posts.to_csv("posts_travel.csv",index=False,columns=df1_posts_cols)

df2_comments_cols = ["comment_id", "author", "score",
                            "created_utc", "parent_id", "link_id","body"]
df2_comments.to_csv("comments_travel.csv", index=False, columns=df2_comments_cols)
        