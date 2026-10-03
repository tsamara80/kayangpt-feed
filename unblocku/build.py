"""Build index.html (the file you host) from app.html (the preview source).

index.html gets real page tags and your store links from store-links.json
(placeholders if that file doesn't exist yet).
Run: python3 build.py
"""
import json, os

src = open("app.html", encoding="utf-8").read()

# Your real links live in store-links.json so rebuilding never loses them.
links = {"checkoutUrl": "PASTE_YOUR_CHECKOUT_LINK", "licenseApi": "PASTE_YOUR_WORKER_URL"}
if os.path.exists("store-links.json"):
    links.update(json.load(open("store-links.json", encoding="utf-8")))

for name in ("checkoutUrl", "licenseApi"):
    old = f'{name}: "demo",'
    assert old in src, f"{name} not found in app.html CONFIG"
    src = src.replace(old, f"{name}: {json.dumps(links[name])},", 1)

head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Beat writer's block: answer 3 questions, get 3 ready content ideas with hooks and outlines.">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
"""
title, rest = src.split("</title>", 1)
rest = rest.replace('<header class="bar">', '</head>\n<body>\n<header class="bar">', 1)
open("index.html", "w", encoding="utf-8").write(head + title + "</title>\n" + rest + "\n</body>\n</html>\n")
print("index.html built")
