from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder

from django.db.models import Q

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required

from .form import UserForm


def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('store')
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('store')
        else:
            messages.error(request,"username or password does not exist")

    context={'page':page,'cartItems':cartData(request)['cartItems']}
    return render(request,'store/login_register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('store')

def registerPage(request):
    form=UserCreationForm()
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user= form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('store')
        else:
            messages.error(request,'An error occured during Registration')

    return render(request,'store/login_register.html',{'form':form,'cartItems':cartData(request)['cartItems']})



def userProfile(request,pk):
    user= User.objects.get(id=pk)
    customer = Customer.objects.get(user=user)
    orders=Order.objects.filter(customer=customer)
    reviews=Review.objects.filter(customer=customer)
	
    # if request.user!=customer.user:
    #     return HttpResponse('You are not allowed here!!!')
          
    context={'user':user,'orders':orders,'cartItems':cartData(request)['cartItems'],'reviews':reviews}
    return render(request,'store/profile.html',context)

@login_required(login_url='login')
def orderDetails(request,pk):
    order=Order.objects.get(id=pk)
    orderItems=OrderItem.objects.filter(order=order)
    
    if request.user!=order.customer.user:
        return HttpResponse('You are not allowed here!!!')
	
    context={'orderItems':orderItems,'order':order}
    return render(request,'store/order_details.html',context)





def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	#products = Product.objects.all()
	q=request.GET.get('q') if request.GET.get('q') !=None else ''
	products=Product.objects.filter(
        Q(name__icontains=q)|
        Q(description__icontains=q)
		)

	product_count=products.count()
	context = {'products':products, 'cartItems':cartItems,'product_count':product_count}
	return render(request, 'store/store.html', context)



def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
      
	if cartItems < 1:
		messages.error(request, 'Cart is empty!!! first add something to the cart') 
		return redirect('store')
    
	print(request.method)
	if request.method=='POST':
		shippingAddress=ShippingAddress.objects.create(
            customer=request.user.customer,
            order=Order.objects.get(customer=request.user.customer,complete=False),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zipcode=request.POST.get('zipcode')
		)
		order=Order.objects.get(customer=request.user.customer,complete=False)
		order.complete=True
		order.save()
		print("address added")
		return redirect('user-profile',request.user.customer.id)

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	order.transaction_id=str(10000000000000 + order.id)
	order.save()

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

#mycode starts
def productDescripton(request,pk):
	product = Product.objects.get(id=pk)
	product_images=ProductImages.objects.filter(product=product) #my code
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
    
	context={'product':product, 'cartItems':cartItems}
    
	#mycode starts
	
	product_reviews=product.review_set.all()
	if request.method=='POST':
		review=Review.objects.create(
            customer=request.user.customer,
            product=product,
            body=request.POST.get('body')
		)

	context['product_reviews']=product_reviews
	context['product_images']=product_images
      
	#mycode end
	
	return render(request, 'store/product_description.html', context) 


# @login_required(login_url='login')
# def updateUser(request):
#     user=request.user
#     form=UserForm(instance=user)

#     if request.method=='POST':
#         form=UserForm(request.POST,instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect('user-profile',pk=user.id)

#     return render(request,'store/update_user.html',{'form':form})

@login_required(login_url='login')
def updateUser(request,pk):
    customer=Customer.objects.get(id=pk)
    form=UserForm(instance=customer)
    
    if request.user!=customer.user:
        return HttpResponse('You are not allowed!!')


    if request.method=='POST':
        customer.name=request.POST.get('name')
        customer.email=request.POST.get('email')
        customer.save()
        return redirect('store')

    context={'form':form,'customer':customer}
    return render(request,'store/update_user.html',context)


@login_required(login_url='login')
def deleteReview(request,pk):
    review=Review.objects.get(id=pk)
    if request.user!=review.customer.user:
        return HttpResponse('You are not allowed!!')

    if request.method=='POST':
        review.delete()
        return redirect('store')
    return render(request,'store/delete.html',{'obj':review})
