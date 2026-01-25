"""
Data Migration Script: Excel to MongoDB
Migrates existing chit fund data from Excel file to MongoDB database
"""
import os
import sys
import pandas as pd
import openpyxl
from datetime import datetime
from database import db, members_collection, payments_collection, sheets_collection, init_db
import json

def clean_num(val):
    """Clean numeric values from Excel"""
    try:
        return float(str(val).replace(',', '').replace('₹', '').strip())
    except:
        return 0.0

def normalize_text(text):
    """Normalize text for comparison"""
    if not text:
        return ""
    return str(text).lower().replace('.', '').replace(' ', '').replace(':', '').strip()

def migrate_from_excel(excel_file='sample_gemini.xlsx', payment_records_file='payment_records.json'):
    """
    Migrate data from Excel file and payment records JSON to MongoDB
    """
    print("Starting data migration...")
    
    # Initialize database
    init_db()
    print("Database initialized")
    
    # Check if Excel file exists
    if not os.path.exists(excel_file):
        print(f"Excel file {excel_file} not found!")
        return False
    
    try:
        # Load workbook to get all sheets
        wb = openpyxl.load_workbook(excel_file, read_only=True)
        sheet_names = wb.sheetnames
        wb.close()
        
        print(f"Found {len(sheet_names)} sheets: {sheet_names}")
        
        # Load payment records
        paid_db = {}
        if os.path.exists(payment_records_file):
            with open(payment_records_file, 'r') as f:
                paid_db = json.load(f)
            print(f"Loaded {len(paid_db)} payment records")
        
        # Track unique members across all sheets
        members_map = {}  # key: normalized_name_area, value: member_id
        
        # Process each sheet
        for sheet_idx, sheet_name in enumerate(sheet_names):
            print(f"\nProcessing sheet: {sheet_name}")
            
            # Create sheet record
            sheet_record = {
                'name': sheet_name,
                'created_at': datetime.utcnow()
            }
            sheet_result = sheets_collection.insert_one(sheet_record)
            print(f"Created sheet record: {sheet_name}")
            
            # Read Excel data
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, engine='openpyxl')
            
            # Parse members and their payments from this sheet
            ledger_configs = [
                {'label_col': 0, 'data_col': 1, 'comm_col': 2, 'amt_col': 3},
                {'label_col': 5, 'data_col': 6, 'comm_col': 7, 'amt_col': 8}
            ]
            
            for config in ledger_configs:
                curr_member = None
                curr_member_id = None
                
                for r in range(df.shape[0]):
                    try:
                        cell_label = str(df.iloc[r, config['label_col']]).strip().upper()
                        
                        # Detect Member Header
                        if cell_label == 'NAME':
                            raw_name = str(df.iloc[r, config['data_col']]).strip().title()
                            if not raw_name or raw_name.upper() in ['NAN', 'NONE', '']:
                                continue
                            
                            raw_area = str(df.iloc[r, config['comm_col']]).strip().title()
                            if not raw_area or raw_area.upper() in ['NAN', 'NONE', '']:
                                raw_area = "General"
                            
                            norm_key = f"{normalize_text(raw_name)}_{normalize_text(raw_area)}"
                            
                            # Check if member already exists
                            if norm_key in members_map:
                                curr_member_id = members_map[norm_key]
                                print(f"  Found existing member: {raw_name}")
                            else:
                                # Create new member
                                member_doc = {
                                    'name': raw_name,
                                    'area': raw_area,
                                    'phone': '',
                                    'created_at': datetime.utcnow()
                                }
                                result = members_collection.insert_one(member_doc)
                                curr_member_id = result.inserted_id
                                members_map[norm_key] = curr_member_id
                                print(f"  Created new member: {raw_name} in {raw_area}")
                            
                            # Initialize payment record for this member in this sheet
                            curr_member = {
                                'member_id': curr_member_id,
                                'name': raw_name,
                                'items': [],
                                'total': 0
                            }
                        
                        # Detect Individual Plan Rows
                        elif curr_member and cell_label.replace('.','',1).isdigit():
                            month_label = str(df.iloc[r, config['label_col']]).strip()
                            plan_val = str(df.iloc[r, config['data_col']]).strip()
                            comm_val = str(df.iloc[r, config['comm_col']]).strip()
                            amt = clean_num(df.iloc[r, config['amt_col']])
                            
                            if amt > 0:
                                # Generate Item ID
                                item_id = f"{normalize_text(curr_member['name'])}_{int(amt)}_{month_label}_{plan_val}".replace(" ", "").replace(".", "")
                                
                                # Check payment status from old system
                                db_entry = paid_db.get(item_id)
                                item_is_paid = False
                                item_paid_date = None
                                if db_entry:
                                    item_is_paid = True
                                    if isinstance(db_entry, str):
                                        try:
                                            item_paid_date = datetime.strptime(db_entry, "%d %b, %I:%M %p")
                                        except:
                                            item_paid_date = datetime.utcnow()
                                
                                curr_member['items'].append({
                                    'month': month_label,
                                    'plan': plan_val,
                                    'commission': comm_val,
                                    'amount': amt,
                                    'id': item_id,
                                    'is_paid': item_is_paid,
                                    'paid_date': item_paid_date
                                })
                                
                                curr_member['total'] += amt
                        
                        # Reset member at block end
                        elif 'TOTAL' in cell_label and curr_member:
                            # Save payment record for this member
                            if curr_member['items']:
                                paid_amount = sum(item['amount'] for item in curr_member['items'] if item['is_paid'])
                                is_paid = paid_amount >= curr_member['total']
                                
                                # Find the latest paid date
                                paid_date = None
                                for item in curr_member['items']:
                                    if item['is_paid'] and item['paid_date']:
                                        if not paid_date or item['paid_date'] > paid_date:
                                            paid_date = item['paid_date']
                                
                                payment_doc = {
                                    'member_id': curr_member['member_id'],
                                    'sheet_name': sheet_name,
                                    'amount': curr_member['total'],
                                    'paid_amount': paid_amount,
                                    'is_paid': is_paid,
                                    'paid_date': paid_date,
                                    'items': curr_member['items'],
                                    'created_at': datetime.utcnow()
                                }
                                payments_collection.insert_one(payment_doc)
                                print(f"    Saved payment record for {curr_member['name']}: ₹{curr_member['total']}")
                            
                            curr_member = None
                            curr_member_id = None
                    
                    except Exception as e:
                        # print(f"    Error processing row {r}: {e}")
                        pass
        
        print(f"\n✅ Migration completed successfully!")
        print(f"Total members: {members_collection.count_documents({})}")
        print(f"Total payment records: {payments_collection.count_documents({})}")
        print(f"Total sheets: {sheets_collection.count_documents({})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Run migration
    success = migrate_from_excel()
    
    if success:
        print("\n🎉 Data migration completed! You can now use the new application.")
        sys.exit(0)
    else:
        print("\n❌ Data migration failed. Please check the errors above.")
        sys.exit(1)
