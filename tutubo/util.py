from tutubo.models import Video


def get_music_score(vid):
    score = 50
    explicit_music = ["full album", "MUSIC VIDEO"]
    maybe_music = ["official video", "Greatest Hits", "Soundtrack", "mix",
                   "music", "compilation", "full show", "lyrics",
                   "live", "cover", "album", "Acoustic"]
    negatives = ["movie", "film", "trailer", "episode",
                 "interview", "podcast", "reaction"]
    norm = lambda k: k.replace("_", "").replace("̲", ""). \
        replace("-", "").replace(" ", "").lower().strip()

    if any(norm(s) in norm(vid.title) for s in negatives):
        score -= 15
    elif any(norm(s) in norm(vid.title) for s in explicit_music):
        score += 6
    elif any(norm(s) in norm(vid.title) for s in maybe_music):
        score += 2
    else:
        score -= 2

    if isinstance(vid, Video):  # data not available in preview object
        if not vid.metadata:
            score -= 1

        kws = [norm(k) for k in vid.keywords]
        for v in vid.metadata:
            if norm(v.get("Song", "")) in norm(vid.title):
                score += 10
            else:
                score -= 1
            if norm(v.get("Artist", "")) in norm(vid.title):
                score += 5
            elif norm(v.get("Artist", "")) in norm(vid.author):
                score += 2
            elif norm(v.get("Artist", "")) in kws:
                score += 1
            else:
                score -= 2

    score = score / 100
    score = max(score, 0)
    score = min(1, score)
    return score
