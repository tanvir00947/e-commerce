from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200,default="default@email.com")
	
	def __str__(self):
		return self.name or f"Customer {self.id}"


class Product(models.Model):
	name = models.CharField(max_length=200,default="Default")
	description=models.TextField(null=True,blank=True)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(null=True, blank=True)

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	order_status=models.CharField(max_length=200,null=True,default="Processing")

	def __str__(self):
		return str(self.id)+" "+self.customer.name+" "+str(self.transaction_id)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product is not None and i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE,default=1)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		
		total = self.product.price * self.quantity
		return total
		
	
class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False,default="Default")
	city = models.CharField(max_length=200, null=False,default="Default")
	state = models.CharField(max_length=200, null=False,default="Default")
	zipcode = models.CharField(max_length=200, null=False,default="Default")
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
	

#my model
class Review(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,default=1)
    product= models.ForeignKey(Product,on_delete=models.CASCADE,default=1)
    body=models.TextField(default="default review")
    updated=models.DateTimeField(auto_now=True)
    created=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-updated','-created']

    def __str__(self):
        return self.body[0:50]


class ProductImages(models.Model):
	product=models.ForeignKey(Product,on_delete=models.CASCADE,default=1)
	image = models.ImageField(null=True, blank=True)

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

	def __str__(self):
		return str(self.id)