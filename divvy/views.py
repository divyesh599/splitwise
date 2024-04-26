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


def validate_exp_type(exp_type):
    if exp_type not in ["EQUAL", "EXACT", "PERCENT"]:
        raise ValueError("Expense type must be one of: EQUAL, EXACT, PERCENT.")

def validate_desc(desc):
    if not isinstance(desc, str):
        raise ValueError("Description must be a string.")

def validate_total_amt(amt):
    if not isinstance(amt, int):
        raise ValueError("Total amount must be an integer.")

def validate_user_ids(user_ids, user_id_list, field_name):
    for uid, amt in user_ids.items():
        if int(uid) not in user_id_list:
            raise ValueError(f"Invalid user ID '{uid}' in '{field_name}'.")
        if not isinstance(amt, (int, float)):
            raise ValueError("Amount must be a number.")

def validate_total(total_dict, expected_total):
    if sum(total_dict.values()) != expected_total:
        raise ValueError(f"Total amount does not match the specified total amount of {expected_total}.")

def validate_created_by(created_by_id, user_id_list):
    if int(created_by_id) not in user_id_list:
        raise ValueError(f"Invalid created by user ID '{created_by_id}'.")

@api_view(['POST'])
def add_expense(request):
    exp_type = request.data.get('expense_type')
    desc = request.data.get('desc')
    amt = request.data.get('total_amount')
    paid_by = request.data.get('paid_by')
    owed_by = request.data.get('owed_by')
    created_by_id = request.data.get('created_by_id')

    user_id_list = list(User.objects.values_list('userId', flat=True))

    try:
        validate_exp_type(exp_type)
        validate_desc(desc)
        validate_total_amt(amt)
        validate_user_ids(paid_by, user_id_list, 'paid_by')
        validate_user_ids(owed_by, user_id_list, 'owed_by')
        validate_total(paid_by, amt)
        if exp_type == "EQUAL":
            validate_total(owed_by, 0)
        elif exp_type == "EXACT":
            validate_total(owed_by, amt)
        elif exp_type == "PERCENT":
            validate_total(owed_by, 100)
        validate_created_by(created_by_id, user_id_list)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # # Create and save the new expense object
    # expense = Expense.objects.create(desc=desc, amount=amt, createdById_id=created_by_id)

    # # Get the expense ID
    # expense_id = expense.expenseId

    
    return Response(request.data, status=status.HTTP_201_CREATED)
