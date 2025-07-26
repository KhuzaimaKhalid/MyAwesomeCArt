from django.urls import path
from . import views 


urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="tracker"),
    path("search/", views.search, name="search"),
    path("products/<int:myid>/", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path('process_google_pay/', views.process_google_pay, name='process_google_pay'),
    # path("process_payfast/",     views.process_payfast,     name="process_payfast")
    
]