#!/usr/bin/env python3
"""Daily business-news podcast generator.

Pipeline: fetch RSS -> select stories (LLM) -> enrich with full articles
-> write two-host script (LLM) -> multi-speaker TTS (Gemini) -> MP3.

Outputs: out/episode.mp3 and out/meta.json
"""
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import wave
from datetime import datetime, timezone
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from urllib.parse import quote_plus

import feedparser
import requests
import trafilatura
from google import genai
from google.genai import types

# ---------------- Config ----------------
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-flash-latest")
TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")
TARGET_MINUTES = int(os.getenv("TARGET_MINUTES", "30"))
HOST_A = os.getenv("HOST_A_NAME", "Alex")
HOST_B = os.getenv("HOST_B_NAME", "Sam")
VOICE_A = os.getenv("VOICE_A", "Puck")   # see ai.google.dev/gemini-api/docs/speech-generation
VOICE_B = os.getenv("VOICE_B", "Kore")
SHOW_NAME = os.getenv("SHOW_NAME", "Morning Market Brief")
WSJ_COOKIES_TXT = os.getenv("WSJ_COOKIES_TXT", "")  # optional, Netscape cookies.txt format

OUT_DIR = Path("out")
WORDS_TARGET = TARGET_MINUTES * 150  # ~150 spoken words/minute

# WSJ feeds drive story selection (editorial judgment); free feeds add coverage.
WSJ_FEEDS = {
    "WSJ Markets": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
    "WSJ Business": "https://feeds.content.dowjones.io/public/rss/WSJcomUSBusiness",
    "WSJ World": "https://feeds.content.dowjones.io/public/rss/RSSWorldNews",
    "WSJ Tech": "https://feeds.content.dowjones.io/public/rss/RSSWSJD",
    "WSJ Economy": "https://feeds.content.dowjones.io/public/rss/socialeconomyfeed",
}
FREE_FEEDS = {
    "CNBC Top": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CNBC Business": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
}

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

client = genai.Client(api_key=GEMINI_API_KEY)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def generate_with_retry(attempts=4, **kwargs):
    """Call the Gemini API, retrying transient network/server errors with backoff."""
    for i in range(attempts):
        try:
            return client.models.generate_content(**kwargs)
        except Exception as ex:
            if i == attempts - 1:
                raise
            wait = 20 * (i + 1)
            log(f"API call failed ({type(ex).__name__}: {ex}); retry {i + 1}/{attempts - 1} in {wait}s")
            time.sleep(wait)


def json_call(what, attempts=3, **kwargs):
    """Gemini call that must return valid JSON; regenerates if output is malformed/truncated."""
    for i in range(attempts):
        resp = generate_with_retry(**kwargs)
        try:
            return json.loads(resp.text)
        except Exception as ex:
            log(f"Bad JSON from model for {what} (attempt {i + 1}/{attempts}): {ex}")
            if i == attempts - 1:
                raise
            time.sleep(10)


# ---------------- 1. Fetch headlines ----------------
def fetch_headlines():
    items = []
    for source, url in {**WSJ_FEEDS, **FREE_FEEDS}.items():
        try:
            feed = feedparser.parse(url, request_headers=UA)
            for e in feed.entries[:25]:
                items.append({
                    "source": source,
                    "title": e.get("title", "").strip(),
                    "summary": re.sub(r"<[^>]+>", "", e.get("summary", ""))[:400],
                    "link": e.get("link", ""),
                    "published": e.get("published", ""),
                })
            log(f"{source}: {len(feed.entries)} items")
        except Exception as ex:
            log(f"WARN {source} failed: {ex}")
    if not items:
        sys.exit("No headlines fetched from any feed; aborting.")
    return items


