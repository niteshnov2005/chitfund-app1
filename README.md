# Chit Fund Management System

A modern, full-featured web application for managing chit fund operations with MongoDB database, user authentication, and beautiful UI design.

## 🌟 Features

### Admin Interface
- **Dashboard**: Real-time statistics and insights
  - Total members count
  - Total fund value
  - Pending payments tracking
  - Recent payment activities
  
- **Member Management**: 
  - Add, edit, and delete members
  - Track member payments
  - Mark payments as paid/unpaid
  - Search and filter members
  - View payment breakdown by items
  
- **Auction Management**:
  - Create and track auctions
  - Record bid amounts and winners
  - View auction history
  
- **Reports**:
  - Payment summaries
  - Analytics and insights
  
- **User Account Management**:
  - Create login accounts for members
  - Manage user credentials

### User/Member Interface
- **Personal Dashboard**:
  - View own payment status
  - Total due, paid, and pending amounts
  - Payment breakdown by month/plan
  
- **Payment Details**:
  - Detailed view of all payment items
  - Payment status tracking
  
- **Payment History**:
  - Complete history across all months
  - Track past payments

## 🎨 Design Features

- **Modern UI**: Clean, professional design with gradient colors
- **Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use sidebar and navigation
- **Real-time Updates**: Live data refresh
- **Beautiful Forms**: User-friendly input forms with validation
- **Status Badges**: Visual indicators for payment status
- **Smooth Animations**: Hover effects and transitions

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Authentication**: bcrypt password hashing
- **Icons**: Font Awesome 6
- **Data Migration**: Automated Excel to MongoDB migration

## 📦 Installation

### Prerequisites
- Python 3.11+
- MongoDB
- pip (Python package manager)

### Setup

1. **Install Dependencies**:
```bash
cd /app
pip install -r requirements.txt
```

2. **Configure Environment**:
Edit `/app/.env` file:
```
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=chitfund_db
SECRET_KEY=your_secret_key_here
```

3. **Migrate Existing Data** (Optional):
If you have existing Excel data:
```bash
python migrate_data.py
```

4. **Start Application**:
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 👤 Default Credentials

### Admin Account
- Username: `admin`
- Password: `nitesh2025`

### Test Member Accounts (created during migration)
- Username: `sohanji` / Password: `member123`
- Username: `jivaramji` / Password: `member123`
- Username: `mangilalji` / Password: `member123`

## 📊 Database Schema

### Collections

1. **users**: User authentication and roles
   - username, password (hashed), role, name, member_id, created_at

2. **members**: Member information
   - name, area, phone, created_at

3. **payments**: Payment records
   - member_id, sheet_name, amount, paid_amount, is_paid, paid_date, items, created_at

4. **auctions**: Auction history
   - date, month, plan, bid_amount, winner, created_at

5. **sheets**: Monthly sheets/periods
   - name, created_at

## 🔐 Security Features

- Password hashing using bcrypt
- Session-based authentication
- Role-based access control (Admin/Member)
- Protected API endpoints
- CSRF protection

## 📱 User Workflows

### Admin Workflow
1. Login with admin credentials
2. View dashboard statistics
3. Manage members (add/edit/delete)
4. Track payments and mark as paid
5. Run monthly auctions
6. Generate reports
7. Create user accounts for members

### Member Workflow
1. Login with member credentials
2. View personal dashboard
3. Check payment status
4. View detailed payment breakdown
5. Access payment history
6. Track due amounts

## 🎯 Key Improvements Over Old System

1. **Database Migration**: Excel → MongoDB (proper database)
2. **Modern UI**: Beautiful, responsive design
3. **User Interface**: Members can now access their own data
4. **Better Security**: Hashed passwords, session management
5. **Real-time Stats**: Live dashboard updates
6. **Mobile Friendly**: Works on all devices
7. **Scalable**: MongoDB can handle large amounts of data
8. **Search & Filter**: Easy to find members and data
9. **Audit Trail**: Track payment dates and history
10. **Professional Look**: Gradient colors, smooth animations

## 📝 API Endpoints

### Authentication
- `POST /api/login`: User login
- `GET /logout`: User logout

### Admin APIs
- `GET /api/admin/stats`: Dashboard statistics
- `GET /api/admin/members`: Get all members
- `POST /api/admin/members`: Create new member
- `PUT /api/admin/members/<id>`: Update member
- `DELETE /api/admin/members/<id>`: Delete member
- `POST /api/admin/toggle-payment`: Toggle payment status
- `GET /api/admin/auctions`: Get auction history
- `POST /api/admin/auctions`: Create new auction

### User APIs
- `GET /api/user/dashboard`: User dashboard data
- `GET /api/user/payment-history`: Payment history

### Common APIs
- `GET /api/sheets`: Get all sheets/periods

## 🚀 Production Deployment

### Using Supervisor
The application is configured to run with Supervisor for automatic restarts:

```bash
sudo supervisorctl restart chitfund_app
sudo supervisorctl status chitfund_app
```

### Logs
- Application logs: `/var/log/supervisor/chitfund_app.out.log`
- Error logs: `/var/log/supervisor/chitfund_app.err.log`

## 🔧 Maintenance

### Backup Database
```bash
mongodump --db chitfund_db --out /backup/chitfund_$(date +%Y%m%d)
```

### Restore Database
```bash
mongorestore --db chitfund_db /backup/chitfund_20250125
```

## 📞 Support

For issues or questions, refer to:
- Database: Check MongoDB connection
- Authentication: Verify user credentials in database
- Payments: Check payments collection
- UI Issues: Clear browser cache

## 🎉 Credits

Built with modern web technologies for efficient chit fund management.

---

**Version**: 2.0  
**Last Updated**: January 2025
