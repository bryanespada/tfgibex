from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from appmodels.models import GeneralConfig, Product, Mercado, Bolsa, Empresa, Blog, Image, Noticia, Subscription
from logs.models import TrackingLog
from django.db.models import Count
from logs.views import log
from django.utils import timezone


def user_is_premium(user):
    """
    Helper function to check if user has an active subscription
    Uses the same logic as the is_premium template tag
    """
    today = timezone.now().date()
    return Subscription.objects.filter(
        user=user,
        due_date__gte=today,
        status='ACTIVE'
    ).exists()


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
        context['mercado'] = selected_mercado
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Bolsa", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":selected_mercado})

    # Listing every bolsa
    else:
        context['bolsas'] = Bolsa.objects.all()
        context['mercado'] = None
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List every item", "item":"Bolsa", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":None})

    return render (request, "app/bolsas.html", context=context)

@login_required(login_url="/users/access")
def empresas(request, bolsa_id=None):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # In case of selected bolsa
    if bolsa_id:
        selected_bolsa = get_object_or_404(Bolsa, id=bolsa_id)
        context['empresas'] = Empresa.objects.filter(bolsas=bolsa_id)
        context['bolsa'] = selected_bolsa
        context['mercado'] = selected_bolsa.mercado
        context['bolsa_title'] = selected_bolsa.title
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Empresa", "has_active_subscription":False, "empresa":None, "bolsa":selected_bolsa, "mercado":selected_bolsa.mercado})

    # Listing every empresa
    else:
        context['empresas'] = Empresa.objects.all()
        context['bolsa'] = None
        context['mercado'] = None
        log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Empresa", "has_active_subscription":False, "empresa":None, "bolsa":None, "mercado":None})

    return render (request, "app/empresas.html", context=context)

@login_required(login_url="/users/access")
def empresa(request, empresa_id):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    selected_empresa = get_object_or_404(Empresa, id=empresa_id)
    context['empresa'] = selected_empresa

    context['images'] = selected_empresa.images.all()

    # Check if user has active subscription
    is_premium = user_is_premium(request.user)

    # Get related news for this company (filter premium if user is free)
    if is_premium:
        context['noticias'] = selected_empresa.noticias.filter(public=True).order_by('-published_date')
    else:
        context['noticias'] = selected_empresa.noticias.filter(public=True, is_premium=False).order_by('-published_date')

    # Como una empresa puede tener múltiples bolsas, tomamos la primera si existe
    first_bolsa = selected_empresa.bolsas.first() if selected_empresa.bolsas.exists() else None
    context['bolsa'] = first_bolsa
    context['mercado'] = selected_empresa.mercado

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"Element", "item":"Empresa", "has_active_subscription":is_premium, "empresa":selected_empresa, "bolsa":first_bolsa, "mercado":selected_empresa.mercado})
    return render (request, "app/empresa.html", context=context)


