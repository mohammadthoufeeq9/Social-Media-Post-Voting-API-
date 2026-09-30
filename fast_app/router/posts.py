from fastapi import FastAPI
from pydantic import BaseModel
from random import randrange
from fastapi import HTTPException,Header,Cookie,Form,File,UploadFile,Depends
from fastapi import APIRouter

router = APIRouter()
posts_DB=[
    {
        "title": "first_api_post",
        "content": "api",
        "id": 4604
    },{
            "title": "Mohammad Thoufeeq",
            "content": "api",
            "id": 4655
        },{
                "title": "sakamoto days",
                "content": "api",
                "id": 4404
            },{
                    "title": "Onepiece",
                    "content": "api",
                    "id": 2604
                },{
                        "title": "Fury_Toxic",
                        "content": "api",
                        "id": 4564
                    },{
                            "title": "Tony",
                            "content": "api",
                            "id": 2204
                        },{
                            "title": "Bleach",
                            "content": "api",
                            "id": 3304
                        }
]


class create_post(BaseModel):
    title:str
    content:str

#dependence
def common_limit(limit:int=5):
    return limit

@router.get("/posts")
def home(limit=Depends(common_limit),title :str |None=None,notify:bool=False):
    if title:
        filtered_title=[]
        for post in posts_DB:
            if post['title']==title:
                filtered_title.append(post)
        return filtered_title[:limit]
    return {
        "Message":"All posts are here",
        "notify":notify,
        "posts":posts_DB[:limit]}



@router.get("/post/{post_id}")
def get_post_by_id(post_id:int,detail:bool=False):

    for post in posts_DB:
        if post["id"]==post_id:
            if detail:
                return{
                    "Message":f"This is the complete information of {post['id']}-post ",
                    "id":post["id"],
                    "title":post["title"],
                    "content":post["content"]
                }
            return post
    raise HTTPException(status_code=404,detail="post not found")


@router.post("/posts")
def createPost(post:create_post):
    new_post={
        "title":post.title,
        "content":post.content,
        "id":randrange(2,10000)
    }
    posts_DB.append(new_post)
    return {"message":"post created"}



@router.put("/posts")
def put_update():
    return {"Message":"Entire post is been updated"}



@router.patch("/posts/{post_id}")
def patch_update(post_id:int,updated_post:create_post):

    for post in posts_DB:
            if post["id"]==post_id:
                post['title']=updated_post.title
                post['content']=updated_post.content
                return post
    raise HTTPException(status_code=404,detail="post not found")
    

@router.delete("/posts")
def post_delete():
    return {"Message":"post is been deleted successfully"}


@router.delete("/post/{post_id}")
def postdelets(post_id:int,delete_post=create_post):
    for post in posts_DB:
        if post["id"]==post_id:
            posts_DB.remove(post)
            return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404,detail="post not found")
