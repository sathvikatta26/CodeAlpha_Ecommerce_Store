from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction

from .models import Product, Order, OrderItem


# HOME PAGE
def home(request):
    products = Product.objects.filter(
        available=True,
        stock__gt=0
    ).select_related("category")

    return render(request, "store/home.html", {
        "products": products
    })


# PRODUCT DETAILS
def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        available=True
    )

    return render(request, "store/product_detail.html", {
        "product": product
    })


# ADD TO CART
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(
            Product,
            id=product_id,
            available=True,
            stock__gt=0
        )

        cart = request.session.get("cart", {})
        product_key = str(product.id)
        current_quantity = cart.get(product_key, 0)

        if current_quantity < product.stock:
            cart[product_key] = current_quantity + 1

        request.session["cart"] = cart

    return redirect("home")


# CART PAGE
def cart_view(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

        total += subtotal

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


# REMOVE FROM CART
def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        product_key = str(product_id)

        if product_key in cart:
            del cart[product_key]

        request.session["cart"] = cart

    return redirect("cart")


# UPDATE CART QUANTITY
def update_cart_quantity(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get("cart", {})
        product_key = str(product_id)

        if product_key in cart:
            action = request.POST.get("action")

            if action == "increase":
                if cart[product_key] < product.stock:
                    cart[product_key] += 1

            elif action == "decrease":
                cart[product_key] -= 1

                if cart[product_key] <= 0:
                    del cart[product_key]

        request.session["cart"] = cart

    return redirect("cart")


# USER REGISTRATION
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "store/register.html", {
        "form": form
    })


# USER LOGIN
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "store/login.html", {
        "form": form
    })


# USER LOGOUT
def user_logout(request):
    if request.method == "POST":
        logout(request)

    return redirect("home")


# CHECKOUT
@login_required(login_url="login")
def checkout_view(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    products = Product.objects.filter(
        id__in=cart.keys(),
        available=True
    )

    cart_items = []
    total = 0
    error = None

    for product in products:
        quantity = cart.get(str(product.id), 0)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 0

        if quantity <= 0:
            continue

        if quantity > product.stock:
            error = (
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )

        subtotal = product.price * quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

        total += subtotal

    if len(cart_items) != len(cart):
        error = "One or more products in your cart are no longer available."

    if not cart_items:
        return redirect("cart")

    if request.method == "POST" and not error:
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not all([full_name, email, phone, address]):
            error = "Please fill in all delivery details."

        elif len(phone) > 15:
            error = "Phone number must not exceed 15 characters."

        else:
            with transaction.atomic():
                locked_products = Product.objects.select_for_update().filter(
                    id__in=cart.keys(),
                    available=True
                )

                locked_items = []
                current_total = 0

                for product in locked_products:
                    quantity = int(cart.get(str(product.id), 0))

                    if quantity <= 0 or quantity > product.stock:
                        error = f"Insufficient stock for {product.name}."
                        break

                    subtotal = product.price * quantity
                    current_total += subtotal

                    locked_items.append((product, quantity))

                if len(locked_items) != len(cart):
                    error = "A product in your cart is no longer available."

                if not error:
                    order = Order.objects.create(
                        user=request.user,
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        address=address,
                        total_amount=current_total
                    )

                    for product, quantity in locked_items:
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )

                        product.stock -= quantity

                        if product.stock == 0:
                            product.available = False

                        product.save()

                    request.session["cart"] = {}

                    return redirect(
                        "order_success",
                        order_id=order.id
                    )

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "error": error,
        "full_name": request.POST.get(
            "full_name",
            request.user.get_full_name()
        ),
        "email": request.POST.get("email", request.user.email),
        "phone": request.POST.get("phone", ""),
        "address": request.POST.get("address", "")
    })


# ORDER SUCCESS
@login_required(login_url="login")
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, "store/order_success.html", {
        "order": order
    })