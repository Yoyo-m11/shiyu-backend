from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


DEFAULT_ITEMS = [
    {
        "id": 1,
        "name": "黑色蓝牙耳机丢失",
        "title": "黑色蓝牙耳机丢失",
        "type": "lost",
        "status": "寻物",
        "category": "数码",
        "time": "2026-04-16 10:30:00",
        "location": "图书馆三楼",
        "description": "丢失一副黑色蓝牙耳机，耳机盒有划痕，品牌是Sony",
        "similarity": 0,
        "match_reason": [],
        "match_summary": "该信息为寻物主帖，系统将根据名称、描述、地点、时间和类别进行匹配。",
        "image": "",
        "images": [],
        "contact": "13800138000"
    },
    {
        "id": 2,
        "name": "捡到黑色Sony蓝牙耳机",
        "title": "捡到黑色Sony蓝牙耳机",
        "type": "found",
        "status": "招领",
        "category": "数码",
        "time": "2026-04-16 11:00:00",
        "location": "图书馆三楼",
        "description": "在图书馆三楼自习区捡到一副黑色Sony蓝牙耳机，耳机盒有明显划痕",
        "similarity": 92,
        "match_reason": ["文本关键词高度相关", "地点高度重合", "时间接近", "类别一致"],
        "match_summary": "该物品在名称、品牌、地点、时间和外观特征上均与原始信息高度一致，属于高匹配结果。",
        "image": "",
        "images": [],
        "contact": "13900139000"
    },
    {
        "id": 3,
        "name": "捡到黑色蓝牙耳机",
        "title": "捡到黑色蓝牙耳机",
        "type": "found",
        "status": "招领",
        "category": "数码",
        "time": "2026-04-16 12:30:00",
        "location": "图书馆",
        "description": "捡到一副黑色蓝牙耳机，没有明显划痕，品牌不清楚",
        "similarity": 68,
        "match_reason": ["文本关键词相关", "地点相近", "类别一致"],
        "match_summary": "该物品与原始信息在物品名称和类别上较为接近，地点范围相近，但品牌和细节特征不完全一致，属于中匹配结果。",
        "image": "",
        "images": [],
        "contact": "13700137000"
    },
    {
        "id": 4,
        "name": "捡到白色耳机",
        "title": "捡到白色耳机",
        "type": "found",
        "status": "招领",
        "category": "数码",
        "time": "2026-04-17 09:00:00",
        "location": "教学楼A区",
        "description": "捡到一副白色耳机，型号不清楚",
        "similarity": 38,
        "match_reason": ["类别一致", "物品类型相近"],
        "match_summary": "该物品与原始信息同属耳机类物品，但颜色、地点和时间存在明显差异，属于低匹配结果。",
        "image": "",
        "images": [],
        "contact": "13600136000"
    },
    {
        "id": 5,
        "name": "捡到学生证",
        "title": "捡到学生证",
        "type": "found",
        "status": "招领",
        "category": "证件",
        "time": "2026-04-18 09:00:00",
        "location": "第一食堂",
        "description": "捡到一张学生证，名字看不清",
        "similarity": 10,
        "match_reason": ["类别不一致", "文本关键词不相关"],
        "match_summary": "该信息与耳机寻物信息类别和描述均不相关，作为干扰项用于展示系统区分能力。",
        "image": "",
        "images": [],
        "contact": "13500135000"
    },
    {
        "id": 6,
        "name": "学生证丢失",
        "title": "学生证丢失",
        "type": "lost",
        "status": "寻物",
        "category": "证件",
        "time": "2026-04-18 09:00:00",
        "location": "第一食堂",
        "description": "丢失一张学生证，可能在食堂附近",
        "similarity": 0,
        "match_reason": [],
        "match_summary": "该信息为学生证寻物主帖，系统将根据证件类别、地点和时间进行匹配。",
        "image": "",
        "images": [],
        "contact": "13900001111"
    },
    {
        "id": 7,
        "name": "拾到学生证（食堂门口）",
        "title": "拾到学生证（食堂门口）",
        "type": "found",
        "status": "招领",
        "category": "证件",
        "time": "2026-04-18 09:20:00",
        "location": "第一食堂",
        "description": "在食堂门口捡到一张学生证，时间与丢失时间非常接近",
        "similarity": 90,
        "match_reason": ["类别一致", "地点高度重合", "时间接近", "文本关键词相关"],
        "match_summary": "该招领信息与学生证寻物信息在类别、地点和时间上高度一致，属于高匹配结果。",
        "image": "",
        "images": [],
        "contact": "13900002222"
    },
    {
        "id": 8,
        "name": "捡到证件",
        "title": "捡到证件",
        "type": "found",
        "status": "招领",
        "category": "证件",
        "time": "2026-04-18 11:00:00",
        "location": "食堂附近",
        "description": "捡到一张证件，可能是学生证",
        "similarity": 63,
        "match_reason": ["类别一致", "地点相近", "文本关键词部分相关"],
        "match_summary": "该信息与学生证寻物信息类别一致，地点较为接近，但描述不够明确，属于中匹配结果。",
        "image": "",
        "images": [],
        "contact": "13900003333"
    },
    {
        "id": 9,
        "name": "拾到校园卡",
        "title": "拾到校园卡",
        "type": "found",
        "status": "招领",
        "category": "证件",
        "time": "2026-04-19 08:00:00",
        "location": "教学楼B区",
        "description": "在教学楼附近捡到一张校园卡",
        "similarity": 35,
        "match_reason": ["类别相近", "时间较远", "地点不同"],
        "match_summary": "该信息与学生证同属证件类，但具体物品、时间和地点存在差异，属于低匹配结果。",
        "image": "",
        "images": [],
        "contact": "13900004444"
    },
    {
        "id": 10,
        "name": "线性代数教材丢失",
        "title": "线性代数教材丢失",
        "type": "lost",
        "status": "寻物",
        "category": "书籍",
        "time": "2026-04-17 20:00:00",
        "location": "自习室302",
        "description": "丢失一本线性代数教材，蓝色封面，里面有笔记",
        "similarity": 0,
        "match_reason": [],
        "match_summary": "该信息为书籍类寻物主帖，系统将根据书名、地点、时间和描述特征进行匹配。",
        "image": "",
        "images": [],
        "contact": "13688889999"
    },
    {
        "id": 11,
        "name": "捡到线性代数教材",
        "title": "捡到线性代数教材",
        "type": "found",
        "status": "招领",
        "category": "书籍",
        "time": "2026-04-17 20:30:00",
        "location": "自习室302",
        "description": "捡到一本线性代数教材，蓝色封面，里面有课堂笔记",
        "similarity": 88,
        "match_reason": ["书名一致", "地点高度重合", "时间接近", "描述特征一致"],
        "match_summary": "该书籍与寻物信息在书名、封面特征、地点和时间上高度一致，属于高匹配结果。",
        "image": "",
        "images": [],
        "contact": "13677778888"
    },
    {
        "id": 12,
        "name": "捡到数学教材",
        "title": "捡到数学教材",
        "type": "found",
        "status": "招领",
        "category": "书籍",
        "time": "2026-04-17 21:00:00",
        "location": "自习室",
        "description": "捡到一本数学类教材，封面偏蓝色",
        "similarity": 58,
        "match_reason": ["类别一致", "地点相近", "文本部分相关"],
        "match_summary": "该书籍与线性代数教材在类别和地点上较为接近，但书名和细节描述不完全一致，属于中匹配结果。",
        "image": "",
        "images": [],
        "contact": "13666667777"
    },
    {
        "id": 13,
        "name": "捡到英语教材",
        "title": "捡到英语教材",
        "type": "found",
        "status": "招领",
        "category": "书籍",
        "time": "2026-04-18 09:00:00",
        "location": "教学楼A区",
        "description": "捡到一本英语教材，封面为白色",
        "similarity": 28,
        "match_reason": ["类别一致", "文本相关度低", "地点不同"],
        "match_summary": "该物品同属书籍类，但书名、地点和描述差异较大，属于低匹配结果。",
        "image": "",
        "images": [],
        "contact": "13655556666"
    }
]


