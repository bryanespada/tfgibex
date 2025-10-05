from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from appmodels.models import GeneralConfig, Mercado, Bolsa, Empresa, Subscription, Product, Blog, Image, Noticia
from users.models import CustomUser
from logs.models import UserLog, AdminsLog, SubscriptionLog, TrackingLog
from users.forms import CustomUserCreationByAdminForm, CustomUserEditByAdminForm
from django.contrib import messages
from appmodels.forms import GeneralConfigForm, MercadoForm, BolsaForm, EmpresaForm, SubscriptionForm, ProductForm, BlogForm, ProductAssignForm, ImageForm, NoticiaForm
from django.contrib.auth.models import Group
from logs.views import log
from django.db.models import Count
from utils.functions import get_dates_from_date
from django.urls import reverse



######################################################################################################################################################
# DASHBOARDS
######################################################################################################################################################


@login_required(login_url="/users/access")
def dashboard(request):
    """
    Function serve the index dashboard
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    start_of_last_week = timezone.now() - timedelta(days=7) # Last week reference day
    administration_group = Group.objects.get(name='Administration') # Administration group object

    ##########################################################################################
    # Chart R0_C1: Top row

    # Get the number of users registered
    context['total_users'] = CustomUser.objects.all().count()

    # Get the number of users registered since one week ago
    context['total_users_last_week'] = CustomUser.objects.filter(date_joined__gte=start_of_last_week).count()

    # Get the percentage of users increasement
    context['total_users_increasement'] = context['total_users_last_week']/context['total_users']*100

    # Get the number of admins
    context['total_admins']  = CustomUser.objects.filter(groups=administration_group).count()

    # Get the number of new admins
    context['total_admins_last_week'] = CustomUser.objects.filter(groups=administration_group, date_joined__gte=start_of_last_week).count()

    # Get the percentage of admins increasement
    context['total_admin_increasement'] = context['total_admins_last_week']/context['total_admins']*100

    # Get the number of active subscriptions
    context['total_active_subscriptions'] = Subscription.objects.filter(due_date__gte=timezone.now()).count()

    # Get the number of active subscriptions
    context['total_active_subscriptions_last_week'] = Subscription.objects.filter(due_date__gte=timezone.now(), payment_datetime__gte=start_of_last_week).count()

    # Get the number of empresas
    context['total_empresas'] = Empresa.objects.all().count()

    # Get the number of empresas in a free mode
    context['total_empresas_free'] = Empresa.objects.filter(public=True).count()

    # Get the number of products
    context['total_products'] = Product.objects.all().count()

    # Get the number of products published
    context['total_products_published'] = Product.objects.filter(public=True).count()


    ##########################################################################################
    # Chart R1_C1: Visitors and new users

    context['visitors'] = {}
    context['visitors']['dates'] = []
    context['visitors']['count'] = []

    distinct_users_per_date = {} # Initialize the dict to store all users and dates
    distinct_dates = UserLog.objects.dates('timestamp', 'day', order='DESC') # Get every distinct date

    for log_date in distinct_dates: # For each date founded
        logs_for_date = UserLog.objects.filter(timestamp__date=log_date) # Filter UserLog registries for actual date 
        distinct_users = logs_for_date.exclude(user=None).values_list('user', flat=True).distinct() # Get all users for that date
        distinct_users_per_date[log_date.strftime('%Y-%m-%d')] = len(distinct_users) # Save the number of distinct users
    
    dates_since = get_dates_from_date(min(distinct_users_per_date.keys())) # Get the min date
    context['visitors']['show'] = False if len(distinct_users_per_date.keys()) == 0 else True # If there are dates, the chart will be shown

    dates_tmp = sorted(distinct_users_per_date.keys())

    if dates_tmp:
        for date_since in dates_since:
            date_since = date_since.strftime('%Y-%m-%d')
            (context['visitors']['dates']).append(date_since)
            (context['visitors']['count']).append(distinct_users_per_date[date_since] if date_since in dates_tmp else 0)


    context['new_users'] = {}
    context['new_users']['dates'] = []
    context['new_users']['count'] = []

    distinct_users_per_date = {}  # Inicializa el diccionario para almacenar todos los usuarios y fechas
    distinct_dates = UserLog.objects.dates('timestamp', 'day', order='DESC')  # Obtiene cada fecha distinta

    for log_date in distinct_dates:  # Para cada fecha encontrada
        users_for_date = UserLog.objects.filter(timestamp__date=log_date, action_type='create', status=200)  # Filtra los registros de UserLog para la fecha actual
        distinct_users = users_for_date.exclude(user=None).values_list('user', flat=True).distinct()  # Obtiene todos los usuarios para esa fecha
        distinct_users_per_date[log_date.strftime('%Y-%m-%d')] = len(distinct_users)  # Guarda el número de usuarios distintos

    dates_since = get_dates_from_date(min(distinct_users_per_date.keys()))  # Obtiene la fecha mínima
    context['new_users']['show'] = False if len(distinct_users_per_date.keys()) == 0 else True  # Si hay fechas, se mostrará el gráfico

    dates_tmp = sorted(distinct_users_per_date.keys())

    if dates_tmp:
        for date_since in dates_since:
            date_since = date_since.strftime('%Y-%m-%d')
            context['new_users']['dates'].append(date_since)
            context['new_users']['count'].append(distinct_users_per_date[date_since] if date_since in dates_tmp else 0)



    ##########################################################################################
    # Chart R1_C2: Earning

    subscriptions = Subscription.objects.all() # Get all subscriptions

    daily_total_amount = {} # Initialize the dict to save amounts
    daily_total_subscriptions = {} # Initialize the dict to save the number of subscription por each day

    for subscription in subscriptions:
        start_date = str(subscription.start_date) # Get just the date from each subscription
        amount = subscription.amount # Get the amount

        if start_date not in daily_total_amount: # Initialize the date
            daily_total_amount[start_date] = 0
            daily_total_subscriptions[start_date] = 0

        daily_total_amount[start_date] += amount # Add the amount
        daily_total_subscriptions[start_date] += 1 # Add the new subscription to that date

    context['total_earned'] = {}
    context['total_earned']['amount'] = []
    context['total_earned']['count'] = []
    context['total_earned']['dates'] = []

    dates_tmp = sorted(daily_total_amount.keys()) # Sort days
    context['total_earned']['show'] = False if len(dates_tmp) == 0 else True

    if dates_tmp:
        dates_since = get_dates_from_date(min(dates_tmp)) # Get each date since then and now
        for date_since in dates_since:
            date_since = date_since.strftime('%Y-%m-%d')
            (context['total_earned']['dates']).append(date_since)
            (context['total_earned']['amount']).append(daily_total_amount[date_since] if date_since in dates_tmp else 0)
            (context['total_earned']['count']).append(daily_total_subscriptions[date_since] if date_since in dates_tmp else 0)


    ##########################################################################################
    # Chart R2_C1: Top products

    # Get the top 8 most viewed products by subscriptions
    top_products = SubscriptionLog.objects.exclude(product=None).values('product__title').annotate(block_count=Count('product')).order_by('-block_count')[:8]

    context['top_products'] = {}
    context['top_products']['show'] = True if top_products else False
    # Attach the results to the general context
    context['top_products']['names'] = [block['product__title'] for block in top_products]
    context['top_products']['values'] = [block['block_count'] for block in top_products]


    ##########################################################################################
    # Chart R2_C2: Top empresas

    # Get the top 8 most viewed empresas
    top_empresas = TrackingLog.objects.exclude(empresa=None).values('empresa__title').annotate(empresa_count=Count('empresa')).order_by('-empresa_count')[:8]

    context['top_empresas'] = {}
    context['top_empresas']['show'] = True if top_empresas else False
    # Attach the results to the general context
    context['top_empresas']['names'] = [empresa['empresa__title'] for empresa in top_empresas]
    context['top_empresas']['values'] = [empresa['empresa_count'] for empresa in top_empresas]


    ##########################################################################################
    # Chart R2_C3: Top noticias (más leídas)

    # Obtener las 8 noticias más vistas
    top_noticias = TrackingLog.objects.exclude(noticia=None).values('noticia__title').annotate(noticia_count=Count('noticia')).order_by('-noticia_count')[:8]

    context['top_noticias'] = {}
    context['top_noticias']['show'] = True if top_noticias else False
    # Adjuntar los resultados al contexto general
    context['top_noticias']['names'] = [noticia['noticia__title'][:30] + '...' if len(noticia['noticia__title']) > 30 else noticia['noticia__title'] for noticia in top_noticias]
    context['top_noticias']['values'] = [noticia['noticia_count'] for noticia in top_noticias]


    ##########################################################################################
    # Chart R3_C1: Actividad por día de la semana

    context['activity_by_weekday'] = {}
    context['activity_by_weekday']['names'] = []
    context['activity_by_weekday']['values'] = []

    from django.db.models.functions import ExtractWeekDay

    # Obtener actividad por día de la semana (1=Domingo, 2=Lunes, etc en PostgreSQL/MySQL)
    weekday_counts = UserLog.objects.annotate(
        weekday=ExtractWeekDay('timestamp')
    ).values('weekday').annotate(
        total=Count('id')
    ).order_by('weekday')

    # Mapeo de números a nombres de días en español
    weekday_names = {
        1: 'Domingo',
        2: 'Lunes',
        3: 'Martes',
        4: 'Miércoles',
        5: 'Jueves',
        6: 'Viernes',
        7: 'Sábado'
    }

    # Crear diccionario con los conteos
    weekday_dict = {item['weekday']: item['total'] for item in weekday_counts}

    # Ordenar empezando por Lunes
    weekday_order = [2, 3, 4, 5, 6, 7, 1]  # Lunes a Domingo

    for day_num in weekday_order:
        context['activity_by_weekday']['names'].append(weekday_names[day_num])
        context['activity_by_weekday']['values'].append(weekday_dict.get(day_num, 0))

    # If there's no element to print the chart, this flag tell the template show -No data- message
    context['activity_by_weekday']['show'] = False if sum(s for s in context['activity_by_weekday']['values']) == 0 else True


    ##########################################################################################
    # Chart R3_C2: Registered by country

    context['total_registered_country'] = {}
    context['total_registered_country']['names'] = []
    context['total_registered_country']['values'] = []

    country_counts = UserLog.objects.filter(action_type='create', status=200).values('country').annotate(total=Count('id'))
    total_registered_country = {country['country']: country['total'] for country in country_counts}
    for country in country_counts:
        context['total_registered_country']['names'].append(country['country'])
        context['total_registered_country']['values'].append(total_registered_country.get(country['country'], 0))

    # If there's no element to print the chart, this flag tell the template show -No data- message
    context['total_registered_country']['show'] = False if sum(s for s in context['total_registered_country']['values']) == 0 else True


    ##########################################################################################
    # Chart R3_C3: Subscriptions by country

    context['total_subscriptions_country'] = {}
    context['total_subscriptions_country']['names'] = []
    context['total_subscriptions_country']['values'] = []

    country_counts = SubscriptionLog.objects.filter(action_type='create', status=200).values('country').annotate(total=Count('id'))
    total_subscriptions_country = {country['country']: country['total'] for country in country_counts}
    for country in country_counts:
        context['total_subscriptions_country']['names'].append(country['country'])
        context['total_subscriptions_country']['values'].append(total_subscriptions_country.get(country['country'], 0))

    # If there's no element to print the chart, this flag tell the template show -No data- message
    context['total_subscriptions_country']['show'] = False if sum(s for s in context['total_subscriptions_country']['values']) == 0 else True





    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"", "item":"Dashboard"})
    return render (request, "administration/dashboard/index.html", context)


######################################################################################################################################################
# PARAMETERS
######################################################################################################################################################


@login_required(login_url="/users/access")
def parameters(request):
    """
    Function to manipulate every system parameters of the general app configuration
    """
    context = {}
    config = get_object_or_404(GeneralConfig, id=1)

    if request.method == 'POST':
        form = GeneralConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Parameters successfully updates.")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":"", "item":"Parameters"})
            return redirect('/administration/parameters')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":"Invalid form", "item":"Parameters"})

    form = GeneralConfigForm(instance=config)

    # General
    form.fields['app_name'].widget.attrs.update({'class': 'form-control'})
    form.fields['app_syncopation'].widget.attrs.update({'class': 'form-control'})
    form.fields['app_url'].widget.attrs.update({'class': 'form-control'})
    form.fields['app_logs'].widget.attrs.update({'class': 'form-control'})
    form.fields['smtp_email_account'].widget.attrs.update({'class': 'form-control'})
    form.fields['smtp_password'].widget.attrs.update({'class': 'form-control'})
    form.fields['smtp_server'].widget.attrs.update({'class': 'form-control'})
    form.fields['smtp_port'].widget.attrs.update({'class': 'form-control'})

    # Branding
    form.fields['app_primary'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_1'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_2'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_3'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_4'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_5'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_6'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_7'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_color_8'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_success'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_danger'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_icon'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['app_transparency_factor'].widget.attrs.update({'class': 'form-control'})

    # Payment
    form.fields['currency'].widget.attrs.update({'class': 'form-control'})
    form.fields['paypal_client_id'].widget.attrs.update({'class': 'form-control'})
    form.fields['paypal_secret_key'].widget.attrs.update({'class': 'form-control'})
    form.fields['paypal_account_email'].widget.attrs.update({'class': 'form-control'})
    form.fields['stripe_public_key'].widget.attrs.update({'class': 'form-control'})
    form.fields['stripe_secret_key'].widget.attrs.update({'class': 'form-control'})

    # Google OAuth
    form.fields['google_oauth_client_id'].widget.attrs.update({'class': 'form-control'})
    form.fields['google_oauth_client_secret'].widget.attrs.update({'class': 'form-control'})
    form.fields['google_analytics_tag_id'].widget.attrs.update({'class': 'form-control'})

    context['form'] = form
    context['config'] = config
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Parameters"})
    return render (request, "administration/general/parameters.html", context)


######################################################################################################################################################
# CRUD MERCADOS
######################################################################################################################################################


@login_required(login_url="/users/access")
def mercados(request):
    """
    Function to get all mercados
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['mercados'] = Mercado.objects.all().order_by('title')
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Mercado"})
    return render (request, "administration/mercado/mercados.html", context)

