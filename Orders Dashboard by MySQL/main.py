import SQLQueries
import graphs
import matplotlib.pyplot as plt


# Data presentation

fig = plt.figure()
fig.subplots_adjust( hspace = 0.5 )
fig.suptitle('Orders Dashboard\n Number of Entries: '+str(SQLQueries.numberOfEntries), fontsize=16, fontweight='bold')


graphs.MostSelledProducts_horizonal(SQLQueries.q_MostSelledProducts, fig, 221)
graphs.MonthlySelledProducts(SQLQueries.q_MostSelledProductsMonthly, fig, 212, SQLQueries.mostSelledProducts)
graphs.NotDeliveredOrders(SQLQueries.q_NotDeliveredOrders_StatusAgg, fig, 222)
SQLQueries.AddDashboardEntry()
plt.show()
