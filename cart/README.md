### 뉴비를 위한 뉴비 친화적인 향수 사이트

1. 뉴비 친화적인 카테고리 분류법
- 카테고리 속에 카테고리 등등 엄청 복잡하게 꼬일 수 있다. 그 속에서 중복되는 카테고리를 어떻게 쉽게 구별하게 할 수 있을지?

2. 향수 사진 이미지를 생성해주는 ai이미지 생성기 만들면 어떨까?

3. 각 향의 대표적인 베스트 셀러 향수(추천 기능에 넣자.)

4. 고객이 어떻게 하면 그 향을 머릿 속에 그려볼 수 있을 지 고민

5. 뉴비 웰컴 킷 : 대표적인 향의 시향지를 보내주고 골라봐 기능

6. 처음 향수를 입문하는 자들을 위한 쉬운 용어

7. 매일 구독 서비스.....(아주 나중에...)

8. 검색 서비스를 뉴비 친화적으로 어떻게 만들 수 있을 것인가?


### 선택 결제 구현 구상

1. 체크 박스를 체크한다.
- bootstarp checkbox option

2. 장바구니에서 user와 check된 상품 품목 list를 가져온다.
- request.GET.getlist()

3. 가져온 list 품목의 값들을 모두 더해준다.
- for문 

4. 더한 값을 결제 페이지로 넘겨준다
- context = ['total'] : total_price
- render(context)

4. 결제 페이지에서 확인한다.
- 

# 일단 for문을 돌려야 되거든?
        # 일단 checkobx_item값이 ['9', '5'] 이런 식이야.
        # 그럼 이걸 for문을 돌려서 item_list에 있는 값들을 가져오고
        # request.GET.getlist('checkbox')[0]이게 str형태라서 int로 바꿔줘야 돼.
        # Cart.objects.filter에서 item.id를 가져와서 그 값이 checkbox_item에 있는 값이랑 같으면
        # total_price에 더해주면 되는데
        # c.item.price * c.amount 연산을 해주고,
        # 그걸 템플릿으로 넘겨줘야 돼.

        # 여기서 어떤 에러가 날 수 있을까?
        # 체크 품목에 값이 안 들어올 수 있을 것 같다...


### 수정 사항
    # payment_list(request, total_price=0)에서
    # item_list = Cart.objects.filter(user=request.user, status=False).order_by('user', '-status', '-id') 이거 지웠음
    # 왜냐하면 값을 전부 보내는 것이 아니라 특정한(체크된) 값을 보내기 위해서임.

    for check in checkbox_item:   
        try:
            # 만약 check가 숫자가 아니라면 ValueError가 발생
            check = int(check)   
        except ValueError: 
            print('선택된 상품이 없습니다.') 
            
        check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        check_item_list.append(check_item)
        total_price += (check_item.item.price * check_item.amount)

    # 위는 수정된 코드임
    # try except 구문으로 예외를 바로 체크할 수 있도록 했고
    check_item = Cart.objects.get(user=request.user, item=check, status=False) 
        check_item_list.append(check_item)
    # 로 체크된 특정 값만 보낼 수 있도록 구성했음.