@login_required(login_url="/users/access")
def mercado_add(request):
    """
    Function to add a new mercado
    """
    context = {}
    if request.method == 'POST':
        form = MercadoForm(request.POST)
        if form.is_valid():
            mercado = form.save(commit=False)
            mercado.save()
            messages.success(request, "Mercado successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{mercado.title}'", "item":"Mercado"})
            return redirect('/administration/mercados')
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Invalid form", "item":"Mercado"})

    form = MercadoForm()
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Mercado"})
    return render (request, "administration/mercado/mercado_add.html", context)

@login_required(login_url="/users/access")
def mercado_edit(request, mercado_id):
    """
    Function to edit an existing mercado
    """
    context = {}
    mercado = get_object_or_404(Mercado, id=mercado_id)
    if request.method == 'POST':
        form = MercadoForm(request.POST, instance=mercado)
        if form.is_valid():
            mercado = form.save(commit=False)
            mercado.save()
            messages.success(request, "Mercado successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated '{mercado.title}'", "item":"Mercado"})
            return redirect('/administration/mercados')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating '{mercado.title}'", "item":"Mercado"})

    form = MercadoForm(instance=mercado)
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    context['form'] = form
    context['mercado'] = mercado
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of '{mercado.title}'", "item":"Mercado"})
    return render (request, "administration/mercado/mercado_edit.html", context)

