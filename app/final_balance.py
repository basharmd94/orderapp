
# Updated SQLAlchemy models to fix deprecation warnings
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, MetaData, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker  # Import from orm instead of ext.declarative
from sqlalchemy import create_engine, func,  or_, and_, extract
from sqlalchemy.orm import aliased
from datetime import date, datetime, timedelta







zid = 100005
proj = 'Zepto Chemicals'
customer_id = 'CUS-000002'
# Set till_date to today's date in YYYY-MM-DD format
today = date.today()
till_date = today.strftime('%Y-%m-%d')

# Create base class for declarative models using the updated import path
Base = declarative_base()  # This now comes from sqlalchemy.orm

# The rest of your models remain the same
class Customer(Base):
    __tablename__ = 'cacus'
    
    xcus = Column(String, primary_key=True)
    zid = Column(Integer, primary_key=True)
    xshort = Column(String)
    xstate = Column(String)
    xtaxnum = Column(String)

class GLHeader(Base):
    __tablename__ = 'glheader'
    
    xvoucher = Column(String, primary_key=True)
    zid = Column(Integer, primary_key=True)
    xdate = Column(Date)

class GLDetail(Base):
    __tablename__ = 'gldetail'
    
    xvoucher = Column(String, primary_key=True)
    zid = Column(Integer, primary_key=True)
    xsub = Column(String, primary_key=True)
    xproj = Column(String)
    xprime = Column(Float)

# Create engine and session maker
engine = create_engine('postgresql://postgres:postgres@69.162.102.58:5432/da')
Session = sessionmaker(bind=engine)


def get_payment_sqlalchemy_filtered(zid, customer_id, start_date=None, end_date=None):
    """
    Get payment data using SQLAlchemy ORM with enhanced filtering options.
    
    Args:
        zid (int): The zone ID to filter by
        customer_id (str): Specific customer ID to filter by
        start_date (str or datetime.date, optional): Start date for filtering (format: 'YYYY-MM-DD')
        end_date (str or datetime.date, optional): End date for filtering (format: 'YYYY-MM-DD')
        
    Returns:
        list: List of dictionaries containing payment information
    """
    # Create a new session
    session = Session()
    
    try:
        # Handle date parameters
        if start_date is None:
            # Get first day of current month
            today = date.today()
            start_date = date(today.year, today.month, 1)
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
        if end_date is None:
            # Use current date if not specified
            end_date = date.today()
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Create aliases for tables
        h = aliased(GLHeader)  # alias for glheader
        g = aliased(GLDetail)  # alias for gldetail
        
        # Build the query with SQLAlchemy
        query = session.query(
            h.xdate.label('last_pay_date'),
            g.xsub.label('xcus'),
            g.xprime.label('last_rec_amt'),
            h.xvoucher.label('xvoucher')  # Include voucher number
        ).select_from(h).join(
            g, and_(h.xvoucher == g.xvoucher, h.zid == g.zid)
        ).filter(
            h.zid == zid,
            g.zid == zid,
            g.xsub == customer_id,  # Filter by specific customer ID
            h.xdate.between(start_date, end_date),  # Date range filter
            or_(
                h.xvoucher.like('%RCT-%'),
                h.xvoucher.like('JV--%'),
                h.xvoucher.like('RCT-%'),
                h.xvoucher.like('CRCT%'),
                h.xvoucher.like('STJV%'),
                h.xvoucher.like('BRCT%')
            )
        ).order_by(g.xsub, h.xdate)
        
        # Execute the query and get results
        results = query.all()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            data.append({
                'last_pay_date': row.last_pay_date,
                'xcus': row.xcus,
                'last_rec_amt': float(row.last_rec_amt) if row.last_rec_amt is not None else 0.0,
                'xvoucher': row.xvoucher  # Add voucher number to the result
            })
        
        return data
        
    finally:
        # Close the session
        session.close()