@login_required(login_url="/users/access")
def noticias(request):
    """
    Function to display all news to users
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # Check if user has active subscription
    is_premium = user_is_premium(request.user)

    # Filter news based on subscription status
    if is_premium:
        # Premium users see all public news
        context['noticias'] = Noticia.objects.filter(public=True).order_by('-published_date')
    else:
        # Free users only see non-premium news
        context['noticias'] = Noticia.objects.filter(public=True, is_premium=False).order_by('-published_date')

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"List", "item":"Noticia", "has_active_subscription":is_premium, "mercado":None, "bolsa":None, "empresa":None})
    return render(request, "app/noticias.html", context=context)


@login_required(login_url="/users/access")
def noticia(request, noticia_id):
    """
    Function to display a specific news article
    """
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    selected_noticia = get_object_or_404(Noticia, id=noticia_id, public=True)

    # Check if user has active subscription
    is_premium = user_is_premium(request.user)

    # If news is premium and user doesn't have subscription, deny access
    if selected_noticia.is_premium and not is_premium:
        messages.error(request, "Esta noticia requiere una suscripción activa para poder acceder.")
        return redirect('user_noticias')

    context['noticia'] = selected_noticia

    log(request, "TrackingLog", {"action_type":"read", "status":200, "details":"Element", "item":"Noticia", "has_active_subscription":is_premium, "empresa":selected_noticia.empresa, "bolsa":None, "mercado":selected_noticia.empresa.mercado if selected_noticia.empresa else None, "noticia":selected_noticia})
    return render(request, "app/noticia.html", context=context)


@login_required
def faq(request):
    config = GeneralConfig.objects.all().first()

    # FAQ data structure
    faqs = [
        {
            'category': 'General',
            'questions': [
                {
                    'question': '¿Qué es TFG IBEX?',
                    'answer': 'TFG IBEX es una plataforma de información financiera que proporciona noticias actualizadas, análisis y datos sobre empresas cotizadas en diferentes mercados bursátiles, con especial enfoque en el IBEX 35 y otros índices europeos y americanos.'
                },
                {
                    'question': '¿Necesito una cuenta para acceder al contenido?',
                    'answer': 'Sí, necesitas registrarte para acceder al contenido de la plataforma. Ofrecemos tanto cuentas gratuitas con acceso básico como suscripciones premium con acceso completo a todas las noticias y análisis.'
                },
                {
                    'question': '¿Cómo puedo registrarme?',
                    'answer': 'Puedes registrarte haciendo clic en el botón "Registrarse" en la página de inicio. Solo necesitas proporcionar tu correo electrónico, nombre y crear una contraseña.'
                }
            ]
        },
        {
            'category': 'Suscripción Premium',
            'questions': [
                {
                    'question': '¿Qué ventajas tiene la suscripción Premium?',
                    'answer': 'La suscripción Premium te da acceso ilimitado a todas las noticias, incluyendo contenido exclusivo, análisis en profundidad, informes especiales y acceso prioritario a nuevas funcionalidades.'
                },
                {
                    'question': '¿Cuánto cuesta la suscripción Premium?',
                    'answer': 'Ofrecemos diferentes planes de suscripción con precios competitivos. Puedes ver todos los detalles y precios actualizados en la sección de suscripción de tu perfil.'
                },
                {
                    'question': '¿Cómo puedo cancelar mi suscripción?',
                    'answer': 'Puedes cancelar tu suscripción en cualquier momento desde tu perfil de usuario en la sección "Suscripción". La cancelación será efectiva al final del período de facturación actual.'
                }
            ]
        },
        {
            'category': 'Contenido y Noticias',
            'questions': [
                {
                    'question': '¿Con qué frecuencia se actualiza el contenido?',
                    'answer': 'Nuestro contenido se actualiza continuamente a lo largo del día. Las noticias importantes se publican en tiempo real, mientras que los análisis y reportes especiales se publican regularmente.'
                },
                {
                    'question': '¿Puedo filtrar las noticias por empresa o mercado?',
                    'answer': 'Sí, puedes navegar por mercados específicos (Europeo, Americano, etc.), bolsas (IBEX, DAX, NYSE, NASDAQ) y empresas individuales para ver solo las noticias que te interesan.'
                },
                {
                    'question': '¿Las noticias incluyen análisis técnico?',
                    'answer': 'Las noticias premium pueden incluir análisis técnico, gráficos y proyecciones. El nivel de detalle depende del tipo de noticia y la fuente de información.'
                }
            ]
        },
        {
            'category': 'Navegación y Uso',
            'questions': [
                {
                    'question': '¿Cómo busco una empresa específica?',
                    'answer': 'Puedes usar la barra de búsqueda en las páginas de listado de empresas, o navegar a través de Mercados > Bolsas > Empresas para encontrar la empresa que buscas.'
                },
                {
                    'question': '¿Puedo guardar noticias para leer más tarde?',
                    'answer': 'Actualmente estamos trabajando en esta funcionalidad. Pronto podrás guardar tus noticias favoritas en tu perfil.'
                },
                {
                    'question': '¿La plataforma está disponible en dispositivos móviles?',
                    'answer': 'Sí, nuestra plataforma es totalmente responsive y se adapta a cualquier dispositivo. Puedes acceder desde tu móvil, tablet o computadora con la misma experiencia de usuario.'
                }
            ]
        },
        {
            'category': 'Cuenta y Perfil',
            'questions': [
                {
                    'question': '¿Cómo cambio mi contraseña?',
                    'answer': 'Puedes cambiar tu contraseña desde la página de tu perfil. Si olvidaste tu contraseña, puedes usar la opción "¿Olvidaste tu contraseña?" en la página de inicio de sesión.'
                },
                {
                    'question': '¿Puedo cambiar mi dirección de correo electrónico?',
                    'answer': 'No, actualmente no es posible cambiar la dirección de correo electrónico asociada a tu cuenta. El correo electrónico se usa como identificador único para el inicio de sesión y no puede ser modificado una vez creada la cuenta.'
                },
                {
                    'question': '¿Cómo elimino mi cuenta?',
                    'answer': 'Si deseas eliminar tu cuenta, por favor contacta con nuestro equipo de soporte. Ten en cuenta que esta acción es irreversible y perderás todo tu historial y configuración.'
                }
            ]
        }
    ]

    context = {
        "config": config,
        "faqs": faqs,
    }
    return render(request, "app/faq.html", context)


