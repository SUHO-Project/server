from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .forms import *
import json
from .stt import *
import speech_recognition as sr

def create(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            menu_name = form.cleaned_data['menuName']
            menu_quantity = form.cleaned_data['menuQuantity']
            option1 = form.cleaned_data['option1']
            option2 = form.cleaned_data['option2'] if form.cleaned_data['option2'] != "null" else "기본"

            try:
                menu = Menu.objects.get(menuName=menu_name)

                try:
                    cart_item = Cart.objects.get(menu=menu, option1=option1, option2=option2)

                    # Increase the quantity
                    cart_item.menuQuantity += menu_quantity

                    # Update totalPrice
                    cart_item.totalPrice = (cart_item.menuQuantity * menu.menuPrice)  # Total price based on updated quantity
                    if option2 == "샷추가":
                        cart_item.totalPrice += 500 * cart_item.menuQuantity  # 샷 추가 가격
                    elif option2 == "2샷추가":
                        cart_item.totalPrice += 1000 * cart_item.menuQuantity  # 2샷 추가 가격

                    cart_item.save()

                except Cart.DoesNotExist:
                    # Create new cart item
                    total_price = (menu.menuPrice * menu_quantity)  # Initial total price based on quantity
                    if option2 == "샷추가":
                        total_price += 500 * menu_quantity  # 샷 추가 가격
                    elif option2 == "2샷추가":
                        total_price += 1000 * menu_quantity  # 2샷 추가 가격

                    Cart.objects.create(
                        menu=menu,
                        menuQuantity=menu_quantity,
                        option1=option1,
                        option2=option2,
                        totalPrice=total_price
                    )

                return JsonResponse({'message': 'Cart updated successfully!'}, status=200)

            except Menu.DoesNotExist:
                return JsonResponse({'error': 'Menu not found'}, status=404)
    else:
        form = CartForm()

    return JsonResponse({'error': 'Invalid form data'}, status=400)

@csrf_exempt
def detail(request, cartId):
    if request.method == 'DELETE':
        try:
            Cart.objects.filter(id=cartId).delete()
            return JsonResponse({'message': 'Cart deleted successfully!'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Menu not found'}, status=404)
    elif request.method == 'PUT':
        try:
            updateCart = Cart.objects.get(id=cartId)
            data = json.loads(request.body)
            updateQuantity = data.get('quantity', 0)

            # Update the quantity and total price
            updateCart.menuQuantity += updateQuantity

            # Calculate the new total price based on the updated quantity
            updateCart.totalPrice = (updateCart.menuQuantity * updateCart.menu.menuPrice)

            if updateCart.option2 == "샷추가":
                updateCart.totalPrice += 500 * updateCart.menuQuantity  # 샷 추가 가격
            elif updateCart.option2 == "2샷추가":
                updateCart.totalPrice += 1000 * updateCart.menuQuantity  # 2샷 추가 가격

            if updateCart.menuQuantity <= 0:
                updateCart.delete()
            else:
                updateCart.save()

            return JsonResponse({'message': 'Cart updated successfully!'}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Menu not found'}, status=404)
    
        
# 메인 실행
r = sr.Recognizer()
m = sr.Microphone()

@csrf_exempt
def speakApi(request):
    page = json.loads(request.body).get("page")
    message = json.loads(request.body).get('question')
    answer = ""
    if page == "kiosk":
        answer = returnSpeak(message)
    elif page == "cafemain":
        answer = returnCafeMainSpeak(message)
    elif page == "popup1":
        answer = popup1(message)
    return JsonResponse({'message': answer}, status=200)
        

def returnSpeak(message):
    speak(message)
    answer = listen(r)
    if "카페" in answer or "커피" in answer:
        return answer
    else:
        returnSpeak('없는 메뉴를 선택하셨어요. 다시 선택해 주세요.')

def returnCafeMainSpeak(message):
    speak(message)
    answer = listen(r).replace(" ","")
    if "아메리카노" in answer:
        return "americano"
    elif "카페라떼" in answer:
        return "cafe-latte"
    elif "바닐라라떼" in answer:
        return "valina-latte"
    elif "카라멜마끼아또" in answer:
        return "caramel-macchiato"
    elif "카페모카" in answer:
        return "cafe-mocha"
    elif "카푸치노" in answer:
        return "cappuccino"
    else:
        returnCafeMainSpeak('없는 메뉴를 선택하셨어요. 다시 선택해 주세요.')

def popup1(message):
    speak(message)
    answer = listen(r).replace(" ", "")
    if "아이스" in answer:
        return "TemSelect2"
    elif "핫" in answer:
        return "TemSelect1"
    else:
        popup1('없는 옵션을 선택하셨어요. 다시 선택해 주세요.')