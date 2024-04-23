from django.contrib import admin
from .models import User, Expense, ExpensePaidBy, ExpenseOwedBy

# Define admin classes for each model
class UserAdmin(admin.ModelAdmin):
    list_display = ['userId', 'name', 'email', 'mobileNumber']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expenseId', 'desc', 'amount', 'createdById', 'createdAt']

class ExpensePaidByAdmin(admin.ModelAdmin):
    list_display = ['userId', 'expenseId', 'amount']

class ExpenseOwedByAdmin(admin.ModelAdmin):
    list_display = ['userId', 'expenseId', 'amount']

# Register your models with their respective admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(ExpensePaidBy, ExpensePaidByAdmin)
admin.site.register(ExpenseOwedBy, ExpenseOwedByAdmin)