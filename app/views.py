from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from appmodels.models import GeneralConfig, Product, Mercado, SurgeryType, PeripheralBlock, Blog, Image
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
    
    # Get Top10 Surgery Types
    context['top_10']['surgery_types'] = {}
    context['top_10']['surgery_types']['labels'] = []
    context['top_10']['surgery_types']['values'] = []
    top_10_surgery_Types = TrackingLog.objects.filter(surgery_type__isnull=False).values('surgery_type').annotate(total=Count('surgery_type')).order_by('-total')[:10]
    context['top_10']['surgery_types']['show'] = True if top_10_surgery_Types else False # Decide to show or not 
    for index, block in enumerate(top_10_surgery_Types): # Prepare two lists with de labels and values
        surgery_type = SurgeryType.objects.get(pk=block['surgery_type'])
        context['top_10']['surgery_types']['labels'].append(surgery_type.title)
        context['top_10']['surgery_types']['values'].append(block['total'])
    
    # Get Top10 Peripheral Blocks
    context['top_10']['peripheral_blocks'] = {}
    context['top_10']['peripheral_blocks']['labels'] = []
    context['top_10']['peripheral_blocks']['values'] = []
    top_10_peripheral_blocks = TrackingLog.objects.filter(peripheral_block__isnull=False).values('peripheral_block').annotate(total=Count('peripheral_block')).order_by('-total')[:10]
    context['top_10']['peripheral_blocks']['show'] = True if top_10_peripheral_blocks else False # Decide to show or not 
    for index, block in enumerate(top_10_peripheral_blocks): # Prepare two lists with de labels and values
        peripheral_block = PeripheralBlock.objects.get(pk=block['peripheral_block'])
        context['top_10']['peripheral_blocks']['labels'].append(peripheral_block.title)
        context['top_10']['peripheral_blocks']['values'].append(block['total'])

    log(request, "UserLog", {"action_type":"read", "status":200, "details":"", "item":"Dashboard", "change_by_admin":False})
    return render (request, "app/index.html", context=context)

@login_required(login_url="/users/access")
def mercados(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['mercados'] = Mercado.objects.all()

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Mercado", "has_active_subscription":False, "peripheral_block":None, "surgery_type":None, "mercado":None})
    return render (request, "app/mercados.html", context=context)

@login_required(login_url="/users/access")
def surgery_types(request, mercado_id=None):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # In case of selected mercado
    if mercado_id is not None:
        selected_mercado = get_object_or_404(Mercado, id=mercado_id) # Search the object to save it in the log
        context['surgery_types'] = SurgeryType.objects.filter(mercado=mercado_id)
        context['mercado_title']= selected_mercado.title
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"SurgeryType", "has_active_subscription":False, "peripheral_block":None, "surgery_type":None, "mercado":selected_mercado})

    # Listing every surgery type
    else:
        context['surgery_types'] = SurgeryType.objects.all()
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List every item", "item":"SurgeryType", "has_active_subscription":False, "peripheral_block":None, "surgery_type":None, "mercado":None})
    
    return render (request, "app/surgery_types.html", context=context)

@login_required(login_url="/users/access")
def peripheral_blocks(request, surgery_type_id=None):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # In case of selected surgery_type
    if surgery_type_id:
        selected_surgery_type = get_object_or_404(SurgeryType, id=surgery_type_id)
        context['peripheral_blocks'] = PeripheralBlock.objects.filter(surgery_type=surgery_type_id)
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"PeripheralBlock", "has_active_subscription":False, "peripheral_block":None, "surgery_type":selected_surgery_type, "mercado":selected_surgery_type.mercado})
    
    # Listing every surgery type
    else:
        context['peripheral_blocks'] = PeripheralBlock.objects.all()
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"PeripheralBlock", "has_active_subscription":False, "peripheral_block":None, "surgery_type":None, "mercado":None})
    
    return render (request, "app/peripheral_blocks.html", context=context)

@login_required(login_url="/users/access")
def peripheral_block(request, peripheral_block_id):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    selected_peripheral_block = get_object_or_404(PeripheralBlock, id=peripheral_block_id)
    context['peripheral_block'] = selected_peripheral_block
    
    context['images'] = selected_peripheral_block.images.all()

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"Element", "item":"PeripheralBlock", "has_active_subscription":False, "peripheral_block":selected_peripheral_block, "surgery_type":selected_peripheral_block.surgery_type, "mercado":selected_peripheral_block.surgery_type.mercado})
    return render (request, "app/peripheral_block.html", context=context)


