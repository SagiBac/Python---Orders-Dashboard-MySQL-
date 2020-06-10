import csv
import os.path


def NotDeliveredOrdersAlert(i_QueryRows):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "alerts/Not Delivered Orders.csv")

    with open(path, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow( ["Order","Status","RequiredDate","Comments","Order Amount"] )
        for row in i_QueryRows:
            csvRow = []
            for i in range(0,len(row)-1):
                csvRow.append(row[i])
            filewriter.writerow(csvRow)
        


