from flask import render_template, request, flash, redirect, url_for, session 
from . import products_bp
import math
from datetime import datetime,timezone

# 상품 등록
@products_bp.route("/reg_product", methods=["GET", "POST"])
def reg_product():
    # 로그인 여부 확인 
    userId = session.get('userId')
    if not userId:
        flash("로그인 후에 상품 등록이 가능합니다!")
        return redirect(url_for("auth.login"))

    # 사용자 닉네임 가져오기 
    user = products_bp.db.get_user_by_id(userId)
    nickname=user.get("nickname")

    if request.method == "GET":
        return render_template("reg_product.html", nickname=nickname)

    elif request.method == "POST":
        image_file = request.files.get("productImage")
        image_file.save(f"static/images/{image_file.filename}")
        data = request.form.to_dict()
        current_time = datetime.utcnow().isoformat() 
        data['createdAt'] = current_time 
     
    if products_bp.db.insert_product(userId, data, image_file.filename):
        flash("상품이 성공적으로 등록되었습니다!")
        return redirect(url_for("products.view_products"))
    
# 전체 상품 조회
@products_bp.route("/")
def view_products():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")
    sort_by = request.args.get("sort", "all")
    per_page = 6
    per_row = 3
    row_count = int(per_page / per_row)

    # 데이터베이스에서 상품 가져오기
    data = products_bp.db.get_products() 
    if not data:
        return render_template("products.html", total=0, datas=[], page_count=0, m=row_count)

    # 페이지네이션 처리 및 정렬
    start_idx = per_page * page
    end_idx = per_page * (page + 1)
    if category == "all":
        data = products_bp.db.get_products()
    else:
        data = products_bp.db.get_products_by_category(category)

    # 카테고리 이름 변경 
    category_names = {
    "all": "ALL",
    "fashion": "FASHION",
    "digital": "DIGITAL",
    "tableware": "TABLEWARE",
    "stationary": "STATIONARY"
    }
    current_category_name = category_names.get(category)

    # 버튼별 정렬 
    for key, value in data.items():
        # 두 필드를 모두 확인
        if "createdAt" not in value and "created_at" not in value:
            value["createdAt"] = datetime.now(timezone.utc).isoformat()
        elif "created_at" in value:
            # created_at 값을 createdAt으로 변환
            value["createdAt"] = value.pop("created_at")

    def safe_datetime(value):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError,AttributeError):
             datetime.min

    if sort_by == "recent": # 최신순
        data=dict(sorted(data.items(), key=lambda x: safe_datetime(x[1].get("createdAt","")), reverse=True))
    elif sort_by == "purchase": # 판매량순
        data = dict(sorted(data.items(), key=lambda x: int(x[1].get("purchaseCount", 0)), reverse=True))
    elif sort_by=="review": # 리뷰많은순
        data = dict(sorted(data.items(), key=lambda x: int(x[1].get("reviewCount", 0)), reverse=True))
    else:
        data=dict(sorted(data.items(), key=lambda x: x[1].get("productName",""),reverse=False))
    item_counts = len(data)
    
    # 현재 페이지 데이터
    if item_counts <= per_page:
        paginated_data = dict(list(data.items())[:item_counts])
    else:
        paginated_data = dict(list(data.items())[start_idx:end_idx])

    # 행 데이터 분리
    tot_count = len(paginated_data)
    row_data = []
    for i in range(row_count):
        if (i == row_count - 1) and (tot_count % per_row != 0):
            row_data.append(dict(list(paginated_data.items())[i * per_row:]))
        else:
            row_data.append(dict(list(paginated_data.items())[i * per_row:(i + 1) * per_row]))    
    
    # 템플릿 렌더링
    return render_template(
        "products.html",
        datas=list(paginated_data.items()),
        row1=row_data[0].items() if len(row_data) > 0 else [],
        row2=row_data[1].items() if len(row_data) > 1 else [],
        limit=per_page,
        page=page,
        page_count=int(math.ceil(item_counts / per_page)),
        total=item_counts,
        sort_by=sort_by,
        category=category,
        m=row_count,
        current_category_name=current_category_name  
    )

# 상품 상세 조회 & 상품 별 리뷰 조회
@products_bp.route("/<productId>/")
def view_product_detail(productId):
    from app.reviews.routes import reviews_bp 
    data = products_bp.db.get_product_by_id(productId)
    if not data:
        return redirect(url_for("products.view_products"))
    
    # 리뷰 데이터 가져오기 
    reviews = reviews_bp.db.get_review_by_product(productId)
    if not reviews:
        reviews =[] 

    # 리뷰 개수 계산 
    review_count = len(reviews)

    # 평균 리뷰 점수 계산 
    total_rate = sum(review['rate'] for review in reviews if review.get('rate') is not None)
    average_rate = total_rate / review_count if review_count > 0 else None 

    return render_template("product_detail.html", 
                           productId=productId, 
                           data=data, 
                           reviews= reviews,
                           review_count = review_count,
                           average_rate=average_rate)


# 상품 구매 
@products_bp.route("/<productId>/purchase_now",methods=["POST"])
def purchase_now(productId):
        
    # 로그인 여부 확인 
    user_id = session.get("userId") 
    if not user_id:
        flash("로그인 후에 상품을 구매할 수 있습니다!")
        return redirect(url_for("auth.login"))
        
    # 데이터베이스에서 해당 상품의 purchaseCount 가져오기
    data=request.form.to_dict()
    image_file=request.files.get("productImage")
    product_name = data['productName']
    product = products_bp.db.get_product_by_productName(product_name)
    if not product:
        return redirect(url_for("products.view_products"))

    # purchaseCount 업데이트
    current_count = product.get("purchaseCount", 0)
    updated_count = current_count + 1

    # 데이터베이스에 업데이트된 값 저장
    product["purchaseCount"] = updated_count
    products_bp.db.update_product(productId, product)

    # 상품 정보를 사용자의 purchasedProducts에 추가
    result = products_bp.db.add_purchased_product(user_id, data,productId)
    if result:
        flash("구매가 완료되었습니다! 구매 내역에 추가되었습니다.")
    else:
        flash("구매 처리 중 오류가 발생했습니다.")

    return redirect(url_for("products.view_product_detail",productId=productId))
