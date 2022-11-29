import os
from pathlib import Path

import click
import pandas as pd
import twitter
from rich import print

THIS_DIR = Path(__file__).parent.absolute()


@click.command()
def cli():
    """Post latest requests to Twitter."""
    # Get all photos
    csv_path = THIS_DIR / "photos.csv"
    df = pd.read_csv(csv_path)
    print(f"Reading in {len(df)} photos")

    # Filter down to the untweeted
    untweeted_df = df[pd.isnull(df.tweet_id)]
    print(f"{len(untweeted_df)} photos still untweeted")

    # Pull one randomly
    random_tweet = untweeted_df.sample().iloc[0].to_dict()

    # Connect to Twitter
    api = twitter.Api(
        consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
        consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
        access_token_key=os.getenv("TWITTER_ACCESS_TOKEN_KEY"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    )

    # Upload the image
    image_url = f"https://lapl-photo-collection-bot.s3.us-west-2.amazonaws.com/media/{random_tweet['image']}"
    print(f"Uploading {image_url}")
    media_obj = api.UploadMediaSimple(image_url)

    # Annotate the image with alt text
    alt_text = random_tweet["description"] or random_tweet["title"]
    api.PostMediaMetadata(media_obj, alt_text)

    # Post to Twitter
    message = f"{random_tweet['title']} {random_tweet['link']}"
    print(f"Tweeting {message}")
    status = api.PostUpdate(message, media=media_obj)

    # Save the tweet id
    df.loc[df.id == random_tweet["id"], "tweet_id"] = status.id
    print("Writing CSV back out")
    df.to_csv(csv_path, index=False)


if __name__ == "__main__":
    cli()
