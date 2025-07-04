from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Income
import datetime
import json

@csrf_exempt
def set_income_view(request):
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

            income = Income.objects.create(
                name=name,
                amount=amount,
                source=source,
                date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                notes=notes,
                tax=tax,
                tax_type=tax_type,
                transaction_type=transaction_type
            )

            if income.tax_type == 'flat':
                total = float(income.amount) + float(income.tax)
            elif income.tax_type == 'percentage':
                total = float(income.amount) + (float(income.amount) * float(income.tax) / 100)
            else:
                total = float(income.amount)

            return JsonResponse({
                'message': 'Income saved successfully',
                'income': {
                    'id': income.id,
                    'name': income.name,
                    'amount': float(income.amount),
                    'source': income.source,
                    'date': income.date.strftime('%Y-%m-%d'),
                    'notes': income.notes,
                    'tax': float(income.tax),
                    'tax_type': income.tax_type,
                    'transaction_type': income.transaction_type,
                    'total': round(total, 2),
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({'message': 'Error processing request', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_all_incomes_view(request):
    if request.method == 'GET':
        incomes = Income.objects.all().order_by('-date')

        # Get pagination parameters from query string
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        try:
            per_page = int(request.GET.get('per_page', 10))
        except ValueError:
            per_page = 10

        paginator = Paginator(incomes, per_page)

        try:
            incomes_page = paginator.page(page)
        except PageNotAnInteger:
            incomes_page = paginator.page(1)
        except EmptyPage:
            incomes_page = paginator.page(paginator.num_pages)

        data = []
        for income in incomes_page:
            # Business logic for calculating total
            if income.tax_type == 'flat':
                total = float(income.amount) + float(income.tax)
            elif income.tax_type == 'percentage':
                total = float(income.amount) + (float(income.amount) * float(income.tax) / 100)
            else:
                total = float(income.amount)

            data.append({
                'id': income.id,
                'name': income.name,
                'amount': float(income.amount),
                'tax': float(income.tax),
                'tax_type': income.tax_type,
                'transaction_type': income.transaction_type,
                'total': round(total, 2),
                'source': income.source,
                'date': income.date.strftime('%Y-%m-%d'),
                'notes': income.notes,
            })

        response = {
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': incomes_page.number,
            'results': data,
        }
        return JsonResponse(response, safe=False, status=200)



@csrf_exempt
def get_income_view_by_Id(request):
    if request.method == 'GET':
        income_id = request.GET.get('id')

        if not income_id:
            return JsonResponse({'message': 'Income ID is required.'}, status=400)

        try:
            income = Income.objects.get(id=income_id)

            # Calculate total based on tax_type
            if income.tax_type == 'flat':
                total = float(income.amount) + float(income.tax)
            elif income.tax_type == 'percentage':
                total = float(income.amount) + (float(income.amount) * float(income.tax) / 100)
            else:
                total = float(income.amount)

            data = {
                'id': income.id,
                'name': income.name,
                'amount': float(income.amount),
                'tax': float(income.tax),
                'tax_type': income.tax_type,
                'transaction_type': income.transaction_type,
                'total': round(total, 2),
                'source': income.source,
                'date': income.date.strftime('%Y-%m-%d'),
                'notes': income.notes,
            }

            return JsonResponse(data, status=200)

        except Income.DoesNotExist:
            return JsonResponse({'message': 'Income not found.'}, status=404)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def edit_income_view(request):
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
            income = Income.objects.get(id=income_id)
            income.name = name
            income.amount = amount
            income.source = source
            income.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            income.notes = notes
            income.tax = tax
            income.tax_type = tax_type
            income.transaction_type = transaction_type
            income.save()

            if income.tax_type == 'flat':
                total = float(income.amount) + float(income.tax)
            elif income.tax_type == 'percentage':
                total = float(income.amount) + (float(income.amount) * float(income.tax) / 100)
            else:
                total = float(income.amount)

            return JsonResponse({
                'message': 'Income edited successfully',
                'income': {
                    'id': income.id,
                    'name': income.name,
                    'amount': float(income.amount),
                    'tax': float(income.tax),
                    'tax_type': income.tax_type,
                    'transaction_type': income.transaction_type,
                    'total': round(total, 2),
                    'source': income.source,
                    'date': income.date.strftime('%Y-%m-%d'),
                    'notes': income.notes,
                }
            }, status=200)

        except Income.DoesNotExist:
            return JsonResponse({'message': 'Income not found'}, status=404)
        except Exception as e:
            return JsonResponse({'message': 'Error processing request', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_income_view(request):
    if request.method in ['DELETE', 'POST']:
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
                income_id = body.get('id')
            else:
                income_id = request.POST.get('id')

            if not income_id:
                return JsonResponse({'message': 'Income ID is required.'}, status=400)

            try:
                income = Income.objects.get(id=income_id)
                income.delete()
                return JsonResponse({'message': 'Income deleted successfully.'}, status=200)

            except Income.DoesNotExist:
                return JsonResponse({'message': 'Income not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'message': 'Error processing request.', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)
