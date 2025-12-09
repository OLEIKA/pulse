from fastapi import APIRouter, Depends, UploadFile, Form, File, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select, func, delete

from ..deps import get_db_session, get_current_user, get_optional_user
from ..models.track import Track
from ..models.favorite import Favorite
from ..models.play import Play
from ..models.user import User
from ..services.storage import save_mp3, file_url
from ..schemas.track import TrackUpdate

router = APIRouter()


def get_track_with_owner(db: Session, track_id: int) -> Track:
    track = db.get(Track, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return track


@router.post("/upload")
def upload_track(
    title: str = Form(...),
    artist: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    filename = save_mp3(file)
    track = Track(title=title, artist=artist, filename=filename, creator_id=user.id, is_platform=False)
    db.add(track)
    db.commit()
    db.refresh(track)
    return RedirectResponse(url="/", status_code=303)


@router.post("/{track_id}/like")
def like_track(
    track_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    track = get_track_with_owner(db, track_id)
    existing = db.get(Favorite, (user.id, track.id))
    if existing:
        return RedirectResponse(url="/", status_code=303)
    fav = Favorite(user_id=user.id, track_id=track.id)
    db.add(fav)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/{track_id}/unlike")
def unlike_track(
    track_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    _ = get_track_with_owner(db, track_id)
    existing = db.get(Favorite, (user.id, track_id))
    if existing:
        db.delete(existing)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/{track_id}/play")
def play_track(
    track_id: int,
    db: Session = Depends(get_db_session),
    user: User | None = Depends(get_optional_user),
):
    track = get_track_with_owner(db, track_id)
    play = Play(track_id=track.id, user_id=user.id if user else None)
    db.add(play)
    db.commit()
    return JSONResponse({"status": "ok"})


@router.post("/{track_id}/delete")
def delete_track(
    track_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    track = get_track_with_owner(db, track_id)
    if track.creator_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    # cascade delete favorites and plays
    db.exec(delete(Favorite).where(Favorite.track_id == track.id))
    db.exec(delete(Play).where(Play.track_id == track.id))
    db.delete(track)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/{track_id}/update")
def update_track(
    track_id: int,
    title: str = Form(...),
    artist: str = Form(""),
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    track = get_track_with_owner(db, track_id)
    if track.creator_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    track.title = title
    track.artist = artist
    db.add(track)
    db.commit()
    return RedirectResponse(url="/profiles/me", status_code=303)


def aggregate_track_counts(db: Session, tracks: list[Track]) -> list[dict]:
    track_ids = [t.id for t in tracks]
    if not track_ids:
        return []
    creator_ids = {t.creator_id for t in tracks}
    creators = (
        db.exec(select(User.id, User.nickname).where(User.id.in_(creator_ids))).all()
        if creator_ids
        else []
    )
    creator_map = {cid: nick for cid, nick in creators}
    likes_counts = dict(
        db.exec(
            select(Favorite.track_id, func.count(Favorite.user_id)).where(Favorite.track_id.in_(track_ids)).group_by(Favorite.track_id)
        ).all()
    )
    play_counts = dict(
        db.exec(
            select(Play.track_id, func.count(Play.id)).where(Play.track_id.in_(track_ids)).group_by(Play.track_id)
        ).all()
    )
    enriched = []
    for t in tracks:
        enriched.append(
            {
                "id": t.id,
                "title": t.title,
                "artist": t.artist,
                "creator_id": t.creator_id,
                "creator_nickname": creator_map.get(t.creator_id, ""),
                "filename": t.filename,
                "is_platform": t.is_platform,
                "likes_count": likes_counts.get(t.id, 0),
                "plays_count": play_counts.get(t.id, 0),
                "created_at": t.created_at,
            }
        )
    return enriched
