from django import forms
from .models import GeneralConfig, Mercado, Bolsa, Empresa, Subscription, Product, Blog, Image, Noticia
from users.models import CustomUser

class GeneralConfigForm(forms.ModelForm):

    class Meta:
        model = GeneralConfig
        fields = ['app_name', 'app_syncopation', 'app_icon', 'app_transparency_factor', 'app_logs', 'app_primary', 'app_color_1', 'app_color_2', 'app_color_3', 'app_color_4', 'app_color_5', 'app_color_6', 'app_color_7', 'app_color_8', 'app_success', 'app_danger', 'app_url', 'smtp_email_account','smtp_password','smtp_server','smtp_port', 'currency', 'paypal_client_id', 'paypal_secret_key', 'paypal_account_email', 'stripe_public_key', 'stripe_secret_key', 'google_oauth_client_id', 'google_oauth_client_secret', 'google_analytics_tag_id']


class MercadoForm(forms.ModelForm):

    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = Mercado
        fields = ['title', 'description']


class BolsaForm(forms.ModelForm):

    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = Bolsa
        fields = ['title', 'description', 'mercado']


class EmpresaForm(forms.ModelForm):

    public = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class': ''}), )
    bolsas = forms.ModelMultipleChoiceField(
        queryset = Bolsa.objects.all(),
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
        error_messages={'required': 'Por favor selecciona al menos una bolsa'}
    )
    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = Empresa
        fields = ['title', 'description', 'public', 'mercado', 'bolsas']

    def clean(self):
        cleaned_data = super().clean()
        mercado = cleaned_data.get('mercado')
        bolsas = cleaned_data.get('bolsas')

        if mercado and bolsas:
            # Verificar que todas las bolsas pertenezcan al mercado seleccionado
            for bolsa in bolsas:
                if bolsa.mercado != mercado:
                    raise forms.ValidationError(
                        f"La bolsa '{bolsa}' no pertenece al mercado '{mercado}'"
                    )

        return cleaned_data


class ImageForm(forms.ModelForm):

    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )
    
    class Meta:
        model = Image
        fields = ['image', 'title', 'description']


class SubscriptionForm(forms.ModelForm):

    user = forms.ModelChoiceField( queryset = CustomUser.objects.all(), required=True )
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(public=True),
        required=False,
        empty_label="Seleccionar producto (opcional)",
        label="Producto"
    )

    class Meta:
        model = Subscription
        fields = ['user', 'product', 'amount', 'currency', 'payment_method', 'payment_product_id', 'payment_subscription_id', 'status', 'start_date', 'due_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        config = GeneralConfig.objects.get(id=1) # Get general config information
        self.fields['currency'].initial = config.currency # Set the same currency value as general config
        self.fields['currency'].widget.attrs['readonly'] = True # Disallow currency field to set it unwritable
        self.fields['payment_product_id'].widget = forms.HiddenInput() # Hide the payment_product_id field

    def save(self, commit=True):
        subscription = super().save(commit=False)
        # If a product is selected, use its ID and price
        if self.cleaned_data.get('product'):
            product = self.cleaned_data['product']
            subscription.payment_product_id = product.id
            # Optionally update the amount with the product's price
            if not self.cleaned_data.get('amount') or self.cleaned_data.get('amount') == 0:
                subscription.amount = product.final_price
        if commit:
            subscription.save()
        return subscription


class ProductForm(forms.ModelForm):

    public = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class': ''}), )
    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'interval_count', 'interval_unit', 'discount', 'public', 'stripe_subscription_id', 'paypal_subscription_id']


class BlogForm(forms.ModelForm):

    public = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class': ''}), )
    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = Blog
        fields = ['title', 'description', 'public', 'url', 'pic']


class ProductAssignForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all(), empty_label="Choose user")
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Choose product")


class NoticiaForm(forms.ModelForm):

    public = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': ''}))
    is_premium = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': ''}))
    summary = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '3'}))
    content = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '10'}))
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'earnings, merger, IPO'}))

    class Meta:
        model = Noticia
        fields = ['title', 'summary', 'content', 'published_date', 'source', 'source_url', 'author',
                  'image', 'video_link', 'empresa', 'tags', 'is_premium', 'public']
        widgets = {
            'published_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }