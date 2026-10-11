from sqlalchemy import or_
from fastapi import HTTPException,Depends,status
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.models.post import Post,User,RevokedToken

from fast_app.schemas.post import(
     create_post,update_post,PostResponse,PostsResponse,UserCreate,UserResponse,UserLogin,RefreshToken
)
from fast_app.utils.password import verify_hash,hash_password
from fast_app.utils.auth import create_access_token,get_current_user,create_refresh_token,SECRET_KEY,ALGORITHM
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import BackgroundTasks
from jose import jwt,JWTError

router = APIRouter()


def get_posts(
    limit: int = 5,
    title: str | None = None,
    search:str|None=None,
    published:bool|None=None,
    page:int=1,
    db: Session = Depends(get_db)
):
    query = db.query(Post)

    if title:
        query = query.filter(Post.title == title)

    if search:
         query = query.filter(or_(
             Post.title.ilike(f"%{search}%"),
             Post.content.ilike(f"%{search}%")
         ))

    if published==True:
          query= query.filter(Post.published == published)
          query=query.order_by(Post.created_at.desc())

    offset=(page -1)*limit
    if page < 1:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No negative pages and zero pages")

    return query.offset(offset).limit(limit).all()


def get_a_post(db:Session,post_id:int):
    return db.query(Post).filter(Post.id==post_id).first()



def get_current_user_admin(current_user=Depends(get_current_user)):
     if not current_user.is_admin:
          raise HTTPException(status_code=403,detail="Admin access required")
     return current_user


@router.get("/admin",status_code=status.HTTP_200_OK)
def get_admin(current_user=Depends(get_current_user_admin)):
     return {
          "Message":"Welcome admin",
          "User":current_user.username
     }


@router.get("/posts",response_model=PostsResponse)
def home(posts=Depends(get_posts),notify:bool=False):
    return{
        'Message':'Here are all the posts',
        'notify':notify,
        'Posts':posts
    }



@router.get("/my-posts",response_model=PostsResponse)
def get_my_posts(current_user=Depends(get_current_user),db:Session=Depends(get_db),notify:bool=False):
     posts=db.query(Post).filter(Post.author_id == current_user.id).all()
     return {
        'Message':'Here are all the posts',
        'notify':notify,
        'Posts':posts
    }


@router.get("/post/{post_id}",response_model=PostResponse)
def get_post_by_id(post_id:int,db:Session=Depends(get_db),detail:bool=False):
            post=get_a_post(db,post_id)
            if post is None:
                raise HTTPException(status_code=404,detail="post not found")
            return post


@router.post("/post",response_model=PostResponse,status_code=status.HTTP_201_CREATED)
def createPost(post_cre:create_post,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
     
     new_post=Post(title=post_cre.title,content=post_cre.content,author_id=current_user.id)
        
     db.add(new_post)
     db.commit()
     db.refresh(new_post) 

     return new_post



@router.put("/post/{post_id}",response_model=PostResponse,status_code=200)
def post_put(post_id:int,post_put:create_post,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    post=get_a_post(db,post_id)
    if post is None:
        raise HTTPException(status_code=404,detail="Post not found-have a break")
    if post.author_id != current_user.id:
         raise HTTPException(status_code=403,detail="You are not allowed to update this post")
    post.title = post_put.title
    post.content = post_put.content

    db.commit()
    db.refresh(post)

    return post     
             



@router.patch("/post/{post_id}",response_model=PostResponse,status_code=200)
def patch_update(post_id:int,post_data:update_post,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    post=get_a_post(db,post_id)
    if Post.author_id != current_user:
         raise HTTPException(status_code=403,detail="You are not allowed to update this post")
    if post is None:
        raise HTTPException(status_code=404,detail="post not found")
    if post_data.title is not None:
         post.title = post_data.title
    if post_data.content is not None:
         post.content = post_data.content

    db.commit()
    db.refresh(post)
    return post

@router.delete("/post/{post_id}",status_code=204)
def post_delete(post_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    post=get_a_post(db,post_id)
    if Post.author_id != current_user:
         raise HTTPException(status_code=403,detail="You are not allowed to delete this post")
    if post is None:
         raise HTTPException(status_code=404,detail="Oh shit!!! Try providing a valid post_id....")
    if post is not None:
        db.delete(post)
        db.commit()
        return 

