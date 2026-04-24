from models import User, Post
from datetime import datetime, timedelta
import json
import re

def create_user(db, user):
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db, user):
    return db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()

def serialize_post(post):
    return {
        "id": post.id,
        "title": post.title,
        "type": post.type,
        "category": post.category,
        "time": post.time,
        "location": post.location,
        "description": post.description,
        "images": json.loads(post.images) if post.images else [],
        "contact": post.contact,
        "status": post.status,
        "similarity": post.similarity if post.similarity is not None else 0.0,
        "match_reason": json.loads(post.match_reason) if post.match_reason else [],
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }

def create_post(db, post):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_post = Post(
        title=post.title,
        type=post.type,
        category=post.category,
        time=post.time,
        location=post.location,
        description=post.description,
        images=json.dumps(post.images, ensure_ascii=False),
        contact=post.contact,
        status="active",
        similarity=0.0,
        match_reason=json.dumps([], ensure_ascii=False),
        created_at=now,
        updated_at=now
    )    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return serialize_post(db_post)

def get_posts(db, type=None, category=None, location=None, time_range=None, keyword=None):
    query = db.query(Post)
    if keyword:
        query = query.filter(
            (Post.title.contains(keyword)) |
            (Post.description.contains(keyword)) |
            (Post.location.contains(keyword))
    )
    if type:
        query = query.filter(Post.type == type)

    if category:
        query = query.filter(Post.category == category)

    if location:
        query = query.filter(Post.location.contains(location))

    posts = query.all()

    if time_range:
        day_map = {
            "3days": 3,
            "7days": 7,
            "14days": 14,
            "30days": 30
        }
        days = day_map.get(time_range)

        if days:
            filtered_posts = []
            now = datetime.now()
            for post in posts:
                try:
                    post_time = datetime.strptime(post.time, "%Y-%m-%d %H:%M:%S")
                    if now - post_time <= timedelta(days=days):
                        filtered_posts.append(post)
                except ValueError:
                    pass
            posts = filtered_posts

    return [serialize_post(post) for post in posts]

def get_post_by_id(db, post_id):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None
    return serialize_post(post)

def get_posts_by_contact(db, contact):
    posts = db.query(Post).filter(Post.contact == contact).all()
    return [serialize_post(post) for post in posts]


def get_my_match_posts(db, contact):
    my_posts = db.query(Post).filter(Post.contact == contact).all()
    result = []

    for post in my_posts:
        match_result = get_match_posts(db, post.id)

        if match_result is None:
            continue

        result.append({
            "source_post": {
                "id": post.id,
                "title": post.title,
                "type": post.type,
                "category": post.category
            },
            "match_total": match_result["total"],
            "matches": match_result["data"]
        })

    return result
# ========== 匹配逻辑开始 ==========

def normalize_text(text):
    if not text:
        return ""
    return text.lower().strip()

def tokenize(text):
    """
    简化版关键词提取：
    1. 提取中英文数字片段
    2. 去掉太短的词
    """
    text = normalize_text(text)
    tokens = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z0-9]+', text)
    return [t for t in tokens if len(t) >= 1]

def calc_text_score(post_a, post_b):
    text_a = f"{post_a.title} {post_a.description}"
    text_b = f"{post_b.title} {post_b.description}"

    keywords_a = set(tokenize(text_a))
    keywords_b = set(tokenize(text_b))

    if not keywords_a or not keywords_b:
        return 0.0

    overlap = keywords_a.intersection(keywords_b)
    overlap_count = len(overlap)

    base_score = 0.0
    if overlap_count >= 3:
        base_score = 0.8
    elif overlap_count >= 2:
        base_score = 0.7
    elif overlap_count == 1:
        base_score = 0.45
    else:
        base_score = 0.0

    title_a = normalize_text(post_a.title)
    title_b = normalize_text(post_b.title)

    # 核心物品词一致时，给更自然的加成：最高抬到 0.8
    core_items = ["耳机", "学生证", "校园卡", "钥匙", "水杯", "书", "证件"]
    for item in core_items:
        if item in title_a and item in title_b:
            base_score = max(base_score, 0.75)
            break

    return base_score

def calc_location_score(location_a, location_b):
    a = normalize_text(location_a)
    b = normalize_text(location_b)

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    if a in b or b in a:
        return 0.8

    return 0.0