@login_required(login_url="/users/access")
def mercado_delete(request, mercado_id):
    """
    Function to delete an existing mercado
    """
    mercado = get_object_or_404(Mercado, id=mercado_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{mercado.title}'", "item":"Mercado"})
    mercado.delete()
    messages.success(request, "Mercado successfully deleted")
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    return redirect('/administration/mercados')


######################################################################################################################################################
# CRUD BOLSAS
######################################################################################################################################################


@login_required(login_url="/users/access")
def bolsas(request):
    """
    Function to get all bolsas
    """
    context = {}
    context['bolsas'] = Bolsa.objects.all().order_by('title')
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Bolsa"})
    return render (request, "administration/bolsa/bolsas.html", context)

@login_required(login_url="/users/access")
def bolsa_add(request):
    """
    Function to add a new bolsa
    """
    context = {}
    if request.method == 'POST':
        form = BolsaForm(request.POST)
        if form.is_valid():
            bolsa = form.save(commit=False)
            bolsa.save()
            messages.success(request, "Bolsa successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{bolsa.title}'", "item":"Bolsa"})
            return redirect('/administration/bolsas')
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Invalid form", "item":"Bolsa"})

    mercados = Mercado.objects.all()
    form = BolsaForm()
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['mercado'].queryset = mercados # Populate the select options
    form.fields['mercado'].widget.attrs.update({'class': 'form-control'})
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Bolsa"})
    return render (request, "administration/bolsa/bolsa_add.html", context)

