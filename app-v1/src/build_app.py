#!/usr/bin/env python3
"""Build the planner pages from template.html + planner_*.js + planner.css + coast.json + data.json.
index.html          -> published artifact page (loads data.json, falls back to the embedded copy)
alaska-planner.html -> standalone single file anyone can open offline (data embedded)
Run after any edit to data.json:  python3 build_app.py"""
import json
data = json.load(open("data.json"))
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
coast = open("coast.json").read().replace("</", "<\\/")
js = "\n".join(open(f).read() for f in ("planner_core.js", "planner_views.js", "planner_map.js")).replace("/*__COAST__*/null", coast)
tpl = open("template.html").read()
for ph, val in (("/*__PLANNER_CSS__*/", open("planner.css").read()), ("/*__PLANNER_JS__*/", js), ("/*__DATA__*/", blob)):
    assert ph in tpl, ph
    tpl = tpl.replace(ph, val, 1)
page = tpl
open("index.html", "w").write(page)
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}</style>\n'
              '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
open("alaska-planner.html", "w").write(standalone)
print("index.html", len(page), "bytes; alaska-planner.html", len(standalone), "bytes")