USER_POSTS = []


def get_all_items():
    return DEFAULT_ITEMS + USER_POSTS


def get_item_by_id(item_id: int):
    for item in get_all_items():
        if int(item["id"]) == int(item_id):
            return item
    return None


def filter_items(type=None, category=None, location=None, keyword=None):
    items = get_all_items()

    if type:
        items = [item for item in items if item.get("type") == type]

    if category:
        items = [item for item in items if item.get("category") == category]

    if location:
        items = [item for item in items if location in item.get("location", "")]

    if keyword:
        items = [
            item for item in items
            if keyword in item.get("name", "")
            or keyword in item.get("title", "")
            or keyword in item.get("description", "")
            or keyword in item.get("location", "")
        ]

    return items


@app.get("/")
def read_root():
    return {"message": "后端启动成功"}


@app.get("/items/recommend")
def items_recommend():
    return get_all_items()


@app.get("/items/{item_id}")
def get_item_detail(item_id: int):
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="未找到物品")
    return item


@app.get("/items/match")
def items_match(itemId: int, sort_by: str = Query(default="similarity")):
    if int(itemId) == 1:
        return [DEFAULT_ITEMS[1], DEFAULT_ITEMS[2], DEFAULT_ITEMS[3], DEFAULT_ITEMS[4]]

    if int(itemId) == 6:
        return [DEFAULT_ITEMS[6], DEFAULT_ITEMS[7], DEFAULT_ITEMS[8]]

    if int(itemId) == 10:
        return [DEFAULT_ITEMS[10], DEFAULT_ITEMS[11], DEFAULT_ITEMS[12]]

    return [DEFAULT_ITEMS[1], DEFAULT_ITEMS[2], DEFAULT_ITEMS[3], DEFAULT_ITEMS[4]]


