from django.shortcuts import render
from .models import Empleado,RegistroAsistencia,Proveedor,Transaccion
from django.views import generic
from django.utils import timezone
from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import datetime,timedelta
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
import os,calendar 
from calendar import monthrange

# Obtén el directorio base de tu proyecto Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construye la ruta al archivo client_scret.json usando BASE_DIR
json_file_path = os.path.join(BASE_DIR, 'core/static/client_scret.json')

# Ahora, puedes usar json_file_path en lugar de 'core/static/client_scret.json' en tu código

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

credentials = service_account.Credentials.from_service_account_file(
    json_file_path, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)



# Create your views here.


@login_required
def employe_list(request):
    empleado = Empleado.objects.all()
    asistencia  = RegistroAsistencia.objects.all()
    cant_regis = RegistroAsistencia.objects.values('empleado').annotate(cantidad_registros=Count('id'))
    listadias = list(range(1, 32))
    array_asistencia = []
    
    

     # Obtener el mes y el año actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year

    ##
        # Obtener el mes y año actuales
    now = datetime.now()
    month = now.month
    year = now.year

    # Obtener todas las semanas del mes actual
    cal = calendar.monthcalendar(year, month)

    # Obtener los nombres de los días de la semana
    days_of_week = calendar.day_name

    # Obtener el nombre del mes actual
    month_name = now.strftime("%B")

    # Combinar los nombres de los días de la semana, los nombres de los días del mes y el nombre del mes
    table_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(("",""))
            else:
                week_data.append((calendar.day_name[calendar.weekday(year, month, day)], day))
        table_data.append(week_data)
    ##
    # Obtener los nombres de los días de la semana
    dias_de_la_semana = calendar.month_name

    # Obtener los números de los días del mes actual
    dias_del_mes = calendar.monthcalendar(año_actual, mes_actual)
    
    # Obtén el primer y último día del mes actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year

    primer_dia_mes = datetime(año_actual, mes_actual, 1, 0, 0, 0).isoformat() + 'Z'

    if mes_actual == 12:
        siguiente_mes = 1
        siguiente_año = año_actual + 1
    else:
        siguiente_mes = mes_actual + 1
        siguiente_año = año_actual

    ultimo_dia_mes = (datetime(siguiente_año, siguiente_mes, 1, 0, 0, 0) - timedelta(seconds=1)).isoformat() + 'Z'
    
    # Obtener eventos del calendario
    events_result = service.events().list(calendarId='es.cl#holiday@group.v.calendar.google.com', timeMin=primer_dia_mes,timeMax=ultimo_dia_mes, maxResults=10, singleEvents=True,orderBy='startTime').execute()

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
    
    tabla_asistencia = generar_tabla_asistencia_mes_actual()

    return render(request,'index.html',{'empleado':empleado,'form':form,'asistencia':asistencia,'listadias':listadias,'cant_regis':cant_regis,'array_asistencia':array_asistencia,'events': event_list,'form2':form2,'table_data':table_data,'tabla_asistencia':tabla_asistencia})


def generar_tabla_asistencia_mes_actual():
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    dias_en_mes = monthrange(anio_actual, mes_actual)[1]

    empleados = Empleado.objects.all()

    tabla_asistencia = []

    for empleado in empleados:
            fila_asistencia = {
                'nombre': empleado.nombre,
                'apellido': empleado.apellido,
                'rut': empleado.rut,
                'imagen': empleado.imageEmp.url,  # Asegúrate de usar el nombre del campo correcto en tu modelo
                'asistencias': []
            }
            dias_asistidos = 0

            for dia in range(1, dias_en_mes + 1):
                fecha = datetime(anio_actual, mes_actual, dia)
                asistencia = RegistroAsistencia.objects.filter(empleado=empleado, fecha=fecha).exists()

                if asistencia:
                    fila_asistencia['asistencias'].append('✔')  # '✔' para asistencia
                    dias_asistidos += 1
                else:
                    fila_asistencia['asistencias'].append('✘')  # '✘' para ausencia

            fila_asistencia['dias_asistidos'] = dias_asistidos
            tabla_asistencia.append(fila_asistencia)

    return tabla_asistencia

@login_required
def dashboard(request):
    
    return render(request,'dashboards/dashboard.html',{})
@login_required
def proveedor(request):
    if request.method == "POST":
        form = ProveedorForms(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('proveedor')
    else:
        form = ProveedorForms()
    proveedores = Proveedor.objects.all()
    return render(request,'proveedores/proveedor.html',{'proveedores':proveedores,'form':form})
@login_required
def finanza(request):
    trans = Transaccion.objects.all()
    if request.method == "POST":
        form = TransaccionForms(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('finanza')
    else:
        form = TransaccionForms()
    return render(request,'finanzas/finanza.html',{'trans':trans,'form':form})



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


#Empleado
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

#Login
class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, 'Nombre de usuario o contraseña incorrectos.')
        return super().form_invalid(form)



#Proveedor
class ProveedorDetailView(generic.DetailView):
    model = Proveedor
    template_name = 'proveedores/proveedor_detail.html'
    context_object_name = 'proveedor'

    
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