# ---------------- 2. Select stories ----------------
def select_stories(items):
    prompt = f"""You are the editor of a daily morning business podcast (like Morning Brew),
recorded at ~4am US Eastern on {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}.
Below are raw headlines from WSJ and other outlets from the last ~24h.

Pick the stories for today's episode. Merge duplicate coverage of the same story into one.
Prioritize: market-moving news, major company news, economy/Fed, deals, notable tech,
one or two lighter/interesting business stories for the back half.

Return JSON: {{"episode_title": str, "stories": [{{
  "headline": str,               // your own neutral phrasing
  "why_it_matters": str,         // 1-2 sentences
  "search_query": str,           // short query to find full coverage on Google News
  "source_links": [str],         // links from the list below covering this story
  "segment": "lead"|"markets"|"business"|"tech"|"closer"
}}]}}
Pick 9-12 stories total, ordered by importance.

HEADLINES:
{json.dumps(items, indent=1)}"""
    data = json_call(
        "story selection",
        model=TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    log(f"Selected {len(data['stories'])} stories: {data['episode_title']}")
    return data


# ---------------- 3. Enrich with full articles ----------------
def wsj_session():
    """Optional: authenticated WSJ session from a cookies.txt secret. Best-effort only."""
    if not WSJ_COOKIES_TXT.strip():
        return None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(WSJ_COOKIES_TXT)
            path = f.name
        jar = MozillaCookieJar(path)
        jar.load(ignore_discard=True, ignore_expires=True)
        s = requests.Session()
        s.cookies = jar
        s.headers.update(UA)
        return s
    except Exception as ex:
        log(f"WARN WSJ cookies unusable: {ex}")
        return None


def extract_article(html):
    text = trafilatura.extract(html, include_comments=False) or ""
    return text.strip()


def fetch_url_text(url, session=None):
    try:
        r = (session or requests).get(url, headers=UA, timeout=20, allow_redirects=True)
        if r.status_code == 200:
            return extract_article(r.text)
    except Exception:
        pass
    return ""


def google_news_links(query, n=2):
    """Top article links for a query via Google News RSS."""
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url, request_headers=UA)
        return [e.link for e in feed.entries[:n]]
    except Exception:
        return []


def enrich(stories, wsj):
    for s in stories:
        texts = []
        # Optional WSJ full text (personal account; skipped silently on failure)
        if wsj:
            for link in [l for l in s.get("source_links", []) if "wsj.com" in l][:1]:
                t = fetch_url_text(link, wsj)
                if len(t) > 800:  # shorter = paywall stub, ignore
                    texts.append(("WSJ (full)", t[:6000]))
                    log(f"  WSJ full text OK: {s['headline'][:50]}")
        # Free coverage
        for link in google_news_links(s["search_query"]):
            t = fetch_url_text(link)
            if len(t) > 400:
                texts.append(("web", t[:5000]))
            if sum(len(t) for _, t in texts) > 9000:
                break
        # Non-WSJ links from original feeds
        if not texts:
            for link in [l for l in s.get("source_links", []) if "wsj.com" not in l][:2]:
                t = fetch_url_text(link)
                if len(t) > 400:
                    texts.append(("web", t[:5000]))
        s["material"] = "\n\n---\n\n".join(t for _, t in texts) or s["why_it_matters"]
        log(f"  enriched '{s['headline'][:50]}' ({len(s['material'])} chars)")
        time.sleep(1)
    return stories


