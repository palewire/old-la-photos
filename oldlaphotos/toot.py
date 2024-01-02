import os
from pathlib import Path

import click
import requests
import pandas as pd
from mastodon import Mastodon
from rich import print

THIS_DIR = Path(__file__).parent.absolute()


@click.command()
def cli():
    """Post latest requests to Twitter."""
    # Get all photos
    csv_path = THIS_DIR / "photos.csv"
    df = pd.read_csv(csv_path).sort_values("id")
    print(f"Reading in {len(df)} photos")

    # Pull one randomly
    random_img = df.sample().iloc[0].to_dict()

    # Connect to Mastodon
    api = Mastodon(
        client_id=os.getenv("MASTODON_CLIENT_KEY"),
        client_secret=os.getenv("MASTODON_CLIENT_SECRET"),
        access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
        api_base_url="https://mastodon.palewi.re",
    )

    # Download the image
    image_url = f"https://lapl-photo-collection-bot.s3.us-west-2.amazonaws.com/media/{random_img['image']}"
    image_path = Path(f"./{random_img['image']}")
    download_url(image_url, image_path)

    # Upload the image
    print(f"Uploading {image_path}")
    alt_text = random_img["description"] or random_img["title"]
    if not alt_text or pd.isnull(alt_text):
        media_obj = api.media_post(image_path)
    else:
        media_obj = api.media_post(image_path, description=alt_text)
    image_path.unlink()

    # Post
    status = f"{random_img['title']} {random_img['link']}"
    print(f"Tooting {status}")
    status = api.status_post(status, media_ids=media_obj['id'])


def download_url(url: str, output_path: Path, timeout: int = 180):
    """Download the provided URL to the provided path."""
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


if __name__ == "__main__":
    cli()
