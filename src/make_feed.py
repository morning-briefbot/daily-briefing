#!/usr/bin/env python3
"""Build the podcast site (feed.xml + episodes/) for GitHub Pages.

Runs after generate_episode.py. Expects:
  out/episode.mp3, out/meta.json  - today's episode
  site/                           - previous site contents (may be empty on first run)
Updates in site/: episodes/<tag>.mp3, episodes.json, feed.xml
"""
import json
import os
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

REPO = os.environ["GITHUB_REPOSITORY"]  # e.g. morning-briefbot/daily-briefing
OWNER, NAME = REPO.split("/")
SHOW_NAME = os.getenv("SHOW_NAME", "Morning Market Brief")
KEEP = int(os.getenv("KEEP_EPISODES", "14"))
PAGES_URL = f"https://{OWNER}.github.io/{NAME}"

SITE = Path(os.getenv("SITE_DIR", "site"))
EPS = SITE / "episodes"
EPS.mkdir(parents=True, exist_ok=True)

meta = json.loads(Path("out/meta.json").read_text())
shutil.copyfile("out/episode.mp3", EPS / f"{meta['tag']}.mp3")

ep_index = SITE / "episodes.json"
episodes = json.loads(ep_index.read_text()) if ep_index.exists() else []
episodes = [e for e in episodes if e["tag"] != meta["tag"]]
episodes.insert(0, meta)

# Prune old episode files beyond KEEP, and entries whose file is missing
for e in episodes[KEEP:]:
    (EPS / f"{e['tag']}.mp3").unlink(missing_ok=True)
episodes = [e for e in episodes[:KEEP] if (EPS / f"{e['tag']}.mp3").exists()]
ep_index.write_text(json.dumps(episodes, indent=2))

items = ""
for e in episodes:
    url = f"{PAGES_URL}/episodes/{e['tag']}.mp3"
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
(SITE / "feed.xml").write_text(feed)
print(f"Feed updated: {len(episodes)} episodes -> {PAGES_URL}/feed.xml")