@app.post("/items/publish")
def publish_item(item: dict):
    new_id = max([i["id"] for i in get_all_items()]) + 1

    new_item = {
        "id": new_id,
        "name": item.get("name") or item.get("title") or "未命名物品",
        "title": item.get("name") or item.get("title") or "未命名物品",
        "type": item.get("type", "lost"),
        "status": "招领" if item.get("type") == "found" else "寻物",
        "category": item.get("category", "其他"),
        "time": item.get("time", ""),
        "location": item.get("location", ""),
        "description": item.get("description", ""),
        "similarity": 0,
        "match_reason": [],
        "match_summary": "用户新发布的信息，系统将根据物品类型、地点、时间和描述进行匹配。",
        "image": "",
        "images": item.get("images", []),
        "contact": item.get("contact", "")
    }

    USER_POSTS.append(new_item)
    return new_item


@app.post("/posts")
def add_post(post: dict):
    new_id = max([i["id"] for i in get_all_items()]) + 1

    new_item = {
        "id": new_id,
        "name": post.get("name") or post.get("title") or "未命名物品",
        "title": post.get("name") or post.get("title") or "未命名物品",
        "type": post.get("type", "lost"),
        "status": "招领" if post.get("type") == "found" else "寻物",
        "category": post.get("category", "其他"),
        "time": post.get("time", ""),
        "location": post.get("location", ""),
        "description": post.get("description", ""),
        "similarity": 0,
        "match_reason": [],
        "match_summary": "用户新发布的信息，系统将根据物品类型、地点、时间和描述进行匹配。",
        "image": "",
        "images": post.get("images", []),
        "contact": post.get("contact", "")
    }

    USER_POSTS.append(new_item)
    return new_item


@app.get("/posts")
def list_posts(
    type: str = Query(default=None),
    category: str = Query(default=None),
    location: str = Query(default=None),
    time_range: str = Query(default=None),
    keyword: str = Query(default=None)
):
    return filter_items(
        type=type,
        category=category,
        location=location,
        keyword=keyword
    )


@app.get("/posts/{post_id}")
def get_post_detail(post_id: int):
    item = get_item_by_id(post_id)
    if not item:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return item


@app.get("/posts/match")
def get_post_match(post_id: int, sort_by: str = Query(default="similarity")):
    return {
        "data": items_match(post_id, sort_by),
        "total": len(items_match(post_id, sort_by))
    }


@app.get("/user/items")
def user_items(contact: str):
    return [
        item for item in get_all_items()
        if item.get("contact") == contact
    ]


@app.get("/user/info")
def user_info():
    return {
        "name": "拾遇用户",
        "contact": "13800138000",
        "avatar": "",
        "publishCount": 3,
        "matchCount": 6
    }


@app.get("/user/messages")
def user_messages():
    return [
        {
            "id": 1,
            "title": "有新的匹配结果",
            "content": "系统为你的黑色蓝牙耳机找到了高匹配招领信息",
            "is_read": False,
            "time": "2026-04-22 22:00:00"
        },
        {
            "id": 2,
            "title": "匹配结果已更新",
            "content": "系统根据时间与地点信息重新排序了候选结果",
            "is_read": False,
            "time": "2026-04-22 22:10:00"
        }
    ]


@app.post("/claims")
def create_claim(claim: dict):
    return {
        "message": "申请已提交",
        "post_id": claim.get("post_id"),
        "claimer_contact": claim.get("claimer_contact"),
        "status": "submitted"
    }


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
