from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_file
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
import os
from database import db, users_collection, members_collection, payments_collection, auctions_collection, sheets_collection, init_db
import pandas as pd
import json
import io

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    raise ValueError("SECRET_KEY environment variable is required")

# Initialize database
init_db()

# --- HELPER FUNCTIONS ---
def login_required(role=None):
    """Decorator to check if user is logged in"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login_page'))
            if role and session.get('role') != role:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return users_collection.find_one({'_id': ObjectId(session['user_id'])})
    return None

# --- AUTHENTICATION ROUTES ---
@app.route('/health')
def health_check():
    """Health check endpoint for Kubernetes/preview"""
    return jsonify({'status': 'healthy', 'service': 'chitfund'}), 200

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login_new.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = users_collection.find_one({'username': username})
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['role'] = user['role']
        session['name'] = user['name']
        
        if user['role'] == 'admin':
            return jsonify({'success': True, 'redirect': '/admin/dashboard'})
        else:
            return jsonify({'success': True, 'redirect': '/user/dashboard'})
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- ADMIN ROUTES ---
@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/members')
@login_required(role='admin')
def admin_members():
    return render_template('admin_members.html')

@app.route('/admin/auctions')
@login_required(role='admin')
def admin_auctions():
    return render_template('admin_auctions.html')

@app.route('/admin/reports')
@login_required(role='admin')
def admin_reports():
    return render_template('admin_reports.html')

@app.route('/admin/users')
@login_required(role='admin')
def admin_users():
    return render_template('admin_users.html')

# --- USER ROUTES ---
@app.route('/user/dashboard')
@login_required()
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/user/payments')
@login_required()
def user_payments():
    return render_template('user_payments.html')

@app.route('/user/history')
@login_required()
def user_history():
    return render_template('user_history.html')

# --- API ROUTES ---

# Dashboard Stats
@app.route('/api/admin/stats')
@login_required(role='admin')
def admin_stats():
    total_members = members_collection.count_documents({})
    total_users = users_collection.count_documents({'role': 'member'})
    
    # Calculate total value from latest sheet
    latest_sheet = sheets_collection.find_one(sort=[('created_at', -1)])
    sheet_name = latest_sheet['name'] if latest_sheet else None
    
    payments = list(payments_collection.find({'sheet_name': sheet_name}))
    total_value = sum(p.get('amount', 0) for p in payments)
    paid_value = sum(p.get('paid_amount', 0) for p in payments)
    pending_value = total_value - paid_value
    
    pending_members = len([p for p in payments if not p.get('is_paid', False)])
    
    # Recent activities
    recent_payments = list(payments_collection.find({'is_paid': True}).sort('paid_date', -1).limit(5))
    
    return jsonify({
        'total_members': total_members,
        'total_users': total_users,
        'total_value': total_value,
        'paid_value': paid_value,
        'pending_value': pending_value,
        'pending_members': pending_members,
        'recent_payments': [{
            'name': members_collection.find_one({'_id': p['member_id']})['name'],
            'amount': p.get('paid_amount', 0),
            'date': p.get('paid_date', '').strftime('%Y-%m-%d') if p.get('paid_date') else ''
        } for p in recent_payments]
    })

# Members API
@app.route('/api/admin/members')
@login_required(role='admin')
def get_all_members():
    sheet_name = request.args.get('sheet')
    
    # Get all members
    members = list(members_collection.find())
    
    result = []
    for member in members:
        # Get payment info for this member
        payment = payments_collection.find_one({
            'member_id': member['_id'],
            'sheet_name': sheet_name
        })
        
        member_data = {
            'id': str(member['_id']),
            'name': member['name'],
            'area': member['area'],
            'phone': member.get('phone', ''),
            'total': payment.get('amount', 0) if payment else 0,
            'paid_amount': payment.get('paid_amount', 0) if payment else 0,
            'is_paid': payment.get('is_paid', False) if payment else False,
            'paid_date': payment.get('paid_date', '').strftime('%Y-%m-%d') if payment and payment.get('paid_date') else None,
            'items': payment.get('items', []) if payment else []
        }
        result.append(member_data)
    
    return jsonify(result)

@app.route('/api/admin/members', methods=['POST'])
@login_required(role='admin')
def create_member():
    data = request.json
    
    # Create member
    member = {
        'name': data['name'],
        'area': data['area'],
        'phone': data.get('phone', ''),
        'created_at': datetime.utcnow()
    }
    
    result = members_collection.insert_one(member)
    
    # Create user account if requested
    if data.get('create_account'):
        hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'username': data['username'],
            'password': hashed_pw,
            'role': 'member',
            'name': data['name'],
            'member_id': result.inserted_id,
            'created_at': datetime.utcnow()
        })
    
    return jsonify({'success': True, 'id': str(result.inserted_id)})

@app.route('/api/admin/members/<member_id>', methods=['PUT'])
@login_required(role='admin')
def update_member(member_id):
    data = request.json
    
    members_collection.update_one(
        {'_id': ObjectId(member_id)},
        {'$set': {
            'name': data['name'],
            'area': data['area'],
            'phone': data.get('phone', ''),
            'updated_at': datetime.utcnow()
        }}
    )
    
    return jsonify({'success': True})

@app.route('/api/admin/members/<member_id>', methods=['DELETE'])
@login_required(role='admin')
def delete_member(member_id):
    members_collection.delete_one({'_id': ObjectId(member_id)})
    payments_collection.delete_many({'member_id': ObjectId(member_id)})
    users_collection.delete_one({'member_id': ObjectId(member_id)})
    
    return jsonify({'success': True})

# Payment API
@app.route('/api/admin/toggle-payment', methods=['POST'])
@login_required(role='admin')
def toggle_payment():
    data = request.json
    member_id = ObjectId(data['member_id'])
    sheet_name = data['sheet_name']
    item_id = data.get('item_id')
    
    payment = payments_collection.find_one({
        'member_id': member_id,
        'sheet_name': sheet_name
    })
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Toggle specific item if item_id provided
    if item_id:
        items = payment.get('items', [])
        for item in items:
            if item['id'] == item_id:
                item['is_paid'] = not item.get('is_paid', False)
                item['paid_date'] = datetime.utcnow() if item['is_paid'] else None
                break
        
        # Recalculate paid amount
        paid_amount = sum(item['amount'] for item in items if item.get('is_paid'))
        is_paid = paid_amount >= payment['amount']
        
        payments_collection.update_one(
            {'_id': payment['_id']},
            {'$set': {
                'items': items,
                'paid_amount': paid_amount,
                'is_paid': is_paid,
                'paid_date': datetime.utcnow() if is_paid else payment.get('paid_date')
            }}
        )
    else:
        # Toggle entire payment
        is_paid = not payment.get('is_paid', False)
        paid_amount = payment['amount'] if is_paid else 0
        
        payments_collection.update_one(
            {'_id': payment['_id']},
            {'$set': {
                'is_paid': is_paid,
                'paid_amount': paid_amount,
                'paid_date': datetime.utcnow() if is_paid else None
            }}
        )
    
    return jsonify({'success': True})

# Sheets API
@app.route('/api/sheets')
@login_required()
def get_sheets():
    sheets = list(sheets_collection.find().sort('created_at', -1))
    return jsonify([{'name': s['name'], 'date': s['created_at'].strftime('%Y-%m-%d')} for s in sheets])

@app.route('/api/sheets', methods=['POST'])
@login_required(role='admin')
def create_sheet():
    data = request.json
    
    sheet = {
        'name': data['name'],
        'created_at': datetime.utcnow()
    }
    
    sheets_collection.insert_one(sheet)
    
    return jsonify({'success': True})

# User Dashboard API
@app.route('/api/user/dashboard')
@login_required()
def user_dashboard_api():
    user = get_current_user()
    if not user or 'member_id' not in user:
        return jsonify({'error': 'Member not found'}), 404
    
    member = members_collection.find_one({'_id': user['member_id']})
    
    # Get latest payments
    latest_sheet = sheets_collection.find_one(sort=[('created_at', -1)])
    sheet_name = latest_sheet['name'] if latest_sheet else None
    
    payment = payments_collection.find_one({
        'member_id': user['member_id'],
        'sheet_name': sheet_name
    })
    
    return jsonify({
        'name': member['name'],
        'area': member['area'],
        'phone': member.get('phone', ''),
        'total_due': payment.get('amount', 0) if payment else 0,
        'paid_amount': payment.get('paid_amount', 0) if payment else 0,
        'pending_amount': (payment.get('amount', 0) - payment.get('paid_amount', 0)) if payment else 0,
        'is_paid': payment.get('is_paid', False) if payment else False,
        'items': payment.get('items', []) if payment else []
    })

@app.route('/api/user/payment-history')
@login_required()
def user_payment_history():
    user = get_current_user()
    if not user or 'member_id' not in user:
        return jsonify({'error': 'Member not found'}), 404
    
    payments = list(payments_collection.find({'member_id': user['member_id']}).sort('created_at', -1))
    
    history = []
    for payment in payments:
        history.append({
            'sheet_name': payment['sheet_name'],
            'amount': payment['amount'],
            'paid_amount': payment.get('paid_amount', 0),
            'is_paid': payment.get('is_paid', False),
            'paid_date': payment.get('paid_date', '').strftime('%Y-%m-%d') if payment.get('paid_date') else None
        })
    
    return jsonify(history)

# Auction API
@app.route('/api/admin/auctions')
@login_required(role='admin')
def get_auctions():
    auctions = list(auctions_collection.find().sort('date', -1).limit(20))
    
    result = []
    for auction in auctions:
        result.append({
            'id': str(auction['_id']),
            'date': auction['date'].strftime('%Y-%m-%d'),
            'month': auction.get('month', ''),
            'plan': auction.get('plan', 0),
            'bid_amount': auction.get('bid_amount', 0),
            'winner': auction.get('winner', '')
        })
    
    return jsonify(result)

@app.route('/api/admin/auctions', methods=['POST'])
@login_required(role='admin')
def create_auction():
    data = request.json
    
    auction = {
        'date': datetime.strptime(data['date'], '%Y-%m-%d'),
        'month': data['month'],
        'plan': data['plan'],
        'bid_amount': data['bid_amount'],
        'winner': data.get('winner', ''),
        'created_at': datetime.utcnow()
    }
    
    auctions_collection.insert_one(auction)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # This only runs locally
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
