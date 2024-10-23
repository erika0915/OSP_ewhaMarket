function goToPage(page) {
    if (page === '전체상품') {
      window.location.href = 'page/all_products.html'; // 전체 상품 페이지로 이동
    } 
    else if (page === '신상품') {
      window.location.href = 'page/new_products.html'; // 신상품 페이지로 이동
    }
    else if (page === '리뷰 조회') {
        window.location.href = 'page/view_review.html'; // 리뷰 조회 페이지로 이동
    }
    else if (page === '마이페이지') {
        window.location.href = 'page/my_page.html'; //  마이페이지로 이동
    }
  }