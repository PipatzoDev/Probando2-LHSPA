from django.shortcuts import render
from .models import Empleado,RegistroAsistencia,Proveedor,Transaccion
from django.views import generic
from django.utils import timezone
from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Count,F,Sum
from django.db.models import F, ExpressionWrapper, CharField
from django.contrib import messages
from django.contrib.auth.views import LoginView
    
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime, timedelta
from django.shortcuts import render

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from django.shortcuts import render
from google.oauth2 import service_account
from googleapiclient.discovery import build

from django.http import JsonResponse



SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

credentials = service_account.Credentials.from_service_account_file(
    'core/static/client_scret.json', scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)



# Create your views here.


@login_required
def employe_list(request):
    empleado = Empleado.objects.all()
    asistencia  = RegistroAsistencia.objects.all()
    cant_regis = RegistroAsistencia.objects.values('empleado').annotate(cantidad_registros=Count('id'))
    listadias = list(range(1, 32))
    array_asistencia = []
    
    
    # Obtener eventos del calendario
    events_result = service.events().list(calendarId='es.cl#holiday@group.v.calendar.google.com', timeMin='2023-10-01T00:00:00Z',timeMax='2023-10-31T23:59:59Z', maxResults=10, singleEvents=True,orderBy='startTime').execute()

    events = events_result.get('items', [])

    # Procesar los eventos
    event_list = []
    if not events:
        event_list.append({'start': 'No hay eventos próximos.', 'summary': ''})
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No hay resumen disponible.')
        event_list.append({'start': start, 'summary': summary})

    if request.method == "POST":
        form = EmpleadoForms(request.POST, request.FILES)
        form2 = AsistenciaForms(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
        elif form2.is_valid():
            post2 = form2.save(commit=False)
            post2.author = request.user
            post2.published_date = timezone.now()
            post2.save()
            return redirect('inicio')
    else:
        form = EmpleadoForms()
        form2 = AsistenciaForms(request.POST)

    return render(request,'index.html',{'empleado':empleado,'form':form,'asistencia':asistencia,'listadias':listadias,'cant_regis':cant_regis,'array_asistencia':array_asistencia,'events': event_list,'form2':form2})

@login_required
def dashboard(request):
    return render(request,'dashboards/dashboard.html')
@login_required
def proveedor(request):
    proveedores = Proveedor.objects.all()
    return render(request,'proveedores/proveedor.html',{'proveedores':proveedores})
@login_required
def finanza(request):
    trans = Transaccion.objects.all()
    return render(request,'finanzas/finanza.html',{'trans':trans})



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class EmpleadoDetailView(generic.DetailView):
    model = Empleado
    template_name = 'empleados/empleado_detail.html'
    context_object_name = 'empleado'
    

class EmpleadoListView(generic.ListView):
    model = Empleado


class EmpleadoCreate(CreateView):
    model = Empleado
    fields = '__all__'
    

class EmpleadoUpdate(UpdateView):
    model = Empleado
    template_name = 'empleados/empleado_mod.html'
    context_object_name = 'empleado'
    form_class = EmpleadoForms
    success_url = reverse_lazy('inicio')
    

class EmpleadoDelete(DeleteView):
    model = Empleado
    template_name = 'empleados/empleado_confirm_delete.html'
    success_url = reverse_lazy('inicio')
    context_object_name = 'empleado'


class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, 'Nombre de usuario o contraseña incorrectos.')
        return super().form_invalid(form)



#Proveedor
class ProveedorUpdate(UpdateView):
    model = Proveedor
    template_name = 'proveedores/proveedor_mod.html'
    context_object_name = 'proveedor'
    form_class = ProveedorForms
    success_url = reverse_lazy('proveedor')
    
class ProveedorDelete(DeleteView):
    model = Proveedor
    template_name = 'proveedores/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor')
    context_object_name = 'proveedor'