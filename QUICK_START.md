# 🚀 Quick Start Guide - Chit Fund Management System

## For Administrators

### 1. Login
- Navigate to application URL
- Click "Admin" button
- Enter credentials:
  - Username: `admin`
  - Password: `nitesh2025`

### 2. Dashboard
- View total members, total value, pending amounts
- See recent payment activities
- Quick action buttons for common tasks

### 3. Managing Members
- Click "Members" in sidebar
- **Add Member**:
  1. Click "Add Member" button
  2. Fill in Name, Area, Phone
  3. Optional: Check "Create user account" to give them login access
  4. Save
  
- **Mark Payment**:
  - Find member in list
  - Click "Mark Paid" button
  - Payment automatically tracked with date/time

### 4. Running Auctions
- Click "Auctions" in sidebar
- Fill in auction details:
  - Date
  - Month
  - Plan amount
  - Bid amount
  - Winner name (optional)
- Click "Create Auction"

### 5. Managing User Accounts
- When adding/editing members, check "Create user account"
- Members can then login with their credentials
- They will see only their own payment information

## For Members/Users

### 1. Login
- Click "Member" button on login page
- Enter your username and password
- (Default test accounts: sohanji / member123)

### 2. Dashboard
- View your payment summary:
  - Total due amount
  - Amount paid
  - Pending amount
  - Payment status
- See detailed breakdown of all payment items

### 3. View Payment Details
- Click any payment item to see details
- View payment status (Paid/Pending)
- Check payment dates

### 4. Payment History
- Access complete payment history
- View all past months
- Track your payment progress

## Common Tasks

### Search Members (Admin)
- Use search bar at top of Members page
- Search by name or area
- Results filter in real-time

### Filter by Month (Admin)
- Use dropdown to select specific month/sheet
- View payments for that period only

### Check Statistics (Admin)
- Dashboard shows live statistics
- Auto-refreshes every 30 seconds
- Click refresh manually if needed

## Tips & Tricks

1. **Mobile Access**: The system works great on phones - use it on the go!

2. **Quick Payment Marking**: In Members page, quickly mark multiple payments without leaving the page

3. **Search Power**: Use partial names in search (e.g., "Sohan" will find "Sohanji")

4. **Dashboard Widgets**: Hover over stats cards for more details

5. **Logout**: Always logout when done for security

## Troubleshooting

### Can't Login?
- Check username and password are correct
- Admin: username is `admin`
- Members: username is usually lowercase name without spaces

### Not Seeing Data?
- Make sure correct month/sheet is selected
- Click refresh or reload page
- Check with admin if you're a member

### Payment Not Updating?
- Admin: Click the toggle button again
- Refresh the page
- Check internet connection

## Getting Help

**For Administrators:**
- Check logs: `/var/log/supervisor/chitfund_app.err.log`
- Restart service: `sudo supervisorctl restart chitfund_app`
- Check database: Verify MongoDB is running

**For Members:**
- Contact your administrator
- Verify your account was created
- Try password reset (contact admin)

## Security Reminders

✅ **DO:**
- Logout after each session
- Use strong passwords
- Keep credentials confidential
- Report suspicious activity

❌ **DON'T:**
- Share your login credentials
- Leave browser open on shared computers
- Use simple passwords
- Access from untrusted devices

---

**Need More Help?** Contact your system administrator.
