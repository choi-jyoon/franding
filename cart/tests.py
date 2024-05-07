from django.test import TestCase, Client


# Create your tests here.

class MyTestClient(Client):
    # Specialized methods for your environment
    client = Client()
    # 홍길동 이라는 유저로 테스트 진행
    response = client.post("/account/", {"username": "홍길동", "password": "a1111111a"})
    print(response.status_code)


# 클라이언트 정보를 바꿔가며 테스트 할 수 있음.
class SimpleTest(TestCase):
    # payment app and cart app 연결 테스트
    def test_cart_connection(self):
        response = self.client.get("/cart/detail/")
        self.assertEqual(response.status_code, 302)

    def test_payment_connection(self):
        response = self.client.get("/payment/")
        self.assertEqual(response.status_code, 302)

    
