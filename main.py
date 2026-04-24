from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi import HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base
from schemas import UserCreate, UserLogin, PostCreate, ClaimCreate
from crud import (
    create_user,
    login_user,
    create_post,
    get_posts,
    get_post_by_id,
    get_match_posts,
    get_posts_by_contact,
    get_my_match_posts
)
import os
import shutil
import uuid

app = FastAPI()

def map_post_to_item(post_dict):
    images = post_dict.get("images") or []
    image = images[0] if images else ""

    sim = post_dict.get("similarity", 0)
    similarity = int(sim * 100) if sim <= 1 else int(sim)

    type_val = post_dict.get("type")
    status = "招领" if type_val == "found" else "寻物"

    return {
        "id": str(post_dict.get("id")),
        "name": post_dict.get("title"),
        "type": type_val,
        "status": status,
        "category": post_dict.get("category"),
        "time": post_dict.get("time"),
        "location": post_dict.get("location"),
        "description": post_dict.get("description"),
        "similarity": similarity,
        "image": image,
        "images": images,
        "contact": post_dict.get("contact")
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "后端启动成功"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = login_user(db, user)
    if not db_user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {
        "message": "登录成功",
        "user_id": db_user.id,
        "username": db_user.username
    }

@app.post("/posts")
def add_post(post: PostCreate, db: Session = Depends(get_db)):
    return create_post(db, post)

@app.get("/posts")
def list_posts(
    type: str = Query(default=None),
    category: str = Query(default=None),
    location: str = Query(default=None),
    time_range: str = Query(default=None),
    keyword: str = Query(default=None),
    db: Session = Depends(get_db)
):
    return get_posts(
        db,
        type=type,
        category=category,
        location=location,
        time_range=time_range,
        keyword=keyword
    )

@app.get("/posts/match")
def get_post_match(
    post_id: int,
    time_range: str = Query(default=None),
    category: str = Query(default=None),
    location: str = Query(default=None),
    sort_by: str = Query(default="similarity"),
    db: Session = Depends(get_db)
):
    result = get_match_posts(
    db=db,
    post_id=post_id,
    time_range=time_range,
    category=category,
    location=location,
    sort_by=sort_by
)
    if result is None:
        raise HTTPException(status_code=404, detail="原始帖子不存在")
    return result

@app.get("/posts/my")
def get_my_posts(contact: str, db: Session = Depends(get_db)):
    return get_posts_by_contact(db, contact)

@app.get("/posts/my/match")
def get_my_matches(contact: str, db: Session = Depends(get_db)):
    return get_my_match_posts(db, contact)

@app.get("/posts/{post_id}")
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return post

# ================== items接口 ==================

@app.get("/items/recommend")
def items_recommend(db: Session = Depends(get_db)):
    posts = get_posts(db)
    return [map_post_to_item(p) for p in posts[:5]]


@app.post("/items/publish")
def publish_item(item: dict, db: Session = Depends(get_db)):
    data = {
        "title": item.get("name"),
        "type": item.get("type"),
        "category": item.get("category"),
        "time": item.get("time"),
        "location": item.get("location"),
        "description": item.get("description"),
        "images": item.get("images", []),
        "contact": item.get("contact")
    }

    new_post = create_post(db, data)
    return map_post_to_item(new_post)


@app.get("/items/match")
def items_match(itemId: int, sort_by: str = Query(default="similarity"), db: Session = Depends(get_db)):
    match_result = get_match_posts(db=db, post_id=itemId, sort_by=sort_by)

    if match_result is None:
        raise HTTPException(status_code=404, detail="物品不存在")

    return [map_post_to_item(p) for p in match_result["data"]]


@app.get("/items/{item_id}")
def get_item_detail(item_id: int, db: Session = Depends(get_db)):
    post = get_post_by_id(db, item_id)
    if not post:
        raise HTTPException(status_code=404, detail="未找到物品")

    item = map_post_to_item(post)
    return item


# ================== user接口 ==================

@app.get("/user/items")
def user_items(contact: str, db: Session = Depends(get_db)):
    posts = get_posts_by_contact(db, contact)
    return [map_post_to_item(p) for p in posts]


@app.get("/user/info")
def user_info():
    return {
        "name": "用户",
        "contact": "13800138000",
        "avatar": "",
        "publishCount": 3,
        "matchCount": 2
    }


@app.get("/user/messages")
def user_messages():
    return [
        {
            "id": 1,
            "title": "有新的匹配结果",
            "content": "系统为你的物品找到了新的匹配信息",
            "is_read": False,
            "time": "2026-04-22 22:00:00"
        }
    ]

@app.post("/upload")
def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join("uploads", filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "上传成功",
        "filename": filename,
        "image_url": f"/uploads/{filename}"
    }

@app.post("/claims")
def create_claim(claim: ClaimCreate):
    return {
        "messagex": "申请已提交",
        "post_id": claim.post_id,
        "claimer_contact": claim.claimer_contact,
        "status": "submitted"
    }