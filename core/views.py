from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from appmodels.models import GeneralConfig

@login_required(login_url="/users/access")
def index(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrators').exists():
            return redirect('/administration/dashboard')
        else:
            return redirect('/app/dashboard')
    return redirect('/users/access')



def custom_403(request, exception):
    config = get_object_or_404(GeneralConfig, id=1)
    context ={ 'config': config }
    return render(request, 'errors/403.html', status=403, context=context)

def custom_404(request, exception):
    config = get_object_or_404(GeneralConfig, id=1)
    context ={ 'config': config }
    return render(request, 'errors/404.html', status=404, context=context)

def custom_500(request):
    config = get_object_or_404(GeneralConfig, id=1)
    context ={ 'config': config }
    return render(request, 'errors/500.html', status=500, context=context)