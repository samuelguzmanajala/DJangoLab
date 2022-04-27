"""
Definition of views.
"""
from app.models import Pelicula, Critico
from django.http import HttpRequest
from datetime import datetime
from django.template import RequestContext
from app.forms import RegistroForm #/filmak/forms.py fitxategian sortu dudan erregistratzeko formularioa
from django.contrib.auth import authenticate, login as auth_login, logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
#"from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import Form
from app.forms import PeliculaForm
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
def login(request):  
	#Dagoeneko logetuta dago
    if request.user.is_authenticated():
        return render(request, 'app/index.html')
	#GET eskaera bada, login formularioa pantailaratu
    if request.method == "GET":
        return render(request, 'app/login.html')	
	#POST eskaera bada erabiltzaile eta pasahitza kautotu
    if request.method == "POST": #""POST":
        error = False #Login okerra bada True
        user = authenticate(username=request.POST['username'], password=request.POST['pass'])
		#Login zuzena
        if user is not None:
            auth_login(request, user)
            return render(request, 'aqpp/index.html')
        else: #Login okerra
            error = True #Login okerra beraz mezua adieraziko zaio txantiloilan
            return render(request, 'app/login.html', {'error': error})

def registro(request):
	#Dagoeneko logetuta dago
    if request.user.is_authenticated:
        return render(request, '/index.html')
	#GET eskaera eginez formularioa sortu
    if request.method == "GET":
        form = RegistroForm()#/filmak/forms.py fitxategian sortu dudan formularioa
        return render(request, 'app/registro.html',{'form': form})
	#POST eskaera eginez, erabiltzaile berria sortu
    if request.method == "POST":
        error = False #Pasahitza berdinak ez badira, errorea ateratzeko
        form = RegistroForm(request.POST) #/filmak/forms.py fitxategian sortu dudan formularioa
        if form.is_valid(): #Formularioa baliozkoa da
            if request.POST['pass1'] == request.POST['pass2']:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['pass1'])
                user.save()
                return HttpResponseRedirect('../login')
            else:
                error = True #Pasahitzak ez dira berdinak beraz mezua aterako zaio txantiloilan
                return render(request, 'app/registro.html', {'form': form, 'error': error})
        else: #Formularioa ez da baliozkoa
            return render(request, 'app/registro.html', {'form': form})

def peliculas(request):
	#Erabiltzailea logeatu gabe badago, berbideratu loginera
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/login')
	#Erabiltzailea logeatuta, filmak bistaratu
	else:
		film_lista = Pelicula.objects.all()
		paginator = Paginator(film_lista, 4)
		page = request.GET.get('page')
		try:
			pelis = paginator.page(page)
		except PageNotAnInteger:
			#Orria ez bada integer, lehengo orria.
			pelis = paginator.page(1)
		except EmptyPage:
			#Orria rangotik kanpo badago, azkena erakutsi.
			pelis = paginator.page(paginator.num_pages)
		return render(request, 'app/peliculas.html', {'pelis': pelis})

def voto(request):
    #Erabiltzailea logeatu gabe badago, berbideratu loginera
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
	#GET eskaera eginez, formularioa sortu
    if request.method == "GET":
        pelis = Pelicula.objects.all()
        return render(request, 'app/voto.html', {"pelis": pelis})
    #POST eskaera bada bozketa burutu
    if request.method == "POST":
        pelis = Pelicula.objects.all() #Filmak lortu
        emaitza = False
        bozka = request.POST['aukera'] #Erabiltzailearen aukera
        emaitza = votar(request, bozka) #Bozkatzaileari deia (Behean)
        return render(request, 'app/voto.html', {"resultados": emaitza, "pelis": pelis, "voto": bozka}) #Erabiltzaileari feedback-a

def favoritas(request):
#    #Erabiltzailea logeatu gabe badago, berbideratu loginera
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    #GET eskaera eginez, formularioa sortu
    if request.method == "GET":
        pelis = Pelicula.objects.all()
        print(pelis)
        return render(request, 'app/favoritas.html', {"pelis": pelis})
        #POST eskaera bada bozketa burutu
    if request.method == "POST":
        pelis = Pelicula.objects.all() #Filmak lortu
        aukera = request.POST['aukera'] #Erabiltzailearen aukera
        zale_lista = Pelicula.objects.get(titulo=aukera).critico_set.all()#Zaleak eskuratu
        erakutsi = True
        return render(request, 'app/favoritas.html', {"pelis": pelis, "zale_lista": zale_lista, "erakutsi": erakutsi, "aukera": aukera}) #Erabiltzaileari feedback-a

def votar(request, bozka):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    emaitza=0
    erab = request.user.id #Uneko erabiltzailearen id-a
    filma = Pelicula.objects.get(titulo=bozka) #Bozkatu nahi den filmaren objektua
    #Bozkatzaile berria bada
    if (Critico.objects.filter(usuario_id=erab).count() == 0):
        erab = User.objects.get(id=request.user.id)
        b = Critico(usuario_id=erab)
        b.save() ###HEMEN BOZKATZAILEA TAULA BETETZEN DUT ERABILTZAILE BERRIAREKIN
        b.favoritas.add(filma)#HEMEN GOGOKOFILMAK TAULA BETETZEN DUT
        filma.votos = filma.votos + 1
        filma.save()
        emaitza=1
    else: #Dagoeneko bozkatzailea da
        b = Critico.objects.get(usuario_id=erab)
        if (filma not in b.favoritas.all()):
            b.favoritas.add(filma)
            filma.votos = filma.votos + 1
            filma.save()
            emaitza=1
        else:
            emaitza=2
    return emaitza

def new_pelicula(request):
    if request.user.is_superuser:
        if request.method == "POST":
            form = PeliculaForm(request.POST)
            if form.is_valid():
                peli = form.save(commit=False)
                peli.save()
                return HttpResponseRedirect('/peliculas')
                #return redirect('detail', pk=question_id)
                #return render(request, 'app/peliculas.html', {'title':'Respuestas posibles','question': question})
        else:
            form = PeliculaForm()
            return render(request, 'app/new_pelicula.html', {'form': form})
    else:
        return HttpResponseRedirect('/login/')
