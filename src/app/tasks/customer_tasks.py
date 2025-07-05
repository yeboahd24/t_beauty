"""
Customer-related background tasks.
"""
import csv
import os
from typing import Dict, Any
from celery import current_task
from src.app.core.celery_app import celery_app
from src.app.db.session import SessionLocal
from src.app.models.customer import Customer
from src.app.services.customer_service import CustomerService


@celery_app.task(bind=True)
def bulk_import_customers_task(self, csv_file_path: str) -> Dict[str, Any]:
    """
    Background task for bulk importing customers from CSV file.
    
    Args:
        csv_file_path: Path to the CSV file to process
        
    Returns:
        Dictionary with import results
    """
    db = SessionLocal()
    
    try:
        # Update task state to PROGRESS
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 0, 'status': 'Starting import...'}
        )
        
        if not os.path.exists(csv_file_path):
            return {
                "success": False,
                "message": f"CSV file not found: {csv_file_path}",
                "imported_count": 0,
                "errors": []
            }
        
        # First pass: count total rows
        total_rows = 0
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            total_rows = sum(1 for row in csv_reader)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_rows, 'status': f'Processing {total_rows} rows...'}
        )
        
        imported_count = 0
        errors = []
        skipped_count = 0
        
        # Second pass: process rows
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
                try:
                    # Update progress every 10 rows
                    if row_num % 10 == 0:
                        self.update_state(
                            state='PROGRESS',
                            meta={
                                'current': row_num - 1,
                                'total': total_rows,
                                'status': f'Processing row {row_num - 1} of {total_rows}...',
                                'imported': imported_count,
                                'skipped': skipped_count,
                                'errors': len(errors)
                            }
                        )
                    
                    # Extract and clean data from CSV
                    first_name = row.get('contact_first_name', '').strip()
                    last_name = row.get('contact_last_name', '').strip()
                    email = row.get('email', '').strip().lower() if row.get('email') else None
                    phone = row.get('phone', '').strip() if row.get('phone') else None
                    
                    # Skip rows with missing essential data
                    if not first_name and not last_name:
                        skipped_count += 1
                        continue
                    
                    # Handle cases where first_name might be empty but last_name has full name
                    if not first_name and last_name:
                        name_parts = last_name.split(' ', 1)
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                    
                    # Skip if email already exists
                    if email and CustomerService.get_by_email(db, email):
                        skipped_count += 1
                        continue
                    
                    # Build address from CSV fields
                    address_parts = []
                    if row.get('address_line_1'):
                        address_parts.append(row.get('address_line_1').strip())
                    if row.get('address_line_2'):
                        address_parts.append(row.get('address_line_2').strip())
                    
                    address_line1 = address_parts[0] if address_parts else None
                    address_line2 = address_parts[1] if len(address_parts) > 1 else None
                    
                    # Extract other fields
                    city = row.get('city', '').strip() if row.get('city') else None
                    state = row.get('province/state', '').strip() if row.get('province/state') else None
                    country = row.get('country', 'Trinidad and Tobago').strip() if row.get('country') else 'Trinidad and Tobago'
                    
                    # Create customer data
                    customer_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone': phone,
                        'address_line1': address_line1,
                        'address_line2': address_line2,
                        'city': city,
                        'state': state,
                        'country': country,
                        'is_active': True,
                        'is_vip': False,
                        'preferred_contact_method': 'phone' if phone else 'email'
                    }
                    
                    # Create customer
                    db_customer = Customer(**customer_data)
                    db.add(db_customer)
                    db.commit()
                    db.refresh(db_customer)
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    db.rollback()
                    continue
        
        # Final update
        self.update_state(
            state='SUCCESS',
            meta={
                'current': total_rows,
                'total': total_rows,
                'status': 'Import completed!',
                'imported': imported_count,
                'skipped': skipped_count,
                'errors': len(errors)
            }
        )
        
        # Clean up temporary file
        try:
            os.unlink(csv_file_path)
        except:
            pass  # Ignore cleanup errors
        
        return {
            "success": True,
            "message": f"Successfully imported {imported_count} customers",
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors
        }
        
    except Exception as e:
        # Clean up temporary file on error
        try:
            os.unlink(csv_file_path)
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'status': 'Import failed'}
        )
        
        return {
            "success": False,
            "message": f"Failed to process CSV file: {str(e)}",
            "imported_count": imported_count if 'imported_count' in locals() else 0,
            "errors": errors if 'errors' in locals() else []
        }
        
    finally:
        db.close()