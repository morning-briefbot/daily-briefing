#!/usr/bin/env python3
"""Update docs/episodes.json and docs/feed.xml after a release is published.

Enclosure URLs use the deterministic GitHub release-asset pattern:
https://github.com/OWNER/REPO/releases/download/TAG/episode.mp3
"""
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape

REPO = os.environ["GITHUB_REPOSITORY"]  # e.g. mike/wsj-daily-brief
OWNER = REPO.split("/")[0]
SHOW_NAME = os.getenv("SHOW_NAME", "Morning Market Brief")
KEEP = int(os.getenv("KEEP_EPISODES", "30"))
PAGES_URL = f"https://{OWNER}.github.io/{REPO.split('/')[1]}"

DOCS = Path("docs")
DOCS.mkdir(exist_ok=True)
EP_FILE = DOCS / "episodes.json"

meta = json.loads(Path("out/meta.json").read_text())
episodes = json.loads(EP_FILE.read_text()) if EP_FILE.exists() else []
episodes = [e for e in episodes if e["tag"] != meta["tag"]]
episodes.insert(0, meta)
pruned_tags = [e["tag"] for e in episodes[KEEP:]]
episodes = episodes[:KEEP]
EP_FILE.write_text(json.dumps(episodes, indent=2))

items = ""
for e in episodes:
    url = f"https://github.com/{REPO}/releases/download/{e['tag']}/episode.mp3"
    items += f"""
  <item>
    <title>{escape(e['title'])}</title>
    <description>{escape(e['description'])}</description>
    <pubDate>{e['pub_date']}</pubDate>
    <guid isPermaLink="false">{e['tag']}</guid>
    <enclosure url="{url}" length="{e['size_bytes']}" type="audio/mpeg"/>
    <itunes:duration>{e['duration_seconds']}</itunes:duration>
  </item>"""

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
<channel>
  <title>{escape(SHOW_NAME)}</title>
  <link>{PAGES_URL}</link>
  <language>en-us</language>
  <description>Your daily AI-generated business news rundown, ready by 5am.</description>
  <itunes:author>{escape(OWNER)}</itunes:author>
  <itunes:explicit>false</itunes:explicit>{items}
</channel>
</rss>
"""
(DOCS / "feed.xml").write_text(feed)
print(f"Feed updated: {len(episodes)} episodes -> {PAGES_URL}/feed.xml")

# Tags older than KEEP -> the workflow deletes these releases
Path("out/prune_tags.txt").write_text("\n".join(pruned_tags))
