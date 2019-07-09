import csv


# Write to CSV
def write(data):
    with open("trades.csv", 'a', newline='') as file:
        wr = csv.writer(file, dialect='excel')
        wr.writerow(data)


# Read from CSV
def read_all():
    trade_list = []
    with open("trades.csv", 'r', newline='') as file:
        rd = csv.reader(file, dialect='excel')
        for row in rd:
            trade_list.append(row)
    return trade_list


# Clear the CSV file
def clear_csv():
    f = open("trades.csv", "w")
    f.truncate()
    f.close()
