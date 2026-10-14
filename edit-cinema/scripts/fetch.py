# fetch candidate images: Wikimedia Commons + Openverse. usage: fetch.py key "query" [key "query" ...]
import json, sys, urllib.request, urllib.parse, os
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "reelVM-editor/1.0 (video edit research)"}
def get(url, tries=4):
    import time
    for t in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == tries-1: raise
            time.sleep(3 * (t+1))
def commons(q, n=6):
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(action="query", generator="search",
        gsrsearch=f"filetype:bitmap {q}", gsrnamespace=6, gsrlimit=n, prop="imageinfo", iiprop="url|size", iiurlwidth=1280, format="json"))
    pages = json.loads(get(u)).get("query", {}).get("pages", {})
    return [(p["imageinfo"][0]["thumburl"], p["title"]) for p in sorted(pages.values(), key=lambda p: p["index"]) if p["imageinfo"][0]["width"] >= 900]
def openverse(q, n=6):
    u = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(dict(q=q, page_size=n, size="large", excluded_source="wikimedia"))
    return [(r["url"], r.get("title") or "") for r in json.loads(get(u))["results"]]
def run(key, q, src):
    try: items = commons(q) if src == "c" else openverse(q)
    except Exception as e: print("ERR", key, src, e); return
    for i, (url, title) in enumerate(items):
        fn = f"cand/{key}_{src}{i}.jpg"
        if os.path.exists(fn): continue
        try:
            open(fn, "wb").write(get(url)); open(fn + ".src", "w").write(f"{url}\n{title}\n")
        except Exception as e: print("dl fail", key, url[:80], e)
args = sys.argv[1:]; jobs = [(args[i], args[i+1], s) for i in range(0, len(args), 2) for s in "co"]
with ThreadPoolExecutor(4) as ex: list(ex.map(lambda j: run(*j), jobs))
