import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  \n({v:d})'.format(p=pct,v=val)
    return my_autopct


def MostSelledProducts_horizonal(i_Query, i_Figure, i_Position):
    data = []
    products = []
    ax = i_Figure.add_subplot(i_Position)
    ax.set_title("Most Selled Products (All time)", fontweight='bold')
    ax.set_xticklabels([])   #hide X axis numbers

    result = i_Query
    for row in result:
        data.append(int(row[1]))
        products.append(str(row[0]))

    plotData = {"products":products , "totalAmount":data}
    df = pd.DataFrame(plotData, index = products)

    df.sort_values(
        by = "totalAmount"
    ).plot(
        kind = "barh", 
        color = "steelblue", 
        legend = False, 
        ax = ax
    )

    for i, v in enumerate(sorted(df.totalAmount)):
        plt.text(10000, i , str('{:,.0f}K $'.format(int(v)/1000)), color='white',fontweight='bold' , va="center")
    
      

def MonthlySelledProducts(i_Query, i_Figure, i_Position, i_ProductList):
    data=[[],[]]
    ax = i_Figure.add_subplot(i_Position)
    ax.set_title("Monthly Selling Of Most Selled Products", fontweight='bold')
    
    result = i_Query
    for product in i_ProductList:
        for row in result:
            if row[0] == product:
                data[0].append(int(row[2]))
                data[1].append(row[1])
        ax.plot(data[1], data[0], '.-', label=product)       
        data=[[],[]]

    datacursor()
    ax.legend(loc='best')
    ax.set_ylabel('Price in $')
    

def NotDeliveredOrders(i_Query, i_Figure, i_Position):
    statuses = []
    orderAmounts = []
    orderCounts = []
    ax = i_Figure.add_subplot(i_Position)
    ax.set_title("Not Delivered Orders", fontweight='bold')

    for row in i_Query:
        statuses.append(row[0])
        orderAmounts.append(row[1])
        orderCounts.append(row[2])

    plotAggStatuses = {"statuses":statuses , "orderAmounts":orderAmounts ,  "orderCounts":orderCounts}    
    dfAmount = pd.DataFrame(plotAggStatuses, index = statuses)

    
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    
    labels = []
    for status in dfAmount['statuses'].tolist():
        labels.append(
            status
            +'\n('
            +'{:,.1f}K $)'.format(int(dfAmount['orderAmounts'][status])/1000)
            )
    explode = (0, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    dfAmountFloat = [float(n) for n in dfAmount['orderCounts'].tolist()]
    ax.pie(dfAmountFloat, 
            explode=explode, 
            labels=labels, 
            autopct = make_autopct(dfAmountFloat),
            shadow=True, startangle=90)

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    plt.show()


