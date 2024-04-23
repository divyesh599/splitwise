from django.shortcuts import render
from django.http import HttpResponse
from divvy.models import User, Expense, ExpensePaidBy, ExpenseOwedBy

# Create your views here.
def homePage(request):
    # return HttpResponse("Welcome to my Django Project")
    return render(request, "index.html")


def allUser(request):
    data = User.objects.all().values()
    return HttpResponse(data)