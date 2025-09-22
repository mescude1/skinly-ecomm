from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review, TasteProfile, SkinType, SkinTone, ProductType, FinishType


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'skin_tone', 'skin_type']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'skin_tone': forms.Select(attrs={'class': 'form-control'}),
            'skin_type': forms.Select(attrs={'class': 'form-control'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts about this product...'
            }),
        }


class ProductFilterForm(forms.Form):
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for products...'
        })
    )
    
    brand = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Brands",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    product_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(ProductType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    skin_type = forms.ChoiceField(
        choices=[('', 'All Skin Types')] + list(SkinType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )
    
    def __init__(self, *args, **kwargs):
        brands = kwargs.pop('brands', None)
        super().__init__(*args, **kwargs)
        if brands:
            self.fields['brand'].queryset = brands


class TasteProfileForm(forms.ModelForm):
    preferred_product_types = forms.MultipleChoiceField(
        choices=ProductType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'taste-preferences'})
    )
    
    preferred_finish_types = forms.MultipleChoiceField(
        choices=FinishType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'taste-preferences'})
    )
    
    class Meta:
        model = TasteProfile
        fields = ['preferred_colors']
        widgets = {
            'preferred_colors': forms.CheckboxSelectMultiple(attrs={'class': 'taste-preferences'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Pre-populate the multiple choice fields
            if self.instance.preferred_product_types:
                self.initial['preferred_product_types'] = self.instance.preferred_product_types.split(',')
            if self.instance.preferred_finish_types:
                self.initial['preferred_finish_types'] = self.instance.preferred_finish_types.split(',')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle the comma-separated fields
        if 'preferred_product_types' in self.cleaned_data:
            instance.preferred_product_types = ','.join(self.cleaned_data['preferred_product_types'])
        
        if 'preferred_finish_types' in self.cleaned_data:
            instance.preferred_finish_types = ','.join(self.cleaned_data['preferred_finish_types'])
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class CartItemForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'style': 'width: 80px;'
        })
    )


class CheckoutForm(forms.Form):
    # Shipping Information
    shipping_first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_country = forms.CharField(
        max_length=100,
        initial='USA',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Payment Information
    payment_method = forms.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'payment-method'})
    )
    
    # Special Instructions
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special delivery instructions...'
        })
    )
    
    # Terms and Conditions
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )