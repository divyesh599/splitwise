from django.db import models

# Create your models here.
class User(models.Model):
    userId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobileNumber = models.CharField(max_length=20)

class Expense(models.Model):
    expenseId = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    createdById = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

class ExpensePaidBy(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = (('userId', 'expenseId'),)

class ExpenseOwedBy(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = (('userId', 'expenseId'),)