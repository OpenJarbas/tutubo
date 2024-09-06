from tutubo.models import Channel

url = "https://www.youtube.com/@ShoutStudios"
c = Channel(url)
for v in c.live:
    if not v.is_live:
        continue
    print(v.title, v.watch_url, v.keywords)

