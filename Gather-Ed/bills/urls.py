from django.urls import path
from . import views

app_name = 'bills'

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.create_bill, name='create_bill'),
    path('<int:bill_id>/', views.bill_detail, name='bill_detail'),
    path('<int:bill_id>/expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('<int:bill_id>/settlements/record/', views.record_settlement, name='record_settlement'),
    path('settlements/<int:settlement_id>/confirm/', views.confirm_settlement, name='confirm_settlement'),
    path('settlements/<int:settlement_id>/reject/', views.reject_settlement, name='reject_settlement'),
    path('<int:bill_id>/toggle-settlement/', views.toggle_bill_settlement, name='toggle_bill_settlement'),
    path('summary/', views.user_summary, name='user_summary'),
]