#pylint: disable=E1101
from sqlalchemy import *
from sqlalchemy import func,update
from sqlalchemy.orm import sessionmaker
import Alerts

user = 'root'
password = '1234'
host = 'localhost'
schema = 'classicmodels'

engine = create_engine('mysql+pymysql://'+user +':' +password +'@'+host+'/'+schema, 
                        echo = True)
meta = MetaData()
Session = sessionmaker(bind=engine)
session = Session()


orders = Table(
   'orders', meta, 
   Column('orderNumber', Integer, primary_key = True), 
   Column('customerNumber', Integer),
   Column('requiredDate', Date),
   Column('orderDate', Date),
   Column('status', String),
   Column('comments', String)
)

customers = Table(
   'customers', meta, 
   Column('customerNumber', Integer, primary_key = True), 
   Column('customerName', String)
)

orderDetails = Table(
   'orderdetails', meta,
   Column('orderNumber', Integer, primary_key = True),
   Column('productCode', String, primary_key = True),
   Column('quantityOrdered', Integer),
   Column('priceEach', DECIMAL),
   Column('orderLineNumber', Integer)
)

dashboardEntries = Table(
   'python_dashboardcounters', meta,
   Column('counterType', String, primary_key = True),
   Column('counter', Integer)
)

"""--------------------------------------------------------------------"""
# Sub Queries

sq_l_Order_Orderdetails = session.query(
   # Orders
   orders.c.orderNumber,
   orders.c.customerNumber,
   orders.c.requiredDate,
   orders.c.orderDate,
   orders.c.status,
   orders.c.comments,
   # Order Details
   orderDetails.c.productCode,
   orderDetails.c.quantityOrdered,
   orderDetails.c.priceEach,
   orderDetails.c.orderLineNumber,
   # Calculated
   (orderDetails.c.priceEach * orderDetails.c.quantityOrdered).label('totalAmount'),
   func.substr(orders.c.orderDate, 6, 2).label('orderDate_Month'),
   func.substr(orders.c.orderDate, 1, 4).label('orderDate_Year'),
   func.date(
      func.substr(orders.c.orderDate, 1, 4) + "-" +
      func.substr(orders.c.orderDate, 6, 2) + "-01"
      ).label("orderDate_Monthyear")
   ).join(
   orderDetails
   , orders.c.orderNumber == orderDetails.c.orderNumber 
   , isouter=True
).subquery()

sq_MonthlySelledProducts = session.query(
   sq_l_Order_Orderdetails.c.productCode,
   sq_l_Order_Orderdetails.c.orderDate_Monthyear,
   func.sum(sq_l_Order_Orderdetails.c.totalAmount).label('monthlyAmount')
).group_by(
   sq_l_Order_Orderdetails.c.productCode,
   sq_l_Order_Orderdetails.c.orderDate_Monthyear  
).subquery()

sq_MostSelledProducts = session.query(
   sq_MonthlySelledProducts.c.productCode,
   func.sum(sq_MonthlySelledProducts.c.monthlyAmount).label('totalProductAmount')
).group_by(
   sq_MonthlySelledProducts.c.productCode
).order_by(
   func.sum(sq_MonthlySelledProducts.c.monthlyAmount).desc()
).limit(5).subquery()

mostSelledProducts = []
for product in session.query(sq_MostSelledProducts.c.productCode).distinct():
   mostSelledProducts.append(product[0])


sq_StatusCountFromOrders = session.query(
   orders.c.status,
   func.count(distinct(orders.c.orderNumber)).label('ordersCount')
).group_by(
   orders.c.status
).filter(
   or_(orders.c.status == 'In Process', orders.c.status =='On Hold')
).subquery()

sq_StatusAmountFromOrderDetails = session.query(
   sq_l_Order_Orderdetails.c.status,
   func.sum(sq_l_Order_Orderdetails.c.totalAmount).label('monthlyAmount')
).group_by(
   sq_l_Order_Orderdetails.c.status
).filter(
   or_(sq_l_Order_Orderdetails.c.status == 'In Process', sq_l_Order_Orderdetails.c.status =='On Hold')
).subquery()


"""--------------------------------------------------------------------"""
# Queries

q_MostSelledProducts = session.query(
   sq_MonthlySelledProducts.c.productCode,
   func.sum(sq_MonthlySelledProducts.c.monthlyAmount).label('totalProductAmount')
).group_by(
   sq_MonthlySelledProducts.c.productCode
).order_by(
   func.sum(sq_MonthlySelledProducts.c.monthlyAmount).desc()
).limit(5)

q_MostSelledProductsMonthly = session.query(
   sq_MonthlySelledProducts.c.productCode,
   sq_MonthlySelledProducts.c.orderDate_Monthyear,
   sq_MonthlySelledProducts.c.monthlyAmount
).filter(
   sq_MonthlySelledProducts.c.productCode.in_(mostSelledProducts)
).group_by(
   sq_MonthlySelledProducts.c.productCode,
   sq_MonthlySelledProducts.c.orderDate_Monthyear
).order_by(
   func.sum(sq_MonthlySelledProducts.c.orderDate_Monthyear).asc()
)

q_DashboardEntries = session.query(
    dashboardEntries.c.counter
).filter(
    dashboardEntries.c.counterType == 'Entries'
)

for row in q_DashboardEntries:
   numberOfEntries = row[0]


q_NotDeliveredOrders = session.query(
   sq_l_Order_Orderdetails.c.orderNumber,
   sq_l_Order_Orderdetails.c.status,
   sq_l_Order_Orderdetails.c.requiredDate,
   sq_l_Order_Orderdetails.c.comments,
   func.sum(sq_l_Order_Orderdetails.c.totalAmount).label('monthlyAmount'),
   func.count(distinct(sq_l_Order_Orderdetails.c.status).label('ordersCount'))
).group_by(
   sq_l_Order_Orderdetails.c.orderNumber,
   sq_l_Order_Orderdetails.c.status,
      sq_l_Order_Orderdetails.c.requiredDate,
   sq_l_Order_Orderdetails.c.comments,
).filter(
   or_(sq_l_Order_Orderdetails.c.status == 'In Process', sq_l_Order_Orderdetails.c.status =='On Hold')
)



q_NotDeliveredOrders_StatusAgg = session.query(
   sq_StatusCountFromOrders.c.status,
   func.sum(sq_StatusAmountFromOrderDetails.c.monthlyAmount).label('TotalOrderAmount'),
   func.sum(sq_StatusCountFromOrders.c.ordersCount).label('TotalOrdersCount')
).join(
   sq_StatusAmountFromOrderDetails,
   sq_StatusAmountFromOrderDetails.c.status == sq_StatusCountFromOrders.c.status,
   isouter = True
).group_by(
   sq_StatusCountFromOrders.c.status
)


"""--------------------------------------------------------------------"""

# Updating SQL Database
def AddDashboardEntry():
    q_DashboardEntries = session.query(
    dashboardEntries.c.counter
    ).filter(
    dashboardEntries.c.counterType == 'Entries'
    )

    if q_DashboardEntries.count() == 0:
        engine.execute(
            insert(dashboardEntries).values(counterType = 'Entries', counter = 1)
        )
    else:
        for row in q_DashboardEntries:
            curr_counter = row[0]
        engine.execute(
            update(dashboardEntries).where(dashboardEntries.c.counterType == 'Entries').values(counter = curr_counter+1)
    )


"""--------------------------------------------------------------------"""

# Alerts    
Alerts.NotDeliveredOrdersAlert(q_NotDeliveredOrders)


   