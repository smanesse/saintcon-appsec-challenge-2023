#!/usr/bin/python3
import os
import shutil

OUT = "./out"

files = [
    "memeapp/conf/",
    "memeapp/controllers/",
    "memeapp/static/",
    "memeapp/templates/",
    "memeapp/utils/",
    "memeapp/app.py",
    "memeapp/model.py",
]


if os.path.exists(OUT):
    shutil.rmtree(OUT)

os.makedirs(OUT)
os.makedirs(os.path.join(OUT, "memeapp"))


for f in files:
    print("copying", f)
    if f.endswith("/"):
        shutil.copytree(f, os.path.join(OUT, f))
    else:
        shutil.copy(f, os.path.join(OUT, f))


shutil.make_archive("appsec-submission", 'zip', OUT)

if os.path.exists(OUT):
    shutil.rmtree(OUT)