def get_orders_sqlalchemy(zid, customer_id, start_date=None, end_date=None):
    """
    Get customer order data using SQLAlchemy ORM with filtering options.
    Orders are identified by vouchers containing 'INOP'.
    
    Args:
        zid (int): The zone ID to filter by
        customer_id (str): Specific customer ID to filter by
        start_date (str or datetime.date, optional): Start date for filtering (format: 'YYYY-MM-DD')
        end_date (str or datetime.date, optional): End date for filtering (format: 'YYYY-MM-DD')
        
    Returns:
        list: List of dictionaries containing order information
    """
    # Create a new session
    session = Session()
    
    try:
        # Handle date parameters
        if start_date is None:
            # Get first day of current month
            today = date.today()
            start_date = date(today.year, today.month, 1)
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
        if end_date is None:
            # Use current date if not specified
            end_date = date.today()
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Create aliases for tables
        h = aliased(GLHeader)  # alias for glheader
        g = aliased(GLDetail)  # alias for gldetail
        
        # Build the query with SQLAlchemy - filter for INOP vouchers (orders)
        query = session.query(
            h.xdate.label('last_order_date'),
            g.xsub.label('xcus'),
            g.xprime.label('last_order_amt'),
            h.xvoucher.label('xvoucher')  # Include voucher number
        ).select_from(h).join(
            g, and_(h.xvoucher == g.xvoucher, h.zid == h.zid)
        ).filter(
            h.zid == zid,
            g.zid == zid,
            g.xsub == customer_id,  # Filter by specific customer ID
            h.xdate.between(start_date, end_date),  # Date range filter
            h.xvoucher.like('%INOP%')  # Filter for orders
        ).order_by(g.xsub, h.xdate)
        
        # Execute the query and get results
        results = query.all()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            data.append({
                'last_order_date': row.last_order_date,
                'xcus': row.xcus,
                'last_order_amt': float(row.last_order_amt) if row.last_order_amt is not None else 0.0,
                'xvoucher': row.xvoucher  # Add voucher number to the result
            })
        
        return data
        
    finally:
        # Close the session
        session.close()


