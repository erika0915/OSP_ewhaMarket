from flask import render_template, request, flash, redirect, url_for, session
from . import market_bp

# 마켓랭킹 페이지 
@market_bp.route("/")
def view_marketRanking(): 
    products = market_bp.db.get_products() 
    # 사용자별 등록 상품의 구매 수 집계
    user_purchase_count = {}
    for productId, product_data in products.items():
        userId = product_data.get("userId")
        purchase_count = product_data.get("purchaseCount", 0)
        if userId:
            user_purchase_count[userId] = user_purchase_count.get(userId, 0) + purchase_count
        print(userId, ":" , user_purchase_count[userId])

    # 마켓별 등록 상품 개수 상위 3명 
    sorted_users = sorted(user_purchase_count.items(), key=lambda x: x[1], reverse=True)
    print("sorted_users:", sorted_users) 
    
    # 상위 3명의 닉네임, 상품 목록, 상품 이미지 가져오기
    ranking_user_data = []
    for userId, product_count in sorted_users:
        user_info = market_bp.db.get_user_info(userId)
        nickname = user_info.get("nickname") if user_info else "Unknown"
        sell_list = market_bp.db.get_sell_list(userId)


        ranking_user_data.append({"nickname": nickname, "sellList": sell_list})
        print("ranking_user_data", ranking_user_data)
    
    # 데이터를 템플릿으로 전달
    return render_template("market.html", ranking_user_data=ranking_user_data, sorted_users=sorted_users, nickname=nickname, sellList=sell_list)
    
# 특정 사용자 마이페이지 조회
@market_bp.route("/mypage/<nickname>/")
def view_user_mypage(nickname):
    # 닉네임으로 사용자 정보 조회
    userInfo = market_bp.db.get_user_info_by_nickname(nickname)

    userId = userInfo.get("userId")
    purchasedList = market_bp.db.get_purchased_list(userId)
    sellList = market_bp.db.get_sell_list(userId)
    likedList = market_bp.db.get_heart_list(userId)
    
    return render_template("mypage.html",
                           userInfo=userInfo,
                           profileImage=userInfo.get("profileImage"),
                           purchasedList=purchasedList,
                           sellList=sellList,
                           likedList=likedList)
