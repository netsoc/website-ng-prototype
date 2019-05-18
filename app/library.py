import csv


'''
Mock DB functions
'''
def books_from_csv():
    books = []
    with open('/opt/app/static/lib.csv') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        for line in reader:
            books.append({key: val for key, val in zip(headers, line)})

    print(books[0])
    return books

def lookup(id):
    books = books_from_csv()
    for b in books:
        if str(b['callnumber'])==id:
            return b
    return None
