from django import forms
from .models import GeneralConfig, SurgicalArea, SurgeryType, PeripheralBlock, Subscription, Product, Blog, Image
from users.models import CustomUser

class GeneralConfigForm(forms.ModelForm):

    class Meta:
        model = GeneralConfig
        fields = ['app_name', 'app_syncopation', 'app_icon', 'app_transparency_factor', 'app_logs', 'app_primary', 'app_color_1', 'app_color_2', 'app_color_3', 'app_color_4', 'app_color_5', 'app_color_6', 'app_color_7', 'app_color_8', 'app_success', 'app_danger', 'app_url', 'smtp_email_account','smtp_password','smtp_server','smtp_port', 'currency', 'paypal_client_id', 'paypal_secret_key', 'paypal_account_email', 'stripe_public_key', 'stripe_secret_key', 'google_oauth_client_id', 'google_oauth_client_secret', 'google_analytics_tag_id']


class SurgicalAreaForm(forms.ModelForm):

    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = SurgicalArea
        fields = ['title', 'description']


class SurgeryTypeForm(forms.ModelForm):

    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )
    
    class Meta:
        model = SurgeryType
        fields = ['title', 'description', 'surgical_area']


class PeripheralBlockForm(forms.ModelForm):

    public = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class': ''}), )
    surgical_area = forms.ModelChoiceField( queryset = SurgicalArea.objects.all(), required=True )
    surgery_type = forms.ModelChoiceField( queryset = SurgeryType.objects.all(), required=True )
    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )

    class Meta:
        model = PeripheralBlock
        fields = ['title', 'description', 'video_link', 'public', 'surgery_type']


class ImageForm(forms.ModelForm):

    description = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control', 'cols': '40', 'rows': '5'}) )
    
    class Meta:
        model = Image
        fields = ['image', 'title', 'description']


class SubscriptionForm(forms.ModelForm):

    user = forms.ModelChoiceField( queryset = CustomUser.objects.all(), required=True )

    class Meta:
        model = Subscription
        fields = ['user', 'amount', 'currency', 'payment_method', 'payment_product_id', 'payment_subscription_id', 'start_date', 'due_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        config = GeneralConfig.objects.get(id=1) # Get general config information
        self.fields['currency'].initial = config.currency # Set the same currency value as general config
        self.fields['currency'].widget.attrs['readonly'] = True # Disallow currency field to set it unwritable
        self.fields['payment_product_id'].widget.attrs['readonly'] = True # Disallow payment_product_id field to set it unwritable
        self.fields['payment_subscription_id'].widget.attrs['readonly'] = True # Disallow payment_subscription_id field to set it unwritable


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