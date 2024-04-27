from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from .serializers import (
    UserSerializer,
    ExpenseSerializer,
    ExpensePaidBySerializer,
    ExpenseOwedBySerializer,
)

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status

from django.db.models import Sum



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


# class ExpenseListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Expense.objects.all()
#     serializer_class = ExpenseSerializer


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
        raise ValueError(
            f"Total amount does not match the specified total amount of {expected_total}."
        )


def validate_created_by(created_by_id, user_id_list):
    if created_by_id not in user_id_list:
        raise ValueError(f"Invalid created by user ID '{created_by_id}'.")


@api_view(["POST"])
def add_expense(request):
    # Extract data from the request
    exp_type = request.data.get("expense_type")
    desc = request.data.get("desc")
    amt = request.data.get("total_amount")
    paid_by = request.data.get("paid_by")
    owed_by = request.data.get("owed_by")
    created_by_id = request.data.get("created_by_id")

    # Get list of user IDs from the database
    uid_list = list(User.objects.values_list("userId", flat=True))

    # Define validation functions
    def validate_input():
        validate_exp_type(exp_type)
        validate_desc(desc)
        validate_total_amt(amt)
        validate_user_ids(paid_by, uid_list, "paid_by")
        validate_user_ids(owed_by, uid_list, "owed_by")
        validate_total(paid_by, amt)
        if exp_type == "EQUAL":
            validate_total(owed_by, 0)
        elif exp_type == "EXACT":
            validate_total(owed_by, amt)
        elif exp_type == "PERCENT":
            validate_total(owed_by, 100)
        validate_created_by(created_by_id, uid_list)

    # Validate input data
    try:
        validate_input()
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Create and save the new expense object
    expense = Expense.objects.create(
        desc=desc,
        amount=amt,
        createdById_id=created_by_id
    )
    expense_id = expense.expenseId

    # Create ExpensePaidBy objects for each user who paid
    exp_paid = [
        ExpensePaidBy(
            expenseId_id=expense_id,
            userId_id=int(uid),
            amount=round(val, 2)
        )
        for uid, val in paid_by.items()
    ]

    # Use bulk_create to insert all expenses paid by into the database
    ExpensePaidBy.objects.bulk_create(exp_paid)

    # Create ExpenseOwedBy objects based on expense type
    exp_owed = []
    if exp_type == "EQUAL":
        # Calculate equal amount owed by each user
        val = round(amt / len(uid_list), 2)
        thresh = amt - val * len(uid_list)
        exp_owed = [
            ExpenseOwedBy(
                expenseId_id=expense_id,
                userId_id=int(uid),
                amount=val + thresh if i == 0 else val,
            )
            for i, uid in enumerate(uid_list)
        ]
    elif exp_type == "EXACT":
        # Create ExpenseOwedBy objects with exact amounts owed
        exp_owed = [
            ExpenseOwedBy(
                expenseId_id=expense_id,
                userId_id=int(uid),
                amount=round(val, 2)
            )
            for uid, val in owed_by.items()
        ]
    elif exp_type == "PERCENT":
        # Create ExpenseOwedBy objects with amounts calculated based on percentage
        exp_owed = [
            ExpenseOwedBy(
                expenseId_id=expense_id,
                userId_id=int(uid),
                amount=round((amt * val) / 100, 2),
            )
            for uid, val in owed_by.items()
        ]

    # Use bulk_create to insert all expenses owed by into the database
    ExpenseOwedBy.objects.bulk_create(exp_owed)

    # Return success response
    return Response({'message': f'Expense successfully added, EID : {expense_id}'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def show_expenses(request, user_id=None):
    if user_id:
        # Get expenses for the specified user
        user_expenses = Expense.objects.filter(createdById_id=user_id)
        serializer = ExpenseSerializer(user_expenses, many=True)
        return Response(serializer.data)
    else:
        # Get balances for everyone
        users = User.objects.all()
        balances = {}
        for user in users:
            expenses_paid = ExpensePaidBy.objects.filter(userId_id=user.userId).aggregate(total_paid=Sum('amount'))['total_paid'] or 0
            expenses_owed = ExpenseOwedBy.objects.filter(userId_id=user.userId).aggregate(total_owed=Sum('amount'))['total_owed'] or 0
            balance = expenses_paid - expenses_owed
            balances[user.name] = balance
        return Response(balances)
