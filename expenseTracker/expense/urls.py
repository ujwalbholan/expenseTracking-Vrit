from django.urls import path
from . import views

urlpatterns = [
    path('setExpense/', views.set_expense_view, name='set_expense_view'),
    path('getAllExpense/', views.get_all_expense_view, name='get_all_expense_view'),
    path('getExpenseById/', views.get_expense_view_by_Id ,name='get_expense_view_by_Id'),
    path('editExpense/', views.edit_expense_view ,name='edit_expense_view'),
    path('deleteExpense/', views.delete_expense_view ,name='delete_expense_view'),
]