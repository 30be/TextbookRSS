import os
from datetime import datetime, timedelta

import yaml
from feedgen.feed import FeedGenerator

# Get the current directory
feeds_directory = os.path.join(os.getcwd(), "feeds")


def create_feed(name, chapters):
    fg = FeedGenerator()
    fg.id(f"http://23.94.5.170/feeds/{name}")
    fg.title(name)
    fg.author(name="TextbookRSS", email="lykd@pm.me")
    fg.logo("http://23.94.5.170/feeds/TextbookRSS.png")
    fg.subtitle(f"Automatically generated RSS feed feed for {name} textbook")
    fg.link(href="http://23.94.5.170", rel="self")
    fg.language("en")
    for chapter in chapters:
        fe = fg.add_entry()
        fe.id(f"http://23.94.5.170/feeds/{name}/{chapter}")
        fe.link(href=f"http://23.94.5.170/feeds/{name}/{chapter}")
        fe.title(chapter)
        fe.description(f"Chapter {chapter} of {name}")
    return fg


def add_articles(book, amount):
    with open(os.path.join(feeds_directory, book, "unread_chapters.txt"), "a+") as f:
        f.seek(0)
        unread_chapters = [line.rstrip("\n") for line in f.readlines()]
    with open(os.path.join(feeds_directory, book, "read_chapters.txt"), "a+") as f:
        f.seek(0)
        read_chapters = [line.rstrip("\n") for line in f.readlines()]
    read_chapters.extend(unread_chapters[:amount])
    unread_chapters = unread_chapters[amount:]
    with open(os.path.join(feeds_directory, book, "unread_chapters.txt"), "w") as f:
        f.write("\n".join(unread_chapters))
    with open(os.path.join(feeds_directory, book, "read_chapters.txt"), "w") as f:
        f.write("\n".join(read_chapters))

    output = os.path.join(feeds_directory, book, "feed.rss")
    print(f"Updating feed for {book} to {read_chapters}")
    create_feed(book, read_chapters).rss_file(output)


defaults = {
    "last_updated": "2000-01-01",
    "articles_per_day": 1,
    "days_period": 1,
}


def merge_dicts(defaults, config):
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict) and isinstance(config[key], dict):
            merge_dicts(value, config[key])
    return config


def get_config(feed):
    if os.path.exists(os.path.join(feeds_directory, feed, "config.yaml")):
        with open(os.path.join(feeds_directory, feed, "config.yaml"), "r") as file:
            loaded_config = yaml.safe_load(file)
            return merge_dicts(defaults, loaded_config)
    return defaults


for feed in os.listdir(feeds_directory):
    config = get_config(feed)
    last_updated = datetime.fromisoformat(config["last_updated"])
    print(f"Last updated: {last_updated}")
    if datetime.now() > last_updated + (0.9 * timedelta(days=config["days_period"])):
        print(f"Updating {feed}")
        add_articles(feed, config["articles_per_day"])
    config["last_updated"] = datetime.now().isoformat()
    yaml.dump(config, open(os.path.join(feeds_directory, feed, "config.yaml"), "w"))
