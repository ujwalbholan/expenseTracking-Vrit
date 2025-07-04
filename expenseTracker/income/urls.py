from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('setIncome/', views.set_income_view, name='set_income_view'),
    path('getAllIncomes/', views.get_all_incomes_view, name='get_all_incomes_view'),
    path('getIncomeById/', views.get_income_view_by_Id ,name='get_income_view_by_Id'),
    path('editIncome/', views.edit_income_view ,name='edit_income_view'),
    path('deleteIncome/', views.delete_income_view ,name='delete_income_view'),
]