# ---------------- 4. Write the two-host script ----------------
def write_script(episode):
    today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    material = "\n\n=====\n\n".join(
        f"STORY {i+1} [{s['segment']}]: {s['headline']}\nWhy it matters: {s['why_it_matters']}\nMATERIAL:\n{s['material'][:8000]}"
        for i, s in enumerate(episode["stories"])
    )
    prompt = f"""Write today's episode of "{SHOW_NAME}", a daily morning business-news podcast
for {today}, in the style of Morning Brew: smart, conversational, occasionally witty,
never cheesy. Two cohosts: {HOST_A} (drives the rundown, sharper/analytical) and
{HOST_B} (color, context, follow-up questions, occasional dry humor).

HARD REQUIREMENTS:
- TOTAL LENGTH: {WORDS_TARGET} words (+/-10%). This is critical - count as you go.
- Natural dialogue: interruptions, reactions, handoffs. No monologues over 120 words.
- Structure: cold open (top story tease) -> quick hellos -> lead stories -> markets ->
  business -> tech -> lighter closer -> sign-off with "what to watch today".
- All facts must come from the MATERIAL below. Numbers matter; if material lacks a
  number, don't invent one. Attribute reporting where natural ("the Journal reports...").
- No stage directions, no music cues, no sound effects. Spoken words only.
- Spell out numbers/tickers as they should be spoken ("the S and P 500", "up two point three percent").

Return JSON: {{"turns": [{{"speaker": "{HOST_A}"|"{HOST_B}", "text": str}}]}}

STORIES AND MATERIAL:
{material}"""
    turns = json_call(
        "podcast script",
        model=TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=65536,
            temperature=0.8,
        ),
    )["turns"]
    words = sum(len(t["text"].split()) for t in turns)
    log(f"Script: {len(turns)} turns, {words} words (~{words // 150} min)")
    # One retry if badly short
    if words < WORDS_TARGET * 0.7:
        log("Script too short; expanding...")
        turns = json_call(
            "podcast script (rewrite)",
            model=TEXT_MODEL,
            contents=prompt + f"\n\nYour previous draft was only {words} words. "
            f"Write it again at the full {WORDS_TARGET} words - go deeper on every story.",
            config=types.GenerateContentConfig(
                response_mime_type="application/json", max_output_tokens=65536, temperature=0.8),
        )["turns"]
        words = sum(len(t["text"].split()) for t in turns)
        log(f"Rewrite: {len(turns)} turns, {words} words")
    return turns


# ---------------- 5. TTS ----------------
def tts_chunk(dialogue_text, attempt=0):
    try:
        resp = generate_with_retry(
            model=TTS_MODEL,
            contents=f"TTS the following podcast conversation between {HOST_A} and {HOST_B}. "
                     f"Energetic but natural morning-radio delivery:\n\n{dialogue_text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker=HOST_A,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_A))),
                            types.SpeakerVoiceConfig(
                                speaker=HOST_B,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_B))),
                        ]))),
        )
        return resp.candidates[0].content.parts[0].inline_data.data  # raw PCM 24kHz 16-bit mono
    except Exception as ex:
        if attempt < 3:
            wait = 15 * (attempt + 1)
            log(f"TTS chunk failed ({ex}); retry in {wait}s")
            time.sleep(wait)
            return tts_chunk(dialogue_text, attempt + 1)
        raise


def synthesize(turns):
    # Chunk at speaker boundaries, ~3500 chars per TTS request
    chunks, cur = [], []
    for t in turns:
        cur.append(f"{t['speaker']}: {t['text']}")
        if sum(len(x) for x in cur) > 3500:
            chunks.append("\n".join(cur))
            cur = []
    if cur:
        chunks.append("\n".join(cur))
    log(f"TTS: {len(chunks)} chunks")

    pcm = b""
    for i, c in enumerate(chunks):
        log(f"  chunk {i + 1}/{len(chunks)}")
        pcm += tts_chunk(c)
        time.sleep(2)

    OUT_DIR.mkdir(exist_ok=True)
    wav_path = OUT_DIR / "episode.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(pcm)
    mp3_path = OUT_DIR / "episode.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", "96k", str(mp3_path)],
        check=True, capture_output=True)
    wav_path.unlink()
    duration = len(pcm) / (24000 * 2)
    log(f"Audio: {duration / 60:.1f} min, {mp3_path.stat().st_size / 1e6:.1f} MB")
    return mp3_path, int(duration)


# ---------------- Main ----------------
def main():
    items = fetch_headlines()
    episode = select_stories(items)
    wsj = wsj_session()
    episode["stories"] = enrich(episode["stories"], wsj)
    turns = write_script(episode)
    mp3, duration = synthesize(turns)

    today = datetime.now(timezone.utc)
    meta = {
        "date": today.strftime("%Y-%m-%d"),
        "tag": f"ep-{today.strftime('%Y-%m-%d')}",
        "title": f"{today.strftime('%b %d')}: {episode['episode_title']}",
        "description": " • ".join(s["headline"] for s in episode["stories"]),
        "duration_seconds": duration,
        "size_bytes": mp3.stat().st_size,
        "pub_date": today.strftime("%a, %d %b %Y %H:%M:%S +0000"),
    }
    (OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    (OUT_DIR / "script.json").write_text(json.dumps(turns, indent=2))
    log("Done.")


if __name__ == "__main__":
    main()
