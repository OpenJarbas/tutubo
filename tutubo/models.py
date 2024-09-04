from tutubo.pytube import YouTube as Video, Channel, Playlist


class YoutubePreview:
    def __init__(self, renderer_data):
        self._raw_data = renderer_data


class PlaylistPreview(YoutubePreview):
    def get(self):
        return Playlist(self.playlist_url)

    @property
    def title(self):
        return self._raw_data["title"]['simpleText']

    @property
    def playlist_id(self):
        return self._raw_data["playlistId"]

    @property
    def playlist_url(self):
        return f"https://www.youtube.com/playlist?list={self.playlist_id}"

    @property
    def video_count(self):
        return self._raw_data['videoCount']

    @property
    def featured_videos(self):
        videos = []
        for v in self._raw_data['videos']:
            v = v['childVideoRenderer']
            videos.append({
                "videoId": v['videoId'],
                "url": f"https://youtube.com/watch?v={v['videoId']}",
                "image": f"https://img.youtube.com/vi/{v['videoId']}/default.jpg",
                "title": v["title"]["simpleText"]
            })
        return videos

    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return [t['thumbnails'][0] for t in self._raw_data['thumbnails']]

    def __str__(self):
        return self.title

    @property
    def as_dict(self):
        return {'playlistId': self.playlist_id,
                'title': self.title,
                'url': self.playlist_url,
                "image": self.thumbnail_url,
                'featured_videos': self.featured_videos}


class YoutubeMixPreview(PlaylistPreview):
    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return self._raw_data['thumbnail']['thumbnails']

    @property
    def as_dict(self):
        return {'playlistId': self.playlist_id,
                'title': self.title,
                'url': self.playlist_url,
                "image": self.thumbnail_url,
                'featured_videos': self.featured_videos}


class ChannelPreview(YoutubePreview):

    def get(self):
        return Channel(self.channel_url)

    @property
    def title(self):
        return self._raw_data["title"]['simpleText']

    @property
    def description(self):
        return "".join(r["text"] for r in
                       self._raw_data['descriptionSnippet']['runs'])

    @property
    def channel_id(self):
        return self._raw_data["channelId"]

    @property
    def channel_url(self):
        return f"https://www.youtube.com/channel/{self.channel_id}"

    @property
    def video_count(self):
        return int(self._raw_data['videoCountText']["runs"][0]["text"])

    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return self._raw_data['thumbnail']['thumbnails']

    def __str__(self):
        return self.title

    @property
    def as_dict(self):
        return {'channelId': self.channel_id,
                'title': self.title,
                'image': self.thumbnail_url,
                'url': self.channel_url}


class VideoPreview(YoutubePreview):

    def get(self):
        return Video(self.watch_url)

    @property
    def title(self):
        return "".join(r["text"] for r in
                       self._raw_data['title']['runs'])

    @property
    def author(self):
        return "".join(r["text"] for r in
                       self._raw_data['ownerText']['runs'])

    @property
    def channel_id(self):
        return self._raw_data['ownerText']['runs'][0][
            'navigationEndpoint']['commandMetadata'][
            'webCommandMetadata']['url']

    @property
    def channel_url(self):
        return f'https://www.youtube.com/channel/{self.channel_id}'

    @property
    def video_id(self):
        return self._raw_data['videoId']

    @property
    def watch_url(self):
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    def view_count(self):
        # Livestreams have "runs", non-livestreams have "simpleText",
        #  and scheduled releases do not have 'viewCountText'
        if 'viewCountText' in self._raw_data:
            if 'runs' in self._raw_data['viewCountText']:
                vid_view_count_text = \
                    self._raw_data['viewCountText']['runs'][0][
                        'text']
            else:
                vid_view_count_text = \
                    self._raw_data['viewCountText']['simpleText']
            # Strip ' views' text, then remove commas
            stripped_text = vid_view_count_text.split()[0].replace(
                ',', '')
            if stripped_text != 'No':
                return int(stripped_text)
        return 0

    @property
    def length(self):
        if 'lengthText' in self._raw_data:
            pts = self._raw_data['lengthText']['simpleText'].split(":")
            h, m, s = 0, 0, 0
            if len(pts) == 3:
                h, m, s = pts
            elif len(pts) == 2:
                m, s = pts
            elif len(pts) == 1:
                s = pts
            return int(s) + \
                60 * int(m) + \
                60 * 60 * int(h)
        return 0

    @property
    def is_live(self) -> bool:
        return self.length == 0

    @property
    def thumbnail_url(self):
        return f"https://img.youtube.com/vi/{self.video_id}/default.jpg"

    @property
    def keywords(self):
        return []  # just for api compatibility, requires parsing url!

    def __str__(self):
        return self.title

    @property
    def as_dict(self):
        return {'length': self.length,
                'keywords': self.keywords,
                'image': self.thumbnail_url,
                'title': self.title,
                "author": self.author,
                'url': self.watch_url,
                'videoId': self.video_id}


class RelatedVideoPreview(VideoPreview):
    @property
    def as_dict(self):
        return {'length': self.length,
                'keywords': self.keywords,
                'image': self.thumbnail_url,
                'title': self.title,
                "author": self.author,
                'url': self.watch_url,
                'videoId': self.video_id}


class RelatedSearch(YoutubePreview):

    def get(self, preview=True):
        from tutubo.search import YoutubeSearch
        return YoutubeSearch(self.query, preview=preview)

    @property
    def query(self):
        return "".join(r["text"] for r in self._raw_data['query']['runs'])

    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return self._raw_data['thumbnail']['thumbnails']

    def __str__(self):
        return self.query

    @property
    def as_dict(self):
        return {'query': self.query,
                'image': self.thumbnail_url}


class RelatedVideo(Video):
    """"""
