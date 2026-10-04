# ShopEase – Django E-commerce Store

ShopEase is a simple e-commerce web application developed using Django. It allows users to browse products, register and log in, manage a shopping cart, and place orders.

## Features

- User registration, login, and logout
- Product listing with images, prices, and stock availability
- Individual product detail pages
- Add products to cart
- Update product quantities and remove items
- Checkout with customer and delivery details
- Order confirmation page
- Automatic stock update after placing an order
- Django admin panel for managing products, categories, and orders

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS
- **Database:** SQLite
- **Image Handling:** Pillow
- **Version Control:** Git and GitHub

## Project Structure

```text
CodeAlpha_Ecommerce_Store/
│
├── ecommerce/
├── store/
│   ├── migrations/
│   ├── templates/
│   │   └── store/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── media/
│   └── products/
├── manage.py
└── .gitignore
