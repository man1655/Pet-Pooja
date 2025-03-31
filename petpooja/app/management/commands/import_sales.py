# management/commands/import_sales.py
from django.core.management.base import BaseCommand
import csv
from datetime import datetime
from app.models import Sale

class Command(BaseCommand):
    help = "Import sales data from CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_path']
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            sales = []
            
            for row in reader:
                # Parse date (keep time as raw string)
                sale_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                
                sales.append(Sale(
                    order_id=row['order_id'],
                    date=sale_date,
                    item_name=row['item_name'],
                    item_type=row['item_type'],
                    item_price=float(row['item_price']),
                    quantity=int(row['quantity']),
                    transaction_amount=float(row['transaction_amount']),
                    transaction_type=row['transaction_type'],
                    received_by=row['received_by'],
                    time_of_sale=row['time_of_sale'],  # Direct string value
                    ingredients=row['Ingredients']
                ))
                
            Sale.objects.bulk_create(sales)
            self.stdout.write(self.style.SUCCESS(f'Imported {len(sales)} records'))