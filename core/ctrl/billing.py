from fakturoid import Fakturoid
from datetime import date, datetime
from core import app, data, utils


def auth():
    fa = Fakturoid(app.config['billing']['slug'], app.config['billing']['email'],
                   app.config['billing']['apiKey'], f"{app.config['full_name']} ({app.config['billing']['email']})")
    return fa


def load_invoices(data_pass):

    if type(data_pass) is not dict or 'year' not in data_pass.keys():
        x = datetime.now()
        year = x.year
    else:
        year = data_pass['year']

    fa = auth()

    _invoices = fa.invoices(proforma=False, since=date(year, 1, 1))
    invoices = []

    for invoice in _invoices:
        print(invoice.number, invoice.total, invoice.variable_symbol)
        invoices.append(invoice.get_fields())

    result = {
        'status': True,
        'message': f"List of invoices in year {year}",
        'invoices': invoices
    }

    return result
