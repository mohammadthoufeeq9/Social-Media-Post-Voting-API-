from fastapi import APIRouter
from fast_app.models.post import Vote
from fast_app.utils.auth import get_current_user
from fast_app.database.database import get_db
from fastapi import status,HTTPException
from fast_app.schemas.post import Vote_schema
from sqlalchemy.orm import Session
from fastapi import Depends

router=APIRouter(
    tags=['votes']
)

@router.post('/vote',status_code=status.HTTP_201_CREATED)
def Vote_fun(vote:Vote_schema,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    vote_query=db.query(Vote).filter(Vote.post_id == vote.post_id, Vote.user_id == current_user.id)
    found_vote=vote_query.first()
    if vote.dir==1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'user {current_user.id} has already voted post {vote.post_id}...')
        new_vote=Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return{
            'message':'Successfully added vote'
        }
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Oppssss! you didnt vote this post yet-vote not present')
        vote_query.delete()
        db.commit()
        return {
            'message':'successfully deleted vote'
        }