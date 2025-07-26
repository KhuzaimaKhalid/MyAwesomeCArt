from django.db import models

# Create your models here.
class Blogposts(models.Model):
    post_id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 100)
    head0 = models.CharField(max_length = 5000)
    chead0 = models.CharField(max_length = 5000)
    head1 = models.CharField(max_length = 100)
    chead1 = models.CharField(max_length = 5000)
    head2 = models.CharField(max_length = 100)
    chead2 = models.CharField(max_length = 5000)
    pub_date = models.DateField()
    thumbnail = models.ImageField(upload_to = 'shop/images', default = '')