@login_required(login_url="/users/access")
def bolsa_edit(request, bolsa_id):
    """
    Function to edit an existing bolsa
    """
    context = {}
    bolsa = get_object_or_404(Bolsa, id=bolsa_id)
    if request.method == 'POST':
        form = BolsaForm(request.POST, instance=bolsa)
        if form.is_valid():
            bolsa = form.save(commit=False)
            bolsa.save()
            messages.success(request, "Bolsa successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated '{bolsa.title}'", "item":"Bolsa"})
            return redirect('/administration/bolsas')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating '{bolsa.title}'", "item":"Bolsa"})

    form = BolsaForm(instance=bolsa)
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['mercado'].queryset = Mercado.objects.all() # Populate the select options
    form.fields['mercado'].widget.attrs.update({'class': 'form-control'})
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of '{bolsa.title}'", "item":"Bolsa"})
    return render (request, "administration/bolsa/bolsa_edit.html", context)

@login_required(login_url="/users/access")
def bolsa_delete(request, bolsa_id):
    """
    Function to delete an existing bolsa
    """
    bolsa = get_object_or_404(Bolsa, id=bolsa_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{bolsa.title}'", "item":"Bolsa"})
    bolsa.delete()
    messages.success(request, "Bolsa successfully deleted")
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    return redirect('/administration/bolsas')

@login_required(login_url="/users/access")
def get_bolsas_by_mercado(request, mercado_id):
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing by Mercado", "item":"Bolsa"})
    bolsas = Bolsa.objects.filter(mercado=mercado_id)
    bolsas_list = list(bolsas.values('id', 'title')) # Change bolsas into a list of dicts
    return JsonResponse(bolsas_list, safe=False)

######################################################################################################################################################
# CRUD EMPRESAS
######################################################################################################################################################


@login_required(login_url="/users/access")
def empresas(request):
    """
    Function to get all empresas
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['empresas'] = Empresa.objects.all().order_by('title')
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Empresa"})
    return render (request, "administration/empresa/empresas.html", context)

@login_required(login_url="/users/access")
def empresa_add(request):
    """
    Function to add a new empresa
    """
    context = {}
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the empresa and its ManyToMany relationships
            empresa = form.save()
            messages.success(request, "Empresa successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{empresa.title}'", "item":"Empresa"})
            return redirect('/administration/empresas')
        else:
            messages.error(request, "Error adding empresa. Please check the form.")
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Invalid form", "item":"Empresa"})

    # Initialize the Form object
    form = EmpresaForm()

    # Setup mercado field
    form.fields['mercado'].widget.attrs.update({'class': 'form-control'})

    # Initialize empty the bolsas select which depends on mercado selection
    form.fields['bolsas'].queryset = Bolsa.objects.none()
    form.fields['bolsas'].widget.attrs.update({'class': 'form-control'})

    # Rest of empty fields to fill
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['public'].widget.attrs.update({'class': 'form-control'})

    # Attach fields configuration to the context
    context['form'] = form

    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Empresa"})
    return render (request, "administration/empresa/empresa_add.html", context)

@login_required(login_url="/users/access")
def empresa_edit(request, empresa_id):
    """
    Function to edit an existing empresa
    """
    empresa = get_object_or_404(Empresa, id=empresa_id)
    context = {}

    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            # Save the form
            updated_empresa = form.save()
            messages.success(request, "Empresa successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated '{updated_empresa.title}'", "item":"Empresa"})
            return redirect('/administration/empresas')
        else:
            messages.error(request, "Error updating empresa. Please check the form.")
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating '{empresa.title}'", "item":"Empresa"})

    # Initialize the Form object with the existing empresa data
    # This will automatically preselect mercado and bolsas
    form = EmpresaForm(instance=empresa)

    # Setup mercado field
    form.fields['mercado'].widget.attrs.update({'class': 'form-control'})

    # Setup bolsas field to show only bolsas from the empresa's mercado
    if empresa.mercado:
        form.fields['bolsas'].queryset = Bolsa.objects.filter(mercado=empresa.mercado)
    else:
        form.fields['bolsas'].queryset = Bolsa.objects.all()

    form.fields['bolsas'].widget.attrs.update({'class': 'form-control'})

    # Rest of empty fields to fill
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['public'].widget.attrs.update({'class': 'form-control'})

    # Attach fields configuration to the context
    context['form'] = form
    context['empresa'] = empresa

    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of '{empresa.title}'", "item":"Empresa"})
    return render (request, "administration/empresa/empresa_edit.html", context)

@login_required(login_url="/users/access")
def empresa_delete(request, empresa_id):
    """
    Function to delete an existing empresa
    """
    empresa = get_object_or_404(Empresa, id=empresa_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{empresa.title}'", "item":"Empresa"})
    empresa.delete()
    messages.success(request, "Empresa successfully deleted")
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    return redirect('/administration/empresas')

@login_required(login_url="/users/access")
def empresa_gallery(request, empresa_id):
    """
    Function to manage a gallery of an specific empresa
    """
    empresa = get_object_or_404(Empresa, id=empresa_id)
    context = {}
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_gallery = form.save(commit=False)
            image_gallery.empresa = empresa
            image_gallery.save()
            messages.success(request, "Image successfully added to gallery")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{image_gallery.title}'", "item":"Image"})
            return redirect(reverse('administration_empresa_gallery', kwargs={'empresa_id': empresa_id}))
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Invalid form", "item":"Image"})
        messages.error(request, form.errors)

    # Initialize the Form object
    form = ImageForm()

    # Rest of empty fields to fill
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})

    # Attach fields configuration to the context
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['empresa'] = empresa

    empresa = get_object_or_404(Empresa, id=empresa_id)
    context['images'] = empresa.images.all()

    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Image"})
    return render (request, "administration/empresa/empresa_gallery.html", context)


@login_required(login_url="/users/access")
def empresa_image_delete(request, image_id):
    """
    Function to delete an existing empresa image
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    image = get_object_or_404(Image, id=image_id)
    empresa = get_object_or_404(Empresa, id=image.empresa.id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{image.title}'", "item":"Image"})
    image.delete()
    messages.success(request, f"Empresa image '{image.title}' successfully deleted")
    return redirect(reverse('administration_empresa_gallery', kwargs={'empresa_id': empresa.id}))

######################################################################################################################################################
# CRUD+ADMIN USERS
######################################################################################################################################################


@login_required(login_url="/users/access")
def users(request):
    """
    Function to get all users
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['custom_users'] = CustomUser.objects.all().order_by('username')
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"CustomUser"})
    return render (request, "administration/user/users.html", context)

@login_required(login_url="/users/access")
def user_add(request):
    """
    Function to add a new user
    """
    context = {}
    if request.method == 'POST':
        form = CustomUserCreationByAdminForm(request.POST, request.FILES)
        if form.is_valid():
            custom_user = form.save(commit=False)
            custom_user.save()
            messages.success(request, f"User {custom_user.username} successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created {custom_user.username}", "item":"CustomUser"})
            return redirect('/administration/users')
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Invalid form", "item":"CustomUser"})

        context['errors'] = form.errors

    form = CustomUserCreationByAdminForm()
    form.fields['first_name'].widget.attrs.update({'class': 'form-control'})
    form.fields['last_name'].widget.attrs.update({'class': 'form-control'})
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['password1'].widget.attrs.update({'class': 'form-control'})
    form.fields['password2'].widget.attrs.update({'class': 'form-control'})
    form.fields['pic'].widget.attrs.update({'class': 'form-control'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"CustomUser"})
    return render (request, "administration/user/user_add.html", context)

@login_required(login_url="/users/access")
def user_edit(request, custom_user_id):
    """
    Function to edit an existing user
    """
    custom_user = get_object_or_404(CustomUser, id=custom_user_id)
    context = {}
    if request.method == 'POST':
        form = CustomUserEditByAdminForm(request.POST, request.FILES, instance=custom_user)
        if form.is_valid():
            custom_user.save()
            messages.success(request, f"User {custom_user.username} successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated {custom_user.username}", "item":"CustomUser"})
            return redirect('/administration/users')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating {custom_user.username}", "item":"CustomUser"})

        context['errors'] = form.errors

    form = CustomUserEditByAdminForm(instance=custom_user)
    form.fields['first_name'].widget.attrs.update({'class': 'form-control'})
    form.fields['last_name'].widget.attrs.update({'class': 'form-control'})
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['pic'].widget.attrs.update({'class': 'form-control'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['custom_user'] = get_object_or_404(CustomUser, id=custom_user_id)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of {custom_user.username}", "item":"CustomUser"})
    return render (request, "administration/user/user_edit.html", context)

@login_required(login_url="/users/access")
def user_delete(request, custom_user_id):
    """
    Function to delete an existing user
    """
    custom_user = get_object_or_404(CustomUser, id=custom_user_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted {custom_user.username}", "item":"CustomUser"})
    custom_user.delete()
    messages.success(request, f"User {custom_user.username} successfully deleted")
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    return redirect('/administration/users')

@login_required(login_url="/users/access")
def user_make_admin(request, custom_user_id):
    """
    Function to add or remove a user from the Administration group
    """
    custom_user = get_object_or_404(CustomUser, id=custom_user_id)
    admin_group = Group.objects.get(name='Administration')

    if custom_user.is_staff:
        log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Attempted to remove admin privileges to {custom_user.username}", "item":"CustomUser"})
        messages.success(request, f"Action not allowed. User {custom_user.username} is staff")
    elif admin_group in custom_user.groups.all():
        custom_user.groups.remove(admin_group)
        log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Removed admin privileges to {custom_user.username}", "item":"CustomUser"})
        messages.success(request, f"User {custom_user.username} removed from Administration group")
    else:
        custom_user.groups.add(admin_group)
        log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Added admin privileges to {custom_user.username}", "item":"CustomUser"})
        messages.success(request, f"User {custom_user.username} added to Administration group")

    return redirect('/administration/users')

@login_required(login_url="/users/access")
def user_deactivate_account(request, custom_user_id):
    """
    Function to activate or deactivate user account
    """
    custom_user = get_object_or_404(CustomUser, id=custom_user_id)

    if custom_user.is_staff:
        log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Attempted to deactivate account of admin {custom_user.username}", "item":"CustomUser"})
        messages.success(request, f"Action not allowed. User {custom_user.username} is staff")
    elif custom_user.is_active:
        custom_user.is_active = False  # Desactivar la cuenta
        custom_user.save()
        log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Deactivated account of {custom_user.username}", "item":"CustomUser"})
        messages.success(request, f"User {custom_user.username} account deactivated")
    else:
        custom_user.is_active = True  # Activar la cuenta
        custom_user.save()
        log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Activated account of {custom_user.username}", "item":"CustomUser"})
        messages.success(request, f"User {custom_user.username} account activated")

    return redirect('/administration/users')

@login_required(login_url="/users/access")
def user_change_password(request, custom_user_id):
    """
    Function to change user password by admin
    """
    from django.contrib.auth.forms import SetPasswordForm

    custom_user = get_object_or_404(CustomUser, id=custom_user_id)
    context = {}

    if request.method == 'POST':
        form = SetPasswordForm(custom_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Contraseña actualizada exitosamente para {custom_user.username}")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Changed password for {custom_user.username}", "item":"CustomUser"})
            return redirect('administration_user_edit', custom_user_id=custom_user_id)
        else:
            context['errors'] = form.errors
    else:
        form = SetPasswordForm(custom_user)

    # Add Bootstrap classes to form fields
    form.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingrese la nueva contraseña'})
    form.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirme la nueva contraseña'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['custom_user'] = custom_user

    return render(request, "administration/user/user_change_password.html", context)


######################################################################################################################################################
# CRUD SUBSCRIPTIONS
######################################################################################################################################################


@login_required(login_url="/users/access")
def subscriptions(request):
    """
    Function to get all subscriptions
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['subscriptions'] = Subscription.objects.all().order_by('-payment_datetime')
    context['today'] = timezone.now()
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Subscription"})
    return render (request, "administration/subscription/subscriptions.html", context)

@login_required(login_url="/users/access")
def subscription_add(request):
    """
    Function to add a new subscription
    """
    context = {}
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            receptor = subscription.user
            subscription.save()
            messages.success(request, f"Subscription #{subscription.pk} of {subscription.user} successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created #{subscription.id}", "item":"Subscription"})
            log(request, "SubscriptionLog", {"action_type":"create", "status":200, "details":f"Created #{subscription.id} by admin", "payment_gateway":f"{subscription.payment_method}", "receptor": receptor, "product":None})
            return redirect('/administration/subscriptions')
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Creating form", "item":"Subscription"})
            log(request, "SubscriptionLog", {"action_type":"create", "status":400, "details":f"Error creating subscription by admin", "payment_gateway":"", "receptor": None, "product":None})

        context['errors'] = form.errors


    form = SubscriptionForm()
    form.fields['user'].widget.attrs.update({'class': 'form-control'})
    form.fields['product'].widget.attrs.update({'class': 'form-control'})
    form.fields['amount'].widget.attrs.update({'class': 'form-control'})
    form.fields['currency'].widget.attrs.update({'class': 'form-control'})
    form.fields['payment_method'].widget.attrs.update({'class': 'form-control'})
    form.fields['payment_product_id'].widget.attrs.update({'class': 'form-control'})
    form.fields['payment_subscription_id'].widget.attrs.update({'class': 'form-control'})
    form.fields['status'].widget.attrs.update({'class': 'form-control'})
    form.fields['start_date'].widget.attrs.update({'class': 'form-control'})
    form.fields['due_date'].widget.attrs.update({'class': 'form-control'})

    # Pass products data for JavaScript
    from appmodels.models import Product
    products = Product.objects.filter(public=True).values('id', 'title', 'price', 'discount', 'interval_count', 'interval_unit')
    products_json = {}
    for product in products:
        products_json[product['id']] = {
            'title': product['title'],
            'price': float(product['price']),
            'discount': float(product['discount']),
            'interval_count': product['interval_count'],
            'interval_unit': product['interval_unit']  # Now sending 'Y', 'M', or 'W'
        }
    import json
    context['products_json'] = json.dumps(products_json)
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Subscription"})
    return render (request, "administration/subscription/subscription_add.html", context)

@login_required(login_url="/users/access")
def subscription_edit(request, subscription_id):
    """
    Function to edit an existing subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    context = {}
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            subscription.save()
            messages.success(request, f"Subscription #{subscription.pk} of {subscription.user} successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated #{subscription.id}", "item":"Subscription"})
            log(request, "SubscriptionLog", {"action_type":"update", "status":200, "details":f"Updated #{subscription.id} by admin", "payment_gateway":"", "product":None, "receptor": subscription.user})
            return redirect('/administration/subscriptions')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating subscription #{subscription.id}", "item":"Subscription"})
            log(request, "SubscriptionLog", {"action_type":"create", "status":400, "details":f"Error updating #{subscription.id} by admin", "payment_gateway":"", "product":None, "receptor": subscription.user})

        context['errors'] = form.errors


    form = SubscriptionForm(instance=subscription)
    form.fields['user'].widget.attrs.update({'class': 'form-control'})
    form.fields['product'].widget.attrs.update({'class': 'form-control'})
    form.fields['amount'].widget.attrs.update({'class': 'form-control'})
    form.fields['currency'].widget.attrs.update({'class': 'form-control'})
    form.fields['payment_method'].widget.attrs.update({'class': 'form-control'})
    form.fields['payment_product_id'].widget.attrs.update({'class': 'form-control'})
    form.fields['payment_subscription_id'].widget.attrs.update({'class': 'form-control'})
    form.fields['status'].widget.attrs.update({'class': 'form-control'})
    form.fields['start_date'].widget.attrs.update({'class': 'form-control'})
    form.fields['due_date'].widget.attrs.update({'class': 'form-control'})

    # Pass products data for JavaScript
    from appmodels.models import Product
    products = Product.objects.filter(public=True).values('id', 'title', 'price', 'discount', 'interval_count', 'interval_unit')
    products_json = {}
    for product in products:
        products_json[product['id']] = {
            'title': product['title'],
            'price': float(product['price']),
            'discount': float(product['discount']),
            'interval_count': product['interval_count'],
            'interval_unit': product['interval_unit']
        }
    import json
    context['products_json'] = json.dumps(products_json)
    context['form'] = form
    context['subscription'] = subscription
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of subscription #{subscription.id}", "item":"Subscription"})
    return render (request, "administration/subscription/subscription_edit.html", context)

@login_required(login_url="/users/access")
def subscription_cancel(request, subscription_id):
    """
    Function to cancel a subscription (changes status to CANCELED)
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    subscription.status = "CANCELED"
    subscription.save()
    messages.success(request, f"Subscription #{subscription.pk} of {subscription.user} successfully canceled")
    log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Canceled subscription #{subscription.id}", "item":"Subscription"})
    log(request, "SubscriptionLog", {"action_type":"cancel", "status":200, "details":f"Canceled subscription #{subscription.id} by admin", "payment_gateway":subscription.payment_method, "product":None, "receptor": subscription.user})
    return redirect('/administration/subscriptions')

@login_required(login_url="/users/access")
def subscription_delete(request, subscription_id):
    """
    Function to delete an existing subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    user = subscription.user
    subscription_pk = subscription.pk
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted subscription #{subscription_pk}", "item":"Subscription"})
    log(request, "SubscriptionLog", {"action_type":"delete", "status":200, "details":f"Deleted subscription #{subscription_pk} by admin", "payment_gateway":"", "product":None, "receptor": user})
    subscription.delete()
    messages.success(request, f"Subscription #{subscription_pk} of {user} successfully deleted")
    return redirect('/administration/subscriptions')

@login_required(login_url="/users/access")
def assign_product(request):
    """
    Function to assign a product schema to some user
    """
    context = {}
    config = get_object_or_404(GeneralConfig, id=1)

    if request.method == 'POST':
        form = ProductAssignForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            selected_product = form.cleaned_data['product']

            subscription_days = 0
            
            if selected_product.interval_unit == 'W':
                subscription_days = selected_product.interval_count * 7
            elif selected_product.interval_unit == 'M':
                subscription_days = selected_product.interval_count * 30
            elif selected_product.interval_unit == 'Y':
                subscription_days = selected_product.interval_count * 365

            subscription = Subscription.objects.create(
                user = selected_user,
                payment_datetime = timezone.now(),
                amount = selected_product.final_price,
                currency = config.currency,
                payment_method = 'Other',
                start_date = timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=subscription_days)
            )

            messages.success(request, f"Subscription #{subscription.pk} of {subscription.user} successfully created")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created #{subscription.id} by schema", "item":"Subscription"})
            log(request, "SubscriptionLog", {"action_type":"create", "status":200, "details":f"Created #{subscription.id} by schema", "payment_gateway":"", "product":selected_product, "receptor": {subscription.user}})
            return redirect('/administration/subscriptions')

    form = ProductAssignForm()
    form.fields['user'].widget.attrs.update({'class': 'form-control'})
    form.fields['product'].widget.attrs.update({'class': 'form-control'})
    context['form'] = form
    context['config'] = config
    return render(request, 'administration/subscription/assign_product.html', context)



    
######################################################################################################################################################
# CRUD PRODUCTS
######################################################################################################################################################


@login_required(login_url="/users/access")
def products(request):
    """
    Function to get all products
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['products'] = Product.objects.all().order_by('title')
    context['today'] = timezone.now()
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Product"})
    return render (request, "administration/product/products.html", context)

@login_required(login_url="/users/access")
def product_add(request):
    """
    Function to add a new product
    """
    context = {}
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            messages.success(request, f"Product #{product.pk} successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{product.title}'", "item":"Product"})
            return redirect('/administration/products')
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Creating form", "item":"Product"})

        context['errors'] = form.errors

    form = ProductForm()
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['price'].widget.attrs.update({'class': 'form-control'})
    form.fields['interval_count'].widget.attrs.update({'class': 'form-control'})
    form.fields['interval_unit'].widget.attrs.update({'class': 'form-control'})
    form.fields['discount'].widget.attrs.update({'class': 'form-control'})
    form.fields['public'].widget.attrs.update({'class': 'form-control'})
    form.fields['stripe_subscription_id'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['paypal_subscription_id'].widget.attrs.update({'class': 'form-control has-feedback-left'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Product"})
    return render (request, "administration/product/product_add.html", context)

@login_required(login_url="/users/access")
def product_edit(request, product_id):
    """
    Function to edit an existing product
    """
    product = get_object_or_404(Product, id=product_id)
    context = {}
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product.save()
            messages.success(request, f"Product #{product.pk} successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated '{product.title}'", "item":"Product"})
            return redirect('/administration/products')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating '{product.title}'", "item":"Product"})
        context['errors'] = form.errors

    form = ProductForm(instance=product)
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['price'].widget.attrs.update({'class': 'form-control'})
    form.fields['interval_count'].widget.attrs.update({'class': 'form-control'})
    form.fields['interval_unit'].widget.attrs.update({'class': 'form-control'})
    form.fields['discount'].widget.attrs.update({'class': 'form-control'})
    form.fields['public'].widget.attrs.update({'class': 'form-control'})
    form.fields['stripe_subscription_id'].widget.attrs.update({'class': 'form-control has-feedback-left'})
    form.fields['paypal_subscription_id'].widget.attrs.update({'class': 'form-control has-feedback-left'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of '{product.title}'", "item":"Product"})
    return render (request, "administration/product/product_edit.html", context)

@login_required(login_url="/users/access")
def product_delete(request, product_id):
    """
    Function to detete an existing product
    """
    product = get_object_or_404(Product, id=product_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{product.title}'", "item":"Product"})
    product_id = product.pk
    product.delete()
    messages.success(request, f"Product #{product_id} successfully deleted")
    return redirect('/administration/products')


######################################################################################################################################################
# LOGS
######################################################################################################################################################


@login_required(login_url="/users/access")
def logs(request):
    """
    Function to get all logs
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['user_logs'] = UserLog.objects.all().order_by('-timestamp')
    context['admin_logs'] = AdminsLog.objects.all().order_by('-timestamp')
    context['subscription_logs'] = SubscriptionLog.objects.all().order_by('-timestamp')
    context['tracking_logs'] = TrackingLog.objects.all().order_by('-timestamp')
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Log"})
    return render (request, "administration/general/logs.html", context)

@login_required(login_url="/users/access")
def get_log_details(request, log_type, log_id):
    """
    Funtion to get the details of specified log
    """
    context= {}
    context['config']= get_object_or_404(GeneralConfig, id=1)
    
    if log_type == 'user': 
        log_details= get_object_or_404(UserLog, id=log_id)
    elif log_type == 'admin':
        log_details= get_object_or_404(AdminsLog, id=log_id)
    elif log_type == 'subscription':
        log_details= get_object_or_404(SubscriptionLog, id=log_id)
    elif log_type == 'tracking':
        log_details= get_object_or_404(TrackingLog, id=log_id)

    context['log_details']= log_details
    context['log_type']= log_type
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Get Log Details", "item":"Log"})
    return render (request, "administration/general/modal_logs.html", context)

######################################################################################################################################################
# CRUD BLOG
######################################################################################################################################################


@login_required(login_url="/users/access")
def blogs(request):
    """
    Function to get all blog posts
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['blogs'] = Blog.objects.all().order_by('-datetime')
    context['today'] = timezone.now()
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Blog"})
    return render (request, "administration/blog/blogs.html", context)


@login_required(login_url="/users/access")
def blog_add(request):
    """
    Function to add a new post
    """
    context = {}
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, f"Post #{post.pk} successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{post.title}'", "item":"Blog"})
            return redirect('/administration/posts')
        else:
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Creating form", "item":"Blog"})

        context['errors'] = form.errors

    form = BlogForm()
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['pic'].widget.attrs.update({'class': 'form-control'})
    form.fields['url'].widget.attrs.update({'class': 'form-control'})
    form.fields['public'].widget.attrs.update({'class': 'form-control'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Blog"})
    return render (request, "administration/blog/blog_add.html", context)

@login_required(login_url="/users/access")
def blog_edit(request, blog_id):
    """
    Function to edit an existing post
    """
    post = get_object_or_404(Blog, id=blog_id)
    context = {}
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post.save()
            messages.success(request, f"Post #{post.pk} successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated '{post.title}'", "item":"Blog"})
            return redirect('/administration/posts')
        else:
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating '{post.title}'", "item":" Blog"})
        context['errors'] = form.errors

    form = BlogForm(instance=post)
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['description'].widget.attrs.update({'class': 'form-control'})
    form.fields['pic'].widget.attrs.update({'class': 'form-control'})
    form.fields['url'].widget.attrs.update({'class': 'form-control'})
    form.fields['public'].widget.attrs.update({'class': 'form-control'})

    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['post'] = post # Previous information
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of '{post.title}'", "item":"Blog"})
    return render (request, "administration/blog/blog_edit.html", context)

@login_required(login_url="/users/access")
def blog_delete(request, blog_id):
    """
    Function to detete an existing blog post
    """
    post = get_object_or_404(Blog, id=blog_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{post.title}'", "item":"Blog"})
    post_id = post.pk
    post.delete()
    messages.success(request, f"Post #{post_id} successfully deleted")
    return redirect('/administration/posts')


######################################################################################################################################################
# CRUD NOTICIAS
######################################################################################################################################################


@login_required(login_url="/users/access")
def noticias(request):
    """
    Function to get all noticias
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['noticias'] = Noticia.objects.all().order_by('-published_date')
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":"Listing", "item":"Noticia"})
    return render (request, "administration/noticia/noticias.html", context)

@login_required(login_url="/users/access")
def noticia_add(request):
    """
    Function to add a new noticia
    """
    context = {}
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.save()
            messages.success(request, "Noticia successfully added")
            log(request, "AdminsLog", {"action_type":"create", "status":200, "details":f"Created '{noticia.title}'", "item":"Noticia"})
            return redirect('/administration/noticias')
        else:
            messages.error(request, "Error adding noticia. Please check the form.")
            log(request, "AdminsLog", {"action_type":"create", "status":400, "details":f"Invalid form", "item":"Noticia"})

    # Initialize the Form object
    form = NoticiaForm()

    # Setup form fields
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['source'].widget.attrs.update({'class': 'form-control'})
    form.fields['source_url'].widget.attrs.update({'class': 'form-control'})
    form.fields['author'].widget.attrs.update({'class': 'form-control'})
    form.fields['image'].widget.attrs.update({'class': 'form-control'})
    form.fields['empresa'].widget.attrs.update({'class': 'form-control'})

    # Attach fields configuration to the context
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Creating form", "item":"Noticia"})
    return render (request, "administration/noticia/noticia_add.html", context)

@login_required(login_url="/users/access")
def noticia_edit(request, noticia_id):
    """
    Function to edit an existing noticia
    """
    noticia = get_object_or_404(Noticia, id=noticia_id)
    context = {}

    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            updated_noticia = form.save()
            messages.success(request, "Noticia successfully updated")
            log(request, "AdminsLog", {"action_type":"update", "status":200, "details":f"Updated '{updated_noticia.title}'", "item":"Noticia"})
            return redirect('/administration/noticias')
        else:
            messages.error(request, "Error updating noticia. Please check the form.")
            log(request, "AdminsLog", {"action_type":"update", "status":400, "details":f"Invalid form updating '{noticia.title}'", "item":"Noticia"})

    # Initialize the Form object with the existing noticia data
    form = NoticiaForm(instance=noticia)

    # Setup form fields
    form.fields['title'].widget.attrs.update({'class': 'form-control'})
    form.fields['source'].widget.attrs.update({'class': 'form-control'})
    form.fields['source_url'].widget.attrs.update({'class': 'form-control'})
    form.fields['author'].widget.attrs.update({'class': 'form-control'})
    form.fields['image'].widget.attrs.update({'class': 'form-control'})
    form.fields['empresa'].widget.attrs.update({'class': 'form-control'})

    # Attach fields configuration to the context
    context['form'] = form
    context['noticia'] = noticia
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "AdminsLog", {"action_type":"read", "status":200, "details":f"Update form of '{noticia.title}'", "item":"Noticia"})
    return render (request, "administration/noticia/noticia_edit.html", context)

@login_required(login_url="/users/access")
def noticia_delete(request, noticia_id):
    """
    Function to delete an existing noticia
    """
    noticia = get_object_or_404(Noticia, id=noticia_id)
    log(request, "AdminsLog", {"action_type":"delete", "status":200, "details":f"Deleted '{noticia.title}'", "item":"Noticia"})
    noticia.delete()
    messages.success(request, "Noticia successfully deleted")
    return redirect('/administration/noticias')