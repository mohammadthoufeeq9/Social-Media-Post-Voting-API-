from sqlalchemy import or_,and_
from fastapi import HTTPException,Header,Cookie,Form,File,UploadFile,Depends
from fastapi import APIRouter

from sqlalchemy.orm import Session
from fastapi import Depends

from fast_app.database.database import get_db
from fast_app.models.post import Post,User

from fast_app.schemas.post import(
     create_post,update_post,PostResponse,PostsResponse,UserCreate,UserResponse,UserLogin
)
from fast_app.utils.password import verify_hash,hash_password
from fast_app.utils.auth import create_access_token,get_current_user,test_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import BackgroundTasks

router = APIRouter()

#function to get all posts with a limit, title filter,search,pagination,or_,and_,des-aes,
def get_posts(
    limit: int = 5,
    title: str | None = None,
    search:str|None=None,
    published:bool|None=None,
    page:int=0,
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

    return query.offset(offset).limit(limit).all()

#fun to get one post
def get_a_post(db:Session,post_id:int):
    return db.query(Post).filter(Post.id==post_id).first()

#get admin by current user
def get_current_user_admin(current_user=Depends(get_current_user)):
     if not current_user.is_admin:
          raise HTTPException(status_code=403,detail="Admin access required")
     return current_user

@router.get("/admin")
def get_admin(current_user=Depends(get_current_user_admin)):
     return {
          "Message":"Welcome admin",
          "User":current_user.username
     }


#router for user Registration
@router.post("/register",response_model=UserResponse,status_code=201)
def reg(user_data:UserCreate,db:Session=Depends(get_db)):
     new_user=User(
          username=user_data.username,
          email=user_data.email,
          password=hash_password(user_data.password)
     )
     db.add(new_user)
     db.commit()
     db.refresh(new_user)

     return new_user

#router for login
@router.post("/login")
def login(user_detail:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
     print("USERNAME:", user_detail.username)
     print("PASSWORD RECEIVED:", bool(user_detail.password))
     user=db.query(User).filter(User.email == user_detail.username).first()

     print("USER FOUND:", user is not None)

     if user is not None:
          if verify_hash(user_detail.password,user.password):
               token=create_access_token({
                    "user_id":user.id
               })
               return {
                    "Message":"Login Successfull",
                    "access_token":token,
                    "Token_type":"bearer"
               }
          raise HTTPException(status_code=401,detail="Invalid email or password")
     raise HTTPException(status_code=401,detail="Invalid email or password")


@router.get("/posts",response_model=PostsResponse)
def home(current_user=Depends(get_current_user),posts=Depends(get_posts),notify:bool=False):
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


@router.post("/post",response_model=PostResponse,status_code=201)
def createPost(post_cre:create_post,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
     
     new_post=Post(title=post_cre.title,content=post_cre.content,author_id=current_user.id)
        
     db.add(new_post)
     db.commit()#save it
     db.refresh(new_post) # retrieve generated values--this will refrest to create default values if not present it will give only title and content

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

