# 💄 Skinly - Premium Makeup E-commerce Platform

A sophisticated Django-based e-commerce platform for makeup and beauty products with AI-powered recommendations and a luxurious sand/gold/brown color palette.

## ✨ Features

- **🎨 Beautiful Design**: Sand/gold/brown beige color palette with responsive Bootstrap 5 design
- **🤖 AI Recommendations**: Personalized product suggestions based on skin type and preferences
- **🔍 Advanced Search**: Multi-criteria filtering by brand, product type, skin compatibility, price
- **🛒 Complete E-commerce**: Shopping cart, wishlist, checkout, order management
- **👤 User Profiles**: Custom user model with skin tone/type preferences
- **⭐ Review System**: Product reviews with taste profile learning
- **📱 Mobile-Ready**: Fully responsive design for all devices
- **🔐 Secure Authentication**: Django's built-in auth with custom user model

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.0+

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd /Users/mauricioescudero/PycharmProjects/skinly-ecomm
   ```

2. **Activate virtual environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Open your browser** and navigate to:
   - **Main site**: http://127.0.0.1:8000/
   - **Admin panel**: http://127.0.0.1:8000/admin/

## 📊 Sample Data Setup

To get started with sample data, you can add products through the admin panel:

1. Go to http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials
3. Add some **Brands** (e.g., "Fenty Beauty", "Rare Beauty", "Charlotte Tilbury")
4. Add some **Colors** (e.g., "Ruby Red #DC143C", "Golden Glow #FFD700")
5. Add **Products** with different types, prices, and stock quantities
6. Create a **RecommendationEngine** and **SearchEngine** instance

## 🎯 Key URLs

- **Home**: `/` - Main landing page with featured products
- **Products**: `/products/` - Product catalog with filtering
- **Login**: `/login/` - User authentication
- **Profile**: `/profile/` - User profile management
- **Cart**: `/cart/` - Shopping cart
- **Wishlist**: `/wishlist/` - User wishlist
- **Orders**: `/orders/` - Order history

## 🏗️ Project Structure

```
skinly-ecomm/
├── skinly_core/          # Main Django project
│   ├── settings.py       # Project settings
│   └── urls.py          # Main URL configuration
├── skinly/              # Main Django app
│   ├── models.py        # All data models (User, Product, etc.)
│   ├── views.py         # View logic
│   ├── urls.py          # App URL patterns
│   ├── forms.py         # Django forms
│   ├── admin.py         # Admin configuration
│   └── templates/       # HTML templates
│       ├── skinly/      # App templates
│       └── registration/ # Auth templates
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## 🎨 Design System

The application uses a warm, luxurious color palette:

- **Primary Sand**: #F4E4BC (Light sand)
- **Primary Gold**: #D4AF37 (Classic gold)
- **Primary Brown**: #8B6914 (Dark gold/brown)
- **Accent Beige**: #F5F5DC (Beige)
- **Warm Brown**: #A0522D (Sienna brown)
- **Light Cream**: #FDF5E6 (Old lace)

## 🔧 Development

### Adding New Products
Use the admin panel to add products with:
- Name, brand, product type
- Price and stock quantity
- Skin type compatibility
- Color and finish type

### Customizing Recommendations
The `RecommendationEngine` learns from:
- User skin type and tone
- Product reviews and ratings
- Wishlist preferences
- Purchase history

## 📱 Mobile Responsiveness

The application is fully responsive with:
- Mobile-first design approach
- Touch-friendly interface
- Optimized loading for mobile networks
- Responsive navigation and forms

## 🛡️ Security Features

- CSRF protection on all forms
- Secure password validation
- Login required decorators
- Input validation and sanitization

## 🎯 Future Enhancements

- Payment gateway integration (Stripe, PayPal)
- Email notifications for orders
- Advanced inventory management
- Social media integration
- Multi-language support
- Performance analytics

## 🐛 Troubleshooting

**Migration Issues**:
```bash
python manage.py makemigrations --empty skinly
python manage.py migrate
```

**Static Files Not Loading**:
```bash
python manage.py collectstatic
```

**Permission Errors**:
```bash
chmod +x manage.py
```

## 📄 License

This project is for educational and development purposes.

---

**Built with ❤️ using Django, Bootstrap 5, and modern web technologies**