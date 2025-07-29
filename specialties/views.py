from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required  
def index(request):
    return render(request, 'specialties/index.html', {'title': 'Especialidades'})

@login_required
def nutrition(request):
    return render(request, 'specialties/nutrition.html', {'title': 'Nutrición'})

@login_required
def psychology(request):
    return render(request, 'specialties/psychology.html', {'title': 'Psicología'})

@login_required
def pediatrics(request):
    return render(request, 'specialties/pediatrics.html', {'title': 'Pediatría'})

@login_required
def ophthalmology(request):
    return render(request, 'specialties/ophthalmology.html', {'title': 'Oftalmología'})

@login_required
def dentistry(request):
    return render(request, 'specialties/dentistry.html', {'title': 'Odontología'})

