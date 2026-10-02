from sqlalchemy import or_,and_
from fastapi import HTTPException,Header,Cookie,Form,File,UploadFile,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.models.post import Post

from schemas.post import(
     create_post,update_post,PostResponse,PostsResponse
)

router = APIRouter()

#function to get all posts with a limit, title filter,search,pagination,or_,and_,des-aes,
def get_posts(
    limit: int = 5,
    title: str | None = None,
    search:str|None=None,
    published:bool|None=None,
    offset:int=0,
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

    # query = query.filter(
    #     and_(
    #         Post.published == True,
    #         Post.title.ilike("%naruto%")
    #     )
    # )

    if published is not None:
        query= query.filter(Post.published == published)
    query=query.order_by(Post.created_at.desc())

    return query.offset(offset).limit(limit).all()



#fun to get one post
def get_a_post(db:Session,post_id:int):
    return db.query(Post).filter(Post.id==post_id).first()


@router.get("/posts",response_model=PostsResponse)
def home(db=Depends(get_posts),notify:bool=False):
    return{
        'Message':'Here are all the posts',
        'notify':notify,
        'Posts':db
    }


@router.get("/post/{post_id}",response_model=PostResponse)
def get_post_by_id(post_id:int,db:Session=Depends(get_db),detail:bool=False):
            post=get_a_post(db,post_id)
            if post is None:
                raise HTTPException(status_code=404,detail="post not found")
            return post


@router.post("/post",response_model=PostResponse,status_code=201)
def createPost(post_cre:create_post,db:Session=Depends(get_db)):
     new_post=Post(
          title=post_cre.title,
          content=post_cre.content
     )
     db.add(new_post)
     db.commit()#save it
     db.refresh(new_post) # retrieve generated values--this will refrest to create default values if not present it will give only title and content

     return new_post



@router.put("/post/{post_id}",response_model=PostResponse,status_code=200)
def post_put(post_id:int,post_put:create_post,db:Session=Depends(get_db)):
    post=get_a_post(db,post_id)
    if post is None:
        raise HTTPException(status_code=404,detail="Post not found-have a break")
    post.title = post_put.title
    post.content = post_put.content

    db.commit()
    db.refresh(post)

    return post     
             



@router.patch("/post/{post_id}",response_model=PostResponse,status_code=200)
def patch_update(post_id:int,post_data:update_post,db:Session=Depends(get_db)):
    post=get_a_post(db,post_id)
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
def post_delete(post_id:int,db:Session=Depends(get_db)):
    post=get_a_post(db,post_id)
    if post is None:
         raise HTTPException(status_code=404,detail="Oh shit!!! Try providing a valid post_id....")
    if post is not None:
        db.delete(post)
        db.commit()
        return 

