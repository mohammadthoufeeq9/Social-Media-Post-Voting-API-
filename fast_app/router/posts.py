from fastapi import FastAPI
from pydantic import BaseModel
from random import randrange
from fastapi import HTTPException,Header,Cookie,Form,File,UploadFile,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.models.post import Post

router = APIRouter()

class update_post(BaseModel):#patch needs to omite few things so we create another schema with a none
     title:str | None=None
     content:str|None=None

class create_post(BaseModel):
    title:str
    content:str

#dependence
def common_limit(limit:int=5):
    return limit

#function to get all posts
def get_posts(db:Session=Depends(get_db)):
    return db.query(Post).all()

#fun to get one post
def get_a_post(db:Session,post_id:int):
    return db.query(Post).filter(Post.id==post_id).first()


@router.get("/posts")
def home(db=Depends(get_posts),limit=Depends(common_limit),notify:bool=False):
    return{
        'Message':'Here are all the posts',
        'notify':notify,
        'Posts':db[:limit]
    }



@router.get("/post/{post_id}")
def get_post_by_id(post_id:int,db:Session=Depends(get_db),detail:bool=False):
            post=get_a_post(db,post_id)
            if post is None:
                raise HTTPException(status_code=404,detail="post not found")
            return post


@router.post("/post")
def createPost(post_cre:create_post,db:Session=Depends(get_db)):
     new_post=Post(
          title=post_cre.title,
          content=post_cre.content
     )
     db.add(new_post)
     db.commit()#save it
     db.refresh(new_post) # retrieve generated values--this will refrest to create default values if not present it will give only title and content

     return new_post



@router.put("/post/{post_id}")
def post_put(post_id:int,post_put:create_post,db:Session=Depends(get_db)):
    post=get_a_post(db,post_id)
    if post is None:
        raise HTTPException(status_code=404,detail="Post not found-have a break")
    post.title = post_put.title
    post.content = post_put.content

    db.commit()
    db.refresh(post)

    return post     
             



@router.patch("/post/{post_id}")
def patch_update(post_id:int,post_data:update_post,db:Session=Depends(get_db)):
    post=get_a_post(db,post_id)
    if post is None:
        raise HTTPException(status_code=404,detail="post not found")
    if post_data.title is not None:
         post.title = post_data.title
    if post_data is not None:
         post.content = post_data.content

    db.commit()
    db.refresh(post)
    return post

@router.delete("/post/{post_id}")
def post_delete(post_id:int,db:Session=Depends(get_db)):
    post=get_a_post(db,post_id)
    if post is None:
         raise HTTPException(status_code=404,detail="Oh shit!!! Try providing a valid post_id....")
    if post is not None:
        db.delete(post)
        db.commit()
        return {"Message":"post is been deleted successfully"}

