import enum

from pytube.contrib.search import Search as _Search
from tutubo.models import *


class SearchType(enum.IntEnum):
    VIDEOS = enum.auto()
    RELATED_VIDEOS = enum.auto()
    CHANNELS = enum.auto()
    PLAYLISTS = enum.auto()
    YOUTUBE_MIX = enum.auto()
    RELATED_QUERIES = enum.auto()
    ALL = enum.auto()


class YoutubeSearch(_Search):
    # see https://github.com/pytube/pytube/pull/1133
    def __init__(self, query, preview=True):
        super().__init__(query)
        self.preview = preview

    def iterate_results(self, max_pages=1):
        """Return search results.
        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.
        :rtype: list
        :returns:
            A list of YouTube objects.
        """
        pidx = 0
        videos, continuation = self.fetch_and_parse(search_type=SearchType.ALL)

        for v in videos:
            if not self.preview:
                v = v.get()
            yield v

        while continuation is not None:
            pidx += 1
            if pidx > max_pages:
                break
            videos, continuation = self.fetch_and_parse(continuation,
                                                        search_type=SearchType.ALL)
            for v in videos:
                if not self.preview:
                    v = v.get()
                yield v

    def iterate_videos(self, max_pages=1):
        for v in self.iterate_results(max_pages):
            if isinstance(v, Video) or isinstance(v, VideoPreview):
                yield v

    def iterate_related_videos(self, max_pages=1):
        for v in self.iterate_results(max_pages):
            if isinstance(v, RelatedVideo):
                yield v

    def iterate_channels(self, max_pages=1):
        for v in self.iterate_results(max_pages):
            if isinstance(v, Channel) or isinstance(v, ChannelPreview):
                yield v

    def iterate_playlists(self, max_pages=1):
        for v in self.iterate_results(max_pages):
            if isinstance(v, PlaylistPreview) or isinstance(v, Playlist):
                yield v

    def iterate_mixes(self, max_pages=1):
        for v in self.iterate_results(max_pages):
            if isinstance(v, YoutubeMixPreview):
                yield v

    def iterate_queries(self, max_pages=1):
        for v in self.iterate_results(max_pages):
            if isinstance(v, RelatedSearch):
                yield v

    def fetch_and_parse(self, continuation=None, search_type=SearchType.ALL):
        """Fetch from the innertube API and parse the results.

        :param str continuation:
            Continuation string for fetching results.
        :rtype: tuple
        :returns:
            A tuple of a list of YouTube objects and a continuation string.
        """
        # Begin by executing the query and identifying the relevant sections
        #  of the results
        raw_results = self.fetch_query(continuation)

        # Initial result is handled by try block, continuations by except block
        try:
            sections = \
                raw_results['contents']['twoColumnSearchResultsRenderer'][
                    'primaryContents']['sectionListRenderer']['contents']
        except KeyError:
            sections = raw_results['onResponseReceivedCommands'][0][
                'appendContinuationItemsAction']['continuationItems']
        item_renderer = None
        continuation_renderer = None
        for s in sections:
            if 'itemSectionRenderer' in s:
                item_renderer = s['itemSectionRenderer']
            if 'continuationItemRenderer' in s:
                continuation_renderer = s['continuationItemRenderer']

        # If the continuationItemRenderer doesn't exist, assume no further results
        if continuation_renderer:
            next_continuation = continuation_renderer['continuationEndpoint'][
                'continuationCommand']['token']
        else:
            next_continuation = None

        # If the itemSectionRenderer doesn't exist, assume no results.
        if item_renderer:
            results = []
            raw_video_list = item_renderer['contents']
            for video_details in raw_video_list:
                # Skip over ads
                if video_details.get('searchPyvRenderer', {}).get('ads', None):
                    continue

                # Skip "recommended" type videos e.g. "people also watched" and "popular X"
                #  that break up the search results
                elif 'shelfRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.RELATED_VIDEOS]:
                    for v in video_details['shelfRenderer']['content'][
                        'verticalListRenderer']['items']:
                        vid = RelatedVideoPreview(v['videoRenderer'])
                        results.append(vid)
                    continue

                # Skip auto-generated "mix" playlist results
                elif 'radioRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.YOUTUBE_MIX]:
                    pl = YoutubeMixPreview(video_details['radioRenderer'])
                    results.append(pl)
                    continue

                # Skip playlist results
                elif 'playlistRenderer' in video_details and \
                        search_type in [SearchType.ALL, SearchType.PLAYLISTS]:
                    pl = PlaylistPreview(video_details['playlistRenderer'])
                    results.append(pl)
                    continue

                # Skip channel results
                elif 'channelRenderer' in video_details and \
                        search_type in [SearchType.ALL, SearchType.CHANNELS]:
                    ch = ChannelPreview(video_details['channelRenderer'])
                    results.append(ch)
                    continue

                # Skip 'people also searched for' results
                elif 'horizontalCardListRenderer' in video_details and \
                        search_type in [SearchType.RELATED_QUERIES,
                                        SearchType.ALL]:
                    for v in video_details['horizontalCardListRenderer'][
                        'cards']:
                        results.append(
                            RelatedSearch(v['searchRefinementCardRenderer']))
                    continue

                # Can't seem to reproduce, probably related to typo fix suggestions
                elif 'didYouMeanRenderer' in video_details:
                    continue

                # Seems to be the renderer used for the image shown on a no results page
                elif 'backgroundPromoRenderer' in video_details:
                    continue

                # no more results
                elif 'messageRenderer' in video_details:
                    next_continuation = None
                    break

                elif 'videoRenderer' in video_details and \
                        search_type in [SearchType.ALL, SearchType.VIDEOS]:
                    vid = VideoPreview(video_details['videoRenderer'])
                    results.append(vid)
        else:
            results = None

        return results, next_continuation
