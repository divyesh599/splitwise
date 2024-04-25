from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from .serializers import UserSerializer, ExpenseSerializer, ExpensePaidBySerializer, ExpenseOwedBySerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status

# Create your views here.
def homePage(request):
    # return HttpResponse("Welcome to my Django Project")
    return render(request, "index.html")


def allUser(request):
    data = User.objects.all().values()
    return HttpResponse(data)



class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


@api_view(['POST'])
def add_expense(request):
    # Extract data from the request
    paid_by_user_id = request.data.get('paid_by_user_id')
    amount_paid = request.data.get('amount_paid')
    users_involved = request.data.get('users_involved')

    response_data = {
        'message': 'Expense added successfully',
        'paid_by_user_id': paid_by_user_id,
        'amount_paid': str(amount_paid),
        # 'amount_per_user': str(amount_per_user),
        'users_involved': users_involved
    }

    # Return JSON response
    return Response(response_data, status=status.HTTP_201_CREATED)

