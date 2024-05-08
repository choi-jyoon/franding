from django.test import TestCase, Client
from django.urls import reverse
import unittest

# Create your tests here.

class MyTestClient(Client):
    # Specialized methods for your environment
    client = Client()
    # 홍길동 이라는 유저로 테스트 진행
    response = client.post("/login/", {"username": "홍길동", "password": "a1111111a"})


# model.py test 진행
class CartModelTest(TestCase):
    pass
   

# 클라이언트 정보를 바꿔가며 테스트 할 수 있음.
class CartViewTest(TestCase):
    # payment app and cart app 연결 테스트
    def test_cart_detail(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', response.context)
        

    def test_cart_add_cart(self):
        response = self.client.get(reverse('cart:add_cart'))
        self.assertEqual(response.status_code, 302)

    
    def test_cart_accept_ajax(self):
        response = self.client.get(reverse('cart:accept_ajax'))
        self.assertEqual(response.status_code, 302) 

        
    

    
    

        

    
