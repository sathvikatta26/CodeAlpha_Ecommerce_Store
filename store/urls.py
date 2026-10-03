from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # Product
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),

    # Cart
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("remove-from-cart/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update-cart/<int:product_id>/", views.update_cart_quantity, name="update_cart_quantity"),

    # User Authentication
    path("register/", views.register_view, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # Checkout
    path("checkout/", views.checkout_view, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
]