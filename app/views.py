from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from appmodels.models import GeneralConfig, Product, Mercado, Bolsa, Empresa, Blog, Image, Noticia
from logs.models import TrackingLog
from django.db.models import Count
from logs.views import log


@login_required(login_url="/users/access")
def dashboard(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['blog'] = Blog.objects.filter(public=True).order_by("-datetime")

    # Chart data
    context['top_10'] = {}
    
    # Get Top10 Mercados
    context['top_10']['mercados'] = {}
    context['top_10']['mercados']['labels'] = []
    context['top_10']['mercados']['values'] = []
    top_10_mercados = TrackingLog.objects.filter(mercado__isnull=False).values('mercado').annotate(total=Count('mercado')).order_by('-total')[:10]
    context['top_10']['mercados']['show'] = True if top_10_mercados else False # Decide to show or not
    for index, block in enumerate(top_10_mercados): # Prepare two lists with de labels and values
        mercado = Mercado.objects.get(pk=block['mercado'])
        context['top_10']['mercados']['labels'].append(mercado.title)
        context['top_10']['mercados']['values'].append(block['total'])
    
    # Get Top10 Bolsas
    context['top_10']['bolsas'] = {}
    context['top_10']['bolsas']['labels'] = []
    context['top_10']['bolsas']['values'] = []
    top_10_bolsas = TrackingLog.objects.filter(bolsa__isnull=False).values('bolsa').annotate(total=Count('bolsa')).order_by('-total')[:10]
    context['top_10']['bolsas']['show'] = True if top_10_bolsas else False # Decide to show or not
    for index, block in enumerate(top_10_bolsas): # Prepare two lists with de labels and values
        bolsa = Bolsa.objects.get(pk=block['bolsa'])
        context['top_10']['bolsas']['labels'].append(bolsa.title)
        context['top_10']['bolsas']['values'].append(block['total'])
    
    # Get Top10 Empresas
    context['top_10']['empresas'] = {}
    context['top_10']['empresas']['labels'] = []
    context['top_10']['empresas']['values'] = []
    top_10_empresas = TrackingLog.objects.filter(empresa__isnull=False).values('empresa').annotate(total=Count('empresa')).order_by('-total')[:10]
    context['top_10']['empresas']['show'] = True if top_10_empresas else False
    for index, block in enumerate(top_10_empresas):
        empresa = Empresa.objects.get(pk=block['empresa'])
        context['top_10']['empresas']['labels'].append(empresa.title)
        context['top_10']['empresas']['values'].append(block['total'])

    log(request, "UserLog", {"action_type":"read", "status":200, "details":"", "item":"Dashboard", "change_by_admin":False})
    return render (request, "app/index.html", context=context)

@login_required(login_url="/users/access")
def mercados(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['mercados'] = Mercado.objects.all()

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Mercado", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":None})
    return render (request, "app/mercados.html", context=context)

@login_required(login_url="/users/access")
def bolsas(request, mercado_id=None):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # In case of selected mercado
    if mercado_id is not None:
        selected_mercado = get_object_or_404(Mercado, id=mercado_id) # Search the object to save it in the log
        context['bolsas'] = Bolsa.objects.filter(mercado=mercado_id)
        context['mercado_title']= selected_mercado.title
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Bolsa", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":selected_mercado})

    # Listing every bolsa
    else:
        context['bolsas'] = Bolsa.objects.all()
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List every item", "item":"Bolsa", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":None})

    return render (request, "app/bolsas.html", context=context)

@login_required(login_url="/users/access")
def empresas(request, bolsa_id=None):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # In case of selected bolsa
    if bolsa_id:
        selected_bolsa = get_object_or_404(Bolsa, id=bolsa_id)
        context['empresas'] = Empresa.objects.filter(bolsa=bolsa_id)
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Empresa", "has_active_subscription":False, "empresa":None, "bolsa":selected_bolsa, "mercado":selected_bolsa.mercado})

    # Listing every empresa
    else:
        context['empresas'] = Empresa.objects.all()
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Empresa", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":None})

    return render (request, "app/empresas.html", context=context)

@login_required(login_url="/users/access")
def empresa(request, empresa_id):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    selected_empresa = get_object_or_404(Empresa, id=empresa_id)
    context['empresa'] = selected_empresa

    context['images'] = selected_empresa.images.all()

    # Como una empresa puede tener múltiples bolsas, tomamos la primera si existe
    first_bolsa = selected_empresa.bolsas.first() if selected_empresa.bolsas.exists() else None
    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"Element", "item":"Empresa", "has_active_subscription":False, "empresa":selected_empresa, "bolsa":first_bolsa, "mercado":selected_empresa.mercado})
    return render (request, "app/empresa.html", context=context)


@login_required(login_url="/users/access")
def noticias(request):
    """
    Function to display all news to users
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # Get all public news ordered by date
    context['noticias'] = Noticia.objects.filter(public=True).order_by('-published_date')

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Noticia", "has_active_subscription":False, "mercado":None, "bolsa":None, "empresa":None})
    return render(request, "app/noticias.html", context=context)


@login_required(login_url="/users/access")
def noticia(request, noticia_id):
    """
    Function to display a specific news article
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    selected_noticia = get_object_or_404(Noticia, id=noticia_id, public=True)

    # Check if news is premium and user has subscription
    # TODO: Add subscription check logic here

    context['noticia'] = selected_noticia

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"Element", "item":"Noticia", "has_active_subscription":False, "empresa":selected_noticia.empresa, "bolsa":None, "mercado":selected_noticia.empresa.mercado if selected_noticia.empresa else None})
    return render(request, "app/noticia.html", context=context)


