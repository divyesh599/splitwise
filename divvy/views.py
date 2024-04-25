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
    expense_type = request.data.get('expense_type') ## str value out of this : ["EQUAL", "EXACT", "PERCENT"]
    desc = request.data.get('desc') ## str value
    amount_paid = request.data.get('total_amount')   ## integer value
    paid_by_user_id = request.data.get('paid_by')  ## dictionary format : { <user_id> : <amount_paid, in exact figure or in persentage>, ...}
    owed_by_user_id = request.data.get('owed_by')  ## dictionary format : { <user_id> : <amount_owed>, ...}


    try:
        if expense_type not in ["EQUAL", "EXACT", "PERCENT"]:
            raise ValueError("Expense type must be one out of these EQUAL, EXACT, PERCENT.")
        if not isinstance(desc, str):
            raise ValueError("desc must be a str.")
        if not isinstance(amount_paid, int):
            raise ValueError("amount paid must be a int value.")
        if not isinstance(paid_by_user_id, dict):
            raise ValueError("Paid by user id must be a dictionary format. { <user_id> : <amount_paid, in exact figure or in persentage>, ...}")
        if not isinstance(owed_by_user_id, dict):
            raise ValueError("Owed by user id must be a dictionary format. { <user_id> : <amount_owed>, ...}")
        paid_by = {}
        for key, val in paid_by_user_id:
            paid_by[int(key)]=round(val, 2)
        if sum(paid_by.values()) != round(amount_paid, 2):
            raise ValueError("**")
        
        # owed_by = {}
        # for key, val in owed_by_user_id:
        #     owed_by[int(key)]=round(val, 2)
        # if sum(paid_by.values()) != round(amount_paid, 2):
        #     raise ValueError("**")
        
        
    except Exception as e:
        return Response({'error': f'Invalid input data for request parameters. {e}'}, status=status.HTTP_400_BAD_REQUEST)

    # Construct JSON response
    # response_data = {
    #     'message': 'Expense added successfully',
    #     'paid_by_user_id': paid_by_user_id,
    #     'amount_paid': amount_paid,
    #     'expense_type': expense_type,
    #     'users_involved': users_id_involved,
    # }

    # Return JSON response
    return Response(request.data, status=status.HTTP_201_CREATED)
 
