from django.db import models

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField
    products_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  
    desc = models.CharField(max_length=300)
    pub_date = models.DateField() 
    image = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.products_name 

class Contact(models.Model):
    msg_id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 50, default="")
    email = models.CharField(max_length= 50, default="")
    phone = models.CharField(max_length = 20, default="")
    desc = models.CharField(max_length = 1000, default="")

    def __str__(self):
        return self.name
class Order(models.Model):
    order_id = models.AutoField(primary_key = True)
    items_json = models.CharField(max_length = 5000)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    name = models.CharField(max_length= 50, default = "")
    email = models.CharField(max_length = 50, default = "")
    address = models.CharField(max_length = 100, default = "")
    city = models.CharField(max_length= 50, default = "")
    state = models.CharField(max_length= 50, default = "")
    zip_code = models.CharField(max_length = 20, default = "")
    phone = models.CharField(max_length= 20, default = "")

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key = True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length = 5000)
    timestamp = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.update_desc[0:7] + "..."  