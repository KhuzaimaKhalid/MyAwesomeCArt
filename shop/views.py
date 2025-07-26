import json
from math import ceil
import stripe
import hmac
import hashlib
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Order, OrderUpdate, Product, Contact

# Initialize Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Home page
def index(request):
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 - ceil((n / 4) - (n // 4))        
        allprods.append([prod, range(1, nslides), nslides])
    return render(request, 'shop/index.html', {'allprods': allprods})

def searchMatch(query, item):
    q = query.lower()
    return (
        q in item.products_name.lower() or
        q in item.category.lower()
    )


def search(request):
    query = request.GET.get('search', '').strip()

    # if the query is too short, immediately return with a message
    if len(query) < 4:
        return render(request, 'shop/search.html', {
            'allprods': [],
            'msg': "Please enter at least 4 characters to search."
        })

    # filter using your actual model field 'products_name'
    matched = Product.objects.filter(
        Q(products_name__icontains=query) |
        Q(category__icontains=query) | Q(desc__icontains=query)
    )

    # build the carousel data exactly as your template expects
    allprods = []
    for cat in matched.values_list('category', flat=True).distinct():
        items = matched.filter(category=cat)
        n = items.count()
        if n:
            nslides = ceil(n / 4)
            # template loops: {% for product, range, nslides in allprods %}
            allprods.append([items, range(1, nslides + 1), nslides])

    # render the right template, passing lowercase 'allprods'
    return render(request, 'shop/search.html', {
        'allprods': allprods,
        'msg': "" if allprods else f"No results found for “{query}.”"
    })

# About page
def about(request):
    return render(request, 'shop/about.html')

# Contact page
def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        Contact(name=name, email=email, phone=phone, desc=desc).save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})

# Order tracker
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if order:
                updates = []
                for u in OrderUpdate.objects.filter(order_id=orderId):
                    updates.append({'text': u.update_desc, 'time': u.timestamp})
                response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            return HttpResponse('{}')
        except Exception:
            return HttpResponse('{}')
    return render(request, 'shop/tracker.html')


# Product detail
def productView(request, myid):
    product = Product.objects.get(id=myid)
    return render(request, 'shop/prodView.html', {'product': product})

# Checkout page: shows form or post-order thank you
def checkout(request):
    # Always include payment keys in context
    context = {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'GOOGLE_MERCHANT_ID':    settings.GOOGLE_MERCHANT_ID,
        # 'merchant_id':           settings.PAYFAST['MERCHANT_ID'],  # for PayFast widget
    }

    if request.method == "POST":
        
        items_json = request.POST.get('itemsJson', '')
        name       = request.POST.get('name', '')
        amount_str = request.POST.get('amount', '0')
        email      = request.POST.get('email', '')
        address    = f"{request.POST.get('address1', '')} {request.POST.get('address2', '')}".strip()
        city       = request.POST.get('city', '')
        state      = request.POST.get('state', '')
        zip_code   = request.POST.get('zip_code', '')
        phone      = request.POST.get('phone', '')

        
        try:
            total_price = float(amount_str)
        except ValueError:
            total_price = 0.0
        request.session['total_price'] = total_price

        
        order = Order(
            items_json=items_json,
            amount=total_price,
            name=name,
            email=email,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        order.save()
        OrderUpdate(order_id=order.order_id, update_desc="The order has been placed").save()

        
        context.update({
            'thank': True,
            'id': order.order_id,
            # 'transaction_id': order.order_id,  
        })
        return render(request, 'shop/checkout.html', context)

    
    return render(request, 'shop/checkout.html', context)


@csrf_exempt
def process_google_pay(request):
    try:
        data  = json.loads(request.body)
        token = data.get('token')
        amount = int(float(data.get('amount', 0)) * 100)  # convert Rs. to paisa

        # 1) Create Stripe PaymentMethod
        pm = stripe.PaymentMethod.create(
            type="card",
            card={"token": token}
        )
        # 2) Create & confirm PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="pkr",
            payment_method=pm.id,
            confirmation_method="automatic",
            confirm=True,
        )
        return JsonResponse({'success': True, 'payment_intent': intent.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# # Endpoint to process PayFast callback
# @csrf_exempt
# def process_payfast(request):
#     if request.method != "POST":
#         return HttpResponse(status=405)

#     # 1) Gather posted data
#     merchant_id    = request.POST.get('merchant_id')
#     transaction_id = request.POST.get('transaction_id')
#     amount         = request.POST.get('amount')
#     signature      = request.POST.get('pf_signature', '')

#     # 2) Validate merchant
#     if merchant_id != settings.PAYFAST['MERCHANT_ID']:
#         return HttpResponse("Invalid merchant", status=400)

#     # 3) Re-compute signature per PayFast spec
#     params = {k: v for k, v in request.POST.items() if k != 'pf_signature'}
#     sorted_items = sorted(params.items())
#     signing_string = "&".join(f"{k}={v}" for k, v in sorted_items)

#     computed_sig = hmac.new(
#         settings.PAYFAST['SECURED_KEY'].encode(),
#         signing_string.encode(),
#         hashlib.sha256
#     ).hexdigest()

#     if not hmac.compare_digest(computed_sig, signature):
#         return HttpResponse("Signature mismatch", status=400)

#     # 4) Mark the order as paid
#     order = get_object_or_404(Order, order_id=transaction_id)
#     order.payment_status = 'Paid'
#     order.save()
#     OrderUpdate(order_id=order.order_id, update_desc="Payment received via PayFast").save()

#     # 5) Show success page
#     return render(request, 'shop/payment_success.html', {'order': order})
