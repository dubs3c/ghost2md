import argparse
from datetime import datetime
import json
from pathlib import Path
import sys


def get_post_tags(post_id: str, posts_tags: list) -> list:
    """ Get associated tags by post_id """
    post_tags = list(filter(lambda tag: tag["post_id"] == post_id, posts_tags))
    return list(map(lambda tag: tag["tag_id"], post_tags))


def go(json_file: str, output_directory: str) -> None:

    data = ""
    try:
        with open(json_file, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
    except IOError as err:
        print(f"[-] Something went wrong when reading the json file, error: {err}")
        sys.exit(1)

    try:
        t = json.loads(data)
    except Exception as e:
        print(f"[-] Error loading json backup file into json format: {e}")
        sys.exit(1)

    newline = "\n"

    for x in t.get("db"):
        posts = x["data"]["posts"]
        tags = list(map(lambda tag: {"id": tag.get("id"), "name": tag.get("name"), "slug": tag.get("slug")}, x["data"]["tags"]))
        posts_tags = x["data"]["posts_tags"]

        for post in posts:
            id = post.get("id")
            title = post.get("title")
            created = datetime.strptime(post.get("created_at"), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            feature_image = ""
            if post.get("feature_image"):
                feature_image = Path("../thumbnails/", Path(post.get("feature_image")).name)
            slug = post.get("slug")
            content = json.loads(post.get("mobiledoc")).get("cards")[0][1].get("markdown")

            # Get all tag IDs used by this post
            tag_ids = get_post_tags(id, posts_tags)
            used_tags = list(filter(lambda tag: tag["id"] in tag_ids, tags))
        
            output = f"""---
date: {created}
title: '{title}'
template: post
thumbnail: '{feature_image}'
slug: {slug}
categories:
{newline.join(list(map(lambda tag: " - " + tag["name"] , used_tags)))}
tags:
{newline.join(list(map(lambda tag: " - " + tag["name"] , used_tags)))}
---

{content}

"""

            try:
                with open(f"{output_directory}/{created}-{slug}.md", "w+", encoding="utf-8") as f:
                    f.write(output)
            except IOError as err:
                print(f"[-] Something went wrong when writing markdown file to output directory, error: {err}")
                sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ghost2md",
        description=f"Convert Ghost articles to markdown files.",
    )
    parser.add_argument(
        "--json",
        action="store",
        dest="json",
        required=True,
        help="The Ghost json backup file",
    )
    parser.add_argument(
        "--output",
        action="store",
        dest="output",
        required=True,
        help="Where to store all converted markdown files",
    )
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        quit()
    
    json = args.json
    output_directory = args.output

    if not Path(json).exists():
        print(f"[-] The file '{json}' does not exist.")
        sys.exit(1)

    if not Path(output_directory).exists():
        print(f"[-] The output directory '{output_directory}' does not exist, please create it first.")
        sys.exit(1)

    go(json, output_directory)