def get_customer_ledger(zid, customer_id, start_date=None, end_date=None):
    """
    Create a complete customer ledger with both payments and orders.
    
    Args:
        zid (int): The zone ID to filter by
        customer_id (str): Specific customer ID to filter by
        start_date (str or datetime.date, optional): Start date for filtering (format: 'YYYY-MM-DD')
        end_date (str or datetime.date, optional): End date for filtering (format: 'YYYY-MM-DD')
        
    Returns:
        list: List of dictionaries containing combined ledger entries with type indicator
    """
    # Get payment data
    payments = get_payment_sqlalchemy_filtered(
        zid=zid,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get order data
    orders = get_orders_sqlalchemy(
        zid=zid,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Add entry type indicators to each record
    for payment in payments:
        payment['entry_type'] = 'PAYMENT'
        payment['transaction_date'] = payment['last_pay_date']
        payment['amount'] = payment['last_rec_amt']
        payment['xvoucher'] = payment.get('xvoucher', None)  # Add voucher number if available
        
    for order in orders:
        order['entry_type'] = 'ORDER'
        order['transaction_date'] = order['last_order_date']
        order['amount'] = order['last_order_amt']
        order['xvoucher'] = order['xvoucher']  # Include voucher number
    
    # Combine the records
    ledger = payments + orders
    
    # Sort by date
    ledger.sort(key=lambda x: x['transaction_date'])
    
    return ledger

def get_closing_balance(zid, customer_id, proj, closing_date):
    """
    Calculate the closing balance for a customer up to a specific date.
    This will be used as the opening balance for the ledger.
    
    Args:
        zid (int): The zone ID
        customer_id (str): The customer ID
        proj (str): The project
        closing_date (str or datetime.date): The date up to which to calculate the balance
        
    Returns:
        float: The closing balance
    """
    # Create session
    session = Session()
    
    try:
        # Convert string date to datetime.date if needed
        if isinstance(closing_date, str):
            closing_date = datetime.strptime(closing_date, '%Y-%m-%d').date()
        
        # Create aliases for tables
        g = aliased(GLDetail)  # alias for gldetail
        h = aliased(GLHeader)  # alias for glheader
        
        # Query to get the sum of all transactions up to the closing date
        query = session.query(
            func.sum(g.xprime).label('closing_balance')
        ).select_from(g).join(
            h, and_(g.xvoucher == h.xvoucher, g.zid == h.zid)
        ).filter(
            h.zid == zid,
            g.zid == zid,
            g.xsub == customer_id,
            g.xproj == proj,
            ~g.xvoucher.like('%OB%'),  # Exclude opening balance transactions
            h.xdate < closing_date     # All transactions before the start date
        )
        
        # Execute query and get result
        result = query.scalar()
        
        # Return the closing balance or 0 if None
        return float(result) if result is not None else 0.0
        
    finally:
        # Close session
        session.close()

def get_enhanced_customer_ledger(zid, customer_id, proj, start_date=None, end_date=None):
    """
    Create a complete customer ledger with opening balance and transactions in the date range.
    
    Args:
        zid (int): The zone ID
        customer_id (str): The customer ID
        proj (str): The project
        start_date (str or datetime.date): Start date for the ledger
        end_date (str or datetime.date): End date for the ledger
        
    Returns:
        tuple: (opening_balance, ledger_entries)
    """
    # Handle date parameters
    if start_date is None:
        start_date = date.today().replace(day=1)  # First day of current month
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
    if end_date is None:
        end_date = date.today()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get the closing balance up to the start date (will be our opening balance)
    opening_balance = get_closing_balance(zid, customer_id, proj, start_date)
    
    # Get ledger entries within the date range
    ledger_entries = get_customer_ledger(
        zid=zid,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return opening_balance, ledger_entries

# Set the date range for the ledger
formatted_start_date = '2023-01-01'
formatted_end_date = '2025-04-22'

print(f"Creating enhanced customer ledger for customer {customer_id}")
print(f"Date range: {formatted_start_date} to {formatted_end_date}")

# Get the enhanced ledger with opening balance
opening_balance, enhanced_ledger = get_enhanced_customer_ledger(
    zid=zid,
    customer_id=customer_id,
    proj=proj,
    start_date=formatted_start_date,
    end_date=formatted_end_date
)

# Display the results
print(f"\nRetrieved {len(enhanced_ledger)} ledger entries")
print(f"Opening Balance as of {formatted_start_date}: {opening_balance:,.2f}")

if enhanced_ledger:
    # Start with the opening balance
    running_balance = opening_balance
    
    # Create a header for the ledger
    print("\nCustomer Ledger:")
    print(f"{'Date':<12} {'Type':<8} {'Amount':>12} {'Voucher':<15} {'Running Balance':>16}")
    print("-" * 65)
    
    # Add an opening balance entry for better clarity
    print(f"{formatted_start_date:<12} {'OPENING':<8} {0:>12,.2f} {'N/A':<15} {running_balance:>16,.2f}")
    
    # Display all transactions with running balance
    for entry in enhanced_ledger:
        running_balance += entry['amount']
        xvoucher = entry.get('xvoucher', 'N/A') or 'N/A'  # Ensure xvoucher is a string
        print(f"{entry['transaction_date'].strftime('%Y-%m-%d'):<12} "
              f"{entry['entry_type']:<8} "
              f"{entry['amount']:>12,.2f} "
              f"{xvoucher:<15} "
              f"{running_balance:>16,.2f}")
        
    print("-" * 65)
    print(f"Final Balance as of {formatted_end_date}: {running_balance:,.2f}")
else:
    print(f"No ledger entries found for customer {customer_id} in the specified date range")
    print(f"Final Balance as of {formatted_end_date}: {opening_balance:,.2f}")
