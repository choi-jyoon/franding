from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Cart
import unittest

# Create your tests here.

class MyTestClient(Client):
    # Specialized methods for your environment
    client = Client()
    # 홍길동 이라는 유저로 테스트 진행
    response = client.post("/login/", {"username": "홍길동", "password": "a1111111a"})


   

# 클라이언트 정보를 바꿔가며 테스트 할 수 있음.
# class CartViewTest(TestCase):
#     # payment app and cart app 연결 테스트
#     def test_cart_detail(self):
#         response = self.client.get(reverse('cart:cart_detail'))
#         self.assertEqual(response.status_code, 302)
#         self.assertIn('cart', response.context)
        

#     def test_cart_add_cart(self):
#         response = self.client.get(reverse('cart:add_cart'))
#         self.assertEqual(response.status_code, 302)

    
#     def test_cart_accept_ajax(self):
#         response = self.client.get(reverse('cart:accept_ajax'))
#         self.assertEqual(response.status_code, 302) 


class CartViewTests(APITestCase):
    def test_create_product(self):
        """
        새로운 제품을 생성하고 응답을 검증합니다.
        """
        url = reverse('product-list')
        data = {'name': 'Test Product', 'price': 20}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(Cart.objects.get().name, 'Test Product')

    def test_get_product(self):
        """
        제품 목록을 가져오고 결과를 검증합니다.
        """
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)       
    

    
    

        

    
