from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..deps import get_db_session, get_optional_user
from ..services.search import search_tracks, search_profiles
from ..models.favorite import Favorite
from ..models.track import Track
from ..routers.tracks import aggregate_track_counts

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


def compute_tops(tracks: list[dict]):
    if not tracks:
        return set(), set(), set()
    max_play = max(t["plays_count"] for t in tracks)
    max_like = max(t["likes_count"] for t in tracks)
    hit_ids = set()
    top_play_ids = set()
    top_like_ids = set()
    for t in tracks:
        pid = t["id"]
        is_play = max_play > 0 and t["plays_count"] == max_play
        is_like = max_like > 0 and t["likes_count"] == max_like
        if is_play and is_like:
            hit_ids.add(pid)
        elif is_play:
            top_play_ids.add(pid)
        elif is_like:
            top_like_ids.add(pid)
    return hit_ids, top_play_ids, top_like_ids


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    q: str | None = None,
    filter: str = "all",
    db: Session = Depends(get_db_session),
    current_user=Depends(get_optional_user),
):
    filter = filter if filter in {"all", "user", "platform"} else "all"
    tracks = search_tracks(db, q, filter_by=filter)
    enriched_tracks = aggregate_track_counts(db, tracks)
    hit_ids, top_play_ids, top_like_ids = compute_tops(enriched_tracks)
    # mark liked ids for current user
    liked_ids = set()
    if current_user:
        liked_ids = {
            fav.track_id
            for fav in db.exec(select(Favorite).where(Favorite.user_id == current_user.id)).all()
        }
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tracks": enriched_tracks,
            "query": q or "",
            "filter": filter,
            "current_user": current_user,
            "liked_ids": liked_ids,
            "hit_ids": hit_ids,
            "top_play_ids": top_play_ids,
            "top_like_ids": top_like_ids,
        },
    )


@router.get("/profiles/{nickname}", response_class=HTMLResponse)
def profile_page(
    request: Request,
    nickname: str,
    profile: str | None = None,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_optional_user),
):
    from ..routers.profiles import get_user_by_nickname

    user = get_user_by_nickname(db, nickname)
    uploaded = db.exec(select(Track).where(Track.creator_id == user.id)).all()
    favorite_ids = [fav.track_id for fav in db.exec(select(Favorite).where(Favorite.user_id == user.id)).all()]
    favorites = db.exec(select(Track).where(Track.id.in_(favorite_ids))).all() if favorite_ids else []
    liked_ids = set()
    if current_user:
        liked_ids = {
            fav.track_id
            for fav in db.exec(select(Favorite).where(Favorite.user_id == current_user.id)).all()
        }
    profile_results = search_profiles(db, profile) if profile else []
    uploaded_enriched = aggregate_track_counts(db, uploaded)
    favorites_enriched = aggregate_track_counts(db, favorites)
    up_hit, up_play, up_like = compute_tops(uploaded_enriched)
    fav_hit, fav_play, fav_like = compute_tops(favorites_enriched)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "profile_user": user,
            "uploaded": uploaded_enriched,
            "favorites": favorites_enriched,
            "current_user": current_user,
            "liked_ids": liked_ids,
            "profile_query": profile or "",
            "profiles": profile_results,
            "uploaded_hit": up_hit,
            "uploaded_play": up_play,
            "uploaded_like": up_like,
            "favorites_hit": fav_hit,
            "favorites_play": fav_play,
            "favorites_like": fav_like,
        },
    )


@router.get("/profiles/me", response_class=HTMLResponse)
def my_profile_page(request: Request, current_user=Depends(get_optional_user)):
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url=f"/profiles/{current_user.nickname}", status_code=302)