def calc_time_score(time_a, time_b):
    try:
        dt_a = datetime.strptime(time_a, "%Y-%m-%d %H:%M:%S")
        dt_b = datetime.strptime(time_b, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return 0.0

    diff_days = abs((dt_a - dt_b).total_seconds()) / (24 * 3600)

    if diff_days <= 3:
        return 1.0
    elif diff_days <= 7:
        return 0.7
    elif diff_days <= 14:
        return 0.4
    return 0.1

def calc_category_score(category_a, category_b):
    if not category_a or not category_b:
        return 0.0
    return 1.0 if category_a == category_b else 0.0

def calc_image_score(images_a, images_b):
    """
    轻量图像特征版本：
    - 双方都有图：给基础分
    - 文件名有相同片段：更高一点
    """
    if not images_a or not images_b:
        return 0.0

    names_a = [img.split("/")[-1].lower() for img in images_a]
    names_b = [img.split("/")[-1].lower() for img in images_b]

    for a in names_a:
        for b in names_b:
            if a == b:
                return 1.0
            if a in b or b in a:
                return 0.8

    return 0.6

def build_match_reason(text_score, location_score, time_score, category_score, image_score, post_a, post_b):
    reasons = []

    if text_score >= 0.7:
        keywords_a = set(tokenize(f"{post_a.title} {post_a.description}"))
        keywords_b = set(tokenize(f"{post_b.title} {post_b.description}"))
        overlap = keywords_a.intersection(keywords_b)
        if overlap:
            reasons.append(f"文本关键词高度相关（{' / '.join(list(overlap)[:3])}）")
        else:
            reasons.append("文本关键词相关")

    if location_score >= 0.7:
        reasons.append(f"地点高度重合（{post_a.location}）")

    if time_score >= 0.7:
        reasons.append("时间接近（近期）")

    if category_score == 1.0:
        reasons.append(f"类别一致（{post_a.category}）")

    if image_score >= 0.6:
        reasons.append("图像特征相似")

    return reasons

def build_match_summary(text_score, location_score, time_score, category_score, image_score):
    strong_points = []

    if text_score >= 0.7:
        strong_points.append("关键词描述")
    if location_score >= 0.7:
        strong_points.append("地点信息")
    if time_score >= 0.7:
        strong_points.append("时间接近度")
    if category_score >= 1.0:
        strong_points.append("物品类别")
    if image_score >= 0.4:
        strong_points.append("图片特征")

    if not strong_points:
        return "系统检测到部分基础特征存在关联，建议结合实际情况进一步核验。"

    return f"系统综合比对了{'、'.join(strong_points)}，当前结果与原始信息匹配度较高。"

def apply_time_range_filter(posts, time_range):
    if not time_range:
        return posts

    day_map = {
        "3days": 3,
        "7days": 7,
        "14days": 14,
        "30days": 30
    }
    days = day_map.get(time_range)
    if not days:
        return posts

    now = datetime.now()
    filtered = []

    for post in posts:
        try:
            post_time = datetime.strptime(post.time, "%Y-%m-%d %H:%M:%S")
            if now - post_time <= timedelta(days=days):
                filtered.append(post)
        except ValueError:
            pass

    return filtered

def get_match_posts(db, post_id, time_range=None, category=None, location=None, sort_by="similarity"):
    current_post = db.query(Post).filter(Post.id == post_id).first()
    if not current_post:
        return None

    target_type = "found" if current_post.type == "lost" else "lost"

    query = db.query(Post).filter(
        Post.type == target_type,
        Post.id != post_id
    )

    if category:
        query = query.filter(Post.category == category)

    if location:
        query = query.filter(Post.location.contains(location))

    candidate_posts = query.all()
    candidate_posts = apply_time_range_filter(candidate_posts, time_range)

    result = []

    current_images = json.loads(current_post.images) if current_post.images else []

    for post in candidate_posts:
        target_images = json.loads(post.images) if post.images else []

        text_score = calc_text_score(current_post, post)
        location_score = calc_location_score(current_post.location, post.location)
        time_score = calc_time_score(current_post.time, post.time)
        category_score = calc_category_score(current_post.category, post.category)
        image_score = calc_image_score(current_images, target_images)

        similarity = (
            text_score * 0.35 +
            location_score * 0.25 +
            time_score * 0.20 +
            category_score * 0.10 +
            image_score * 0.10
        )

        similarity = round(similarity, 2)

        if similarity < 0.35:
            continue

        match_reason = build_match_reason(
            text_score,
            location_score,
            time_score,
            category_score,
            image_score,
            current_post,
            post
        )

        item = serialize_post(post)
        item["similarity"] = similarity
        item["match_reason"] = match_reason
        item["match_summary"] = build_match_summary(
            text_score,
            location_score,
            time_score,
            category_score,
            image_score
        )
        item["score_detail"] = {
            "text_score": round(text_score, 2),
            "location_score": round(location_score, 2),
            "time_score": round(time_score, 2),
            "category_score": round(category_score, 2),
            "image_score": round(image_score, 2)
        }
        item["_sort_scores"] = {
    "similarity": similarity,
    "time": time_score,
    "location": location_score,
    "category": category_score
}

        result.append(item)

    if sort_by not in ["similarity", "time", "location", "category"]:
        sort_by = "similarity"

    result.sort(key=lambda x: x["_sort_scores"][sort_by], reverse=True)
    result = result[:3]

# 返回前把临时排序字段删掉
    for item in result:
        item.pop("_sort_scores", None)

    return {
        "data": result,
        "total": len(result)
}