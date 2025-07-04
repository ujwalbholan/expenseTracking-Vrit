from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Expense
import datetime
import json

@csrf_exempt
def set_expense_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            amount = request.POST.get('amount')
            source = request.POST.get('source')
            date = request.POST.get('date')
            notes = request.POST.get('notes', '')
            tax = request.POST.get('tax', 0)
            tax_type = request.POST.get('tax_type', 'flat').lower()
            transaction_type = request.POST.get('transaction_type')

            # Validate required fields
            if not all([name, amount, source, date, transaction_type]):
                return JsonResponse({'message': 'Missing required fields'}, status=400)

            # Validate transaction_type
            if transaction_type not in ['credit', 'debit']:
                return JsonResponse({'message': "transaction_type must be 'credit' or 'debit'"}, status=400)

            expense = Expense.objects.create(
                name=name,
                amount=amount,
                source=source,
                date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                notes=notes,
                tax=tax,
                tax_type=tax_type,
                transaction_type=transaction_type
            )

            if expense.tax_type == 'flat':
                total = float(expense.amount) + float(expense.tax)
            elif expense.tax_type == 'percentage':
                total = float(expense.amount) + (float(expense.amount) * float(expense.tax) / 100)
            else:
                total = float(expense.amount)

            return JsonResponse({
                'message': 'Expese saved successfully',
                'Expese': {
                    'id': expense.id,
                    'name': expense.name,
                    'amount': float(expense.amount),
                    'source': expense.source,
                    'date': expense.date.strftime('%Y-%m-%d'),
                    'notes': expense.notes,
                    'tax': float(expense.tax),
                    'tax_type': expense.tax_type,
                    'transaction_type': expense.transaction_type,
                    'total': round(total, 2),
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({'message': 'Error processing request', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_all_expense_view(request):
    if request.method == 'GET':
        expenses = Expense.objects.all().order_by('-date')

        # Get pagination parameters from query string
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        try:
            per_page = int(request.GET.get('per_page', 10))
        except ValueError:
            per_page = 10

        paginator = Paginator(expenses, per_page)

        try:
            expenses_page = paginator.page(page)
        except PageNotAnInteger:
            expenses_page = paginator.page(1)
        except EmptyPage:
            expenses_page = paginator.page(paginator.num_pages)

        data = []
        for expense in expenses_page:
            # Business logic for calculating total
            if expense.tax_type == 'flat':
                total = float(expense.amount) + float(expense.tax)
            elif expense.tax_type == 'percentage':
                total = float(expense.amount) + (float(expense.amount) * float(expense.tax) / 100)
            else:
                total = float(expense.amount)

            data.append({
                'id': expense.id,
                'name': expense.name,
                'amount': float(expense.amount),
                'tax': float(expense.tax),
                'tax_type': expense.tax_type,
                'transaction_type': expense.transaction_type,
                'total': round(total, 2),
                'source': expense.source,
                'date': expense.date.strftime('%Y-%m-%d'),
                'notes': expense.notes,
            })

        response = {
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': expenses_page.number,
            'results': data,
        }
        return JsonResponse(response, safe=False, status=200)



@csrf_exempt
def get_expense_view_by_Id(request):
    if request.method == 'GET':
        expense_id = request.GET.get('id')

        if not expense_id:
            return JsonResponse({'message': 'Income ID is required.'}, status=400)

        try:
            expense = Expense.objects.get(id=expense_id)

            # Calculate total based on tax_type
            if expense.tax_type == 'flat':
                total = float(expense.amount) + float(expense.tax)
            elif expense.tax_type == 'percentage':
                total = float(expense.amount) + (float(expense.amount) * float(expense.tax) / 100)
            else:
                total = float(expense.amount)

            data = {
                'id': expense.id,
                'name': expense.name,
                'amount': float(expense.amount),
                'tax': float(expense.tax),
                'tax_type': expense.tax_type,
                'transaction_type': expense.transaction_type,
                'total': round(total, 2),
                'source': expense.source,
                'date': expense.date.strftime('%Y-%m-%d'),
                'notes': expense.notes,
            }

            return JsonResponse(data, status=200)

        except Expense.DoesNotExist:
            return JsonResponse({'message': 'Income not found.'}, status=404)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def edit_expense_view(request):
    if request.method in ['PUT', 'POST']:
        data = {}

        if request.method == 'POST':
            data = request.POST
        else:
            content_type = request.content_type

            if content_type == 'application/json':
                data = json.loads(request.body)
            elif content_type == 'application/x-www-form-urlencoded':
                data = QueryDict(request.body.decode())
            else:
                return JsonResponse({'message': f'Unsupported Content-Type: {content_type}'}, status=415)

        income_id = data.get('id')
        name = data.get('name')
        amount = data.get('amount')
        source = data.get('source')
        date = data.get('date')
        notes = data.get('notes', '')
        tax = data.get('tax', 0)
        tax_type = data.get('tax_type', 'flat').lower()
        transaction_type = data.get('transaction_type')

        if not all([income_id, name, amount, source, date, transaction_type]):
            return JsonResponse({'message': 'Missing required fields'}, status=400)

        if transaction_type not in ['credit', 'debit']:
            return JsonResponse({'message': "transaction_type must be 'credit' or 'debit'"}, status=400)

        try:
            expense = Expense.objects.get(id=income_id)
            expense.name = name
            expense.amount = amount
            expense.source = source
            expense.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            expense.notes = notes
            expense.tax = tax
            expense.tax_type = tax_type
            expense.transaction_type = transaction_type
            expense.save()

            if expense.tax_type == 'flat':
                total = float(expense.amount) + float(expense.tax)
            elif expense.tax_type == 'percentage':
                total = float(expense.amount) + (float(expense.amount) * float(expense.tax) / 100)
            else:
                total = float(expense.amount)

            return JsonResponse({
                'message': 'Expense edited successfully',
                'expense': {
                    'id': expense.id,
                    'name': expense.name,
                    'amount': float(expense.amount),
                    'tax': float(expense.tax),
                    'tax_type': expense.tax_type,
                    'transaction_type': expense.transaction_type,
                    'total': round(total, 2),
                    'source': expense.source,
                    'date': expense.date.strftime('%Y-%m-%d'),
                    'notes': expense.notes,
                }
            }, status=200)

        except Expense.DoesNotExist:
            return JsonResponse({'message': 'Income not found'}, status=404)
        except Exception as e:
            return JsonResponse({'message': 'Error processing request', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_expense_view(request):
    if request.method in ['DELETE', 'POST']:
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
                income_id = body.get('id')
            else:
                income_id = request.POST.get('id')

            if not income_id:
                return JsonResponse({'message': 'Expense ID is required.'}, status=400)

            try:
                expense = Expense.objects.get(id=income_id)
                expense.delete()
                return JsonResponse({'message': 'Expense deleted successfully.'}, status=200)

            except Expense.DoesNotExist:
                return JsonResponse({'message': 'Expense not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'message': 'Error processing request.', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)
