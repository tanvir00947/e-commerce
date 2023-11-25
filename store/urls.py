from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url


	path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerPage,name='register'),
    
	path('profile/<str:pk>/',views.userProfile,name="user-profile"),


	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    
	path('product_description/<str:pk>/',views.productDescripton,name="product_description"),
    
	path('update-user/<str:pk>/',views.updateUser,name='update-user'),
    path('order_details/<str:pk>/',views.orderDetails,name='order_details'),

	path('delete_review/<str:pk>/',views.deleteReview,name='delete_review'),
]