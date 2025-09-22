"""
Enum choices for the Skinly models
"""
from django.db import models

class SkinTone(models.TextChoices):
    FAIR = "FAIR", "Fair"
    LIGHT = "LIGHT", "Light"
    MEDIUM = "MEDIUM", "Medium"
    TAN = "TAN", "Tan"
    DEEP = "DEEP", "Deep"


class SkinType(models.TextChoices):
    OILY = "OILY", "Oily"
    DRY = "DRY", "Dry"
    COMBINATION = "COMBINATION", "Combination"
    SENSITIVE = "SENSITIVE", "Sensitive"
    NORMAL = "NORMAL", "Normal"

class ProductType(models.TextChoices):
    FOUNDATION = "FOUNDATION", "Foundation"
    CONCEALER = "CONCEALER", "Concealer"
    POWDER = "POWDER", "Powder"
    BLUSH = "BLUSH", "Blush"
    EYESHADOW = "EYESHADOW", "Eyeshadow"
    LIPSTICK = "LIPSTICK", "Lipstick"
    MASCARA = "MASCARA", "Mascara"
    EYELINER = "EYELINER", "Eyeliner"
    SKINCARE = "SKINCARE", "Skincare"
    OTHER = "OTHER", "Other"

class FinishType(models.TextChoices):
    MATTE = "MATTE", "Matte"
    DEWY = "DEWY", "Dewy"
    SATIN = "SATIN", "Satin"
    GLOSSY = "GLOSSY", "Glossy"
    SHIMMER = "SHIMMER", "Shimmer"

class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELED = "CANCELED", "Canceled"

class PaymentMethodType(models.TextChoices):
    CREDIT_CARD = "CREDIT_CARD", "Credit Card"
    PAYPAL = "PAYPAL", "PayPal"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY", "Cash on Delivery"