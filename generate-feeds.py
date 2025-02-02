import os
from datetime import datetime, timedelta

import yaml
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests
import re

# Get the current directory
feeds_directory = os.path.join(os.getcwd(), "feeds")


def is_link(string):
    return re.match(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", string
    )  # http[s]://[www.]google.com


def create_feed(name, chapters):
    fg = FeedGenerator()
    fg.id(f"http://23.94.5.170/feeds/{name}")
    fg.title(name)
    fg.author(name="TextbookRSS", email="lykd@pm.me")
    fg.logo("http://23.94.5.170/feeds/TextbookRSS.png")
    fg.subtitle(f"Automatically generated RSS feed feed for {name} textbook")
    fg.link(href="http://23.94.5.170", rel="self")
    fg.language("en")
    links = 0
    for chapter in chapters:
        fe = fg.add_entry()
        fe.id(chapter)

        if is_link(chapter):
            link = chapter
            links += 1
        else:
            link = f"http://23.94.5.170/feeds/{name}/{chapter}"
        fe.link(href=link)
        chapter_name = BeautifulSoup(requests.get(link).content, "html.parser").title
        fe.title(chapter_name)
        fe.description(f"Chapter {chapter_name} of {name}: {chapter}")
    print(f"Created {len(chapters)} chapters for {name}, {links} of which are external links")
    return fg


def add_articles(book, amount):
    with open(os.path.join(feeds_directory, book, "unread_chapters.txt"), "r") as f:
        unread_chapters = [line.rstrip("\n") for line in f.readlines()]
    with open(os.path.join(feeds_directory, book, "read_chapters.txt"), "r") as f:
        read_chapters = [line.rstrip("\n") for line in f.readlines()]
    read_chapters += unread_chapters[:amount]
    unread_chapters = unread_chapters[amount:]
    with open(os.path.join(feeds_directory, book, "unread_chapters.txt"), "w") as f:
        f.write("\n".join(unread_chapters))
    with open(os.path.join(feeds_directory, book, "read_chapters.txt"), "w") as f:
        f.write("\n".join(read_chapters))

    output_file = os.path.join(feeds_directory, book, "feed.rss")
    print(f"Added {read_chapters[-amount:]}")
    create_feed(book, read_chapters).rss_file(output_file)


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


def set_config(feed, config):
    with open(os.path.join(feeds_directory, feed, "config.yaml"), "w") as f:
        yaml.dump(config, f)


for feed in os.listdir(feeds_directory):
    config = get_config(feed)
    last_updated = datetime.fromisoformat(config["last_updated"])
    if datetime.now() > last_updated + (0.9 * timedelta(days=config["days_period"])):
        config["last_updated"] = datetime.now().isoformat()
        add_articles(feed, config["articles_per_day"])
    else:
        print(f"Last updated {feed}: {last_updated}")
    set_config(feed, config)
