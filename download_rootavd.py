import urllib.request
import zipfile
import io
import os
import shutil

print("Downloading rootAVD from GitLab...")
url = "https://gitlab.com/newbit/rootAVD/-/archive/master/rootAVD-master.zip"
r = urllib.request.urlopen(url)

print("Extracting...")
z = zipfile.ZipFile(io.BytesIO(r.read()))
z.extractall(".")

if os.path.exists("rootAVD-master"):
    if os.path.exists("rootAVD"):
        shutil.rmtree("rootAVD")
    os.rename("rootAVD-master", "rootAVD")

print("Done.")
