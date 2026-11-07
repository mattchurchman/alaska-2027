#!/usr/bin/env python3
"""Check that source, price and media URLs still answer.

  python3 tools/linkcheck.py [--only domain] [--limit N] [--timeout S]

Writes notes/linkcheck.txt and prints a summary. Status 'ok' = HTTP 2xx/3xx.
Many cruise and travel sites block scripts (403/429) even when the page is fine in a
browser, so treat 'blocked' as "check by hand", not "broken". Run it on a normal
computer: Claude's cloud workspace only reaches an allowlist of sites, so most
links show 'unreachable' there.
"""
import sys, urllib.request, urllib.error, concurrent.futures as cf
from common import load, ROOT

args = sys.argv[1:]
def opt(n, dflt=None):
    if n in args:
        i = args.index(n); v = args[i + 1]; del args[i:i + 2]; return v
    return dflt
only, limit, timeout = opt("--only"), int(opt("--limit", "0")), float(opt("--timeout", "15"))

d = load()
urls = {}
def add(u, where):
    if u and u.startswith("http"):
        urls.setdefault(u, []).append(where)
for s in d["sources"]["sources"]:
    add(s.get("url"), f"source:{s['id']}")
for r in d["prices"]["rows"]:
    add(r.get("url"), f"row:{r['id']}")
for m in d["media"]["photos"]:
    add(m.get("url"), f"photo:{m['id']}"); add(m.get("page"), f"photo:{m['id']}")
for v in d["media"]["videos"] + d["media"]["officialLinks"]:
    add(v.get("url"), f"media:{v.get('id')}")
todo = [u for u in urls if not only or only in u]
if limit:
    todo = todo[:limit]

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"}
def check(u):
    for method in ("HEAD", "GET"):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA, method=method), timeout=timeout) as r:
                return u, "ok", r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 400, 404, 429):
                continue
            return u, ("blocked" if e.code in (401, 403, 429, 999) else "broken"), e.code
        except Exception as e:
            if method == "GET":
                return u, "unreachable", type(e).__name__
    return u, "unreachable", "?"

res = []
with cf.ThreadPoolExecutor(12) as ex:
    for r in ex.map(check, todo):
        res.append(r)
(ROOT / "notes").mkdir(exist_ok=True)
with open(ROOT / "notes/linkcheck.txt", "w") as f:
    for u, st, code in sorted(res, key=lambda x: (x[1] != "broken", x[1], x[0])):
        f.write(f"{st:<11} {code!s:<18} {u}  <- {', '.join(urls[u][:3])}{' ...' if len(urls[u]) > 3 else ''}\n")
from collections import Counter
print(dict(Counter(st for _, st, _ in res)), f"of {len(res)} urls; details in notes/linkcheck.txt")
