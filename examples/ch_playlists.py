from tutubo.models import Channel

url = "https://www.youtube.com/channel/UC4BSeEq7XNtihGqI309vhYg"
c = Channel(url)
for pl in c.playlists:
    print(pl.title)
    for video in pl.videos:
        print("     ", video.title)

