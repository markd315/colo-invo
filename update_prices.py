import urllib.request
import re
import datetime
import os
import sys

URL = "https://oldschool.runescape.wiki/w/Rewards_Chest_(Fortis_Colosseum)"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Colo-Invo-Updater/1.0'}

def main():
    print(f"Fetching {URL}...")
    req = urllib.request.Request(URL, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        sys.exit(1)

    rewards = []
    # The wiki typically has text like: "Average wave 1 reward is worth <span>29,280</span>"
    # But we should also be flexible with HTML tags.
    for wave in range(1, 13):
        # We look for something containing "wave <N> reward" and a number nearby in a span or text
        pattern = re.compile(rf"wave\s+{wave}\s+reward\s+is\s+worth\s+<span[^>]*>([\d,.]+)", re.IGNORECASE)
        match = pattern.search(html)
        if match:
            val_str = match.group(1).replace(',', '')
            try:
                val = float(val_str)
                # Keep as integer if possible for cleaner look
                if val.is_integer():
                    rewards.append(str(int(val)))
                else:
                    rewards.append(str(val))
            except ValueError:
                print(f"Failed to parse value for wave {wave}: {match.group(1)}")
                sys.exit(1)
        else:
            print(f"Failed to find reward for wave {wave}")
            sys.exit(1)

    if len(rewards) != 12:
        print(f"Expected 12 rewards, found {len(rewards)}")
        sys.exit(1)

    rewards_str = "[" + ", ".join(rewards) + "]"
    print(f"Parsed rewards: {rewards_str}")

    # Now update index.html
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "views", "index.html")
    if not os.path.exists(html_path):
        print(f"index.html not found at {html_path}")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the waveRewards array
    # We use the markers: /* WIKI_REWARDS_START */ [ ... ] /* WIKI_REWARDS_END */
    content = re.sub(
        r"/\*\s*WIKI_REWARDS_START\s*\*/.*?/\*\s*WIKI_REWARDS_END\s*\*/",
        f"/* WIKI_REWARDS_START */ {rewards_str} /* WIKI_REWARDS_END */",
        content,
        flags=re.DOTALL
    )

    # Replace LAST_UPDATED_AT placeholder
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    content = re.sub(
        r"<!--\s*LAST_UPDATED_AT\s*-->.*?<!--\s*/LAST_UPDATED_AT\s*-->",
        f"<!-- LAST_UPDATED_AT -->Last updated: {now_str}<!-- /LAST_UPDATED_AT -->",
        content,
        flags=re.DOTALL
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully updated {html_path} with new values and timestamp: {now_str}")

if __name__ == "__main__":
    main()
