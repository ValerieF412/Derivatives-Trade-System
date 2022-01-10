#!/usr/bin/python3
#pylint: disable=E1101
#pylint: disable=C0103
"""
functions used in views so the file is readable and not bloated
"""
from collections import defaultdict

import io
import os
from reportlab.pdfgen import canvas
from keras import backend as K
import pandas as pd
from sklearn.externals import joblib
from django.core.files.base import ContentFile
from django.db import connection, transaction


from .models import Trade, Report, Company, Currency, ProductsSold, Error
from .resources import TradeResource

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def getDate(request):
    """ retrievs date from datepicker and returns in django format"""
    year = request.POST.get('date_year')
    month = request.POST.get('date_month')
    day = request.POST.get('date_day')
    return f'{year}-{month}-{day}'

def generate_report(date):
    """ given a date generate report regarding all trades on the day."""
    num_trades = len(Trade.objects.filter(add_date=date))

    # returns the notional sum in usd of trades in a given date.
    notional_sum = 0
    day = Trade.objects.filter(add_date=date)
    for t in day:
        ccy = Currency.objects.filter(currency__iexact=t.notional_currency).first()
        notional_sum += t.notional_amount / ccy.valueInUSD

    # returns the number of erroneous trades.
    trades = []
    errors = Error.objects.all()

    for e in errors:
        trades.append(e.trade_id)

    num_errors = 0
    for trade in trades:
        if trade.add_date == date:
            num_errors += 1

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont('Helvetica', 12)

    p.drawString(30, 750, 'DAILY TRADE EXECUTION')
    p.drawString(30, 735, 'SUMMARY REPORT')
    p.drawString(275, 750, 'DATE GENERATED:')
    p.drawString(500, 750, "12/12/2010")
    p.line(480, 747, 580, 747)

    p.drawString(30, 703, 'TOTAL NUMBER OF TRADES TODAY:')
    p.line(250, 700, 580, 700)
    p.drawString(250, 703, str(num_trades))

    p.drawString(30, 671, 'TOTAL NUMBER OF ERROR CORRECTIONS TODAY:')
    p.line(340, 668, 580, 668)
    p.drawString(340, 671, str(num_errors))

    p.drawString(30, 639, 'TOTAL NOTIONAL VALUE TRADED TODAY(IN USD$):')
    p.line(340, 636, 580, 636)
    p.drawString(340, 639, "$ " + str(notional_sum))

    p.showPage()
    p.save()
    buffer.seek(0) #buffer now contains pdf, use reportlab to draw your pdf

    trade_resource = TradeResource()
    queryset = Trade.objects.filter(add_date=date)
    dataset = trade_resource.export(queryset)
    #this uses the library to return the model data for trades
    #on the given date

    r = Report()
    r.date = date
    r.csv.save(date, ContentFile(dataset.csv)) #save csv
    r.pdf.save(date, buffer) #save pdf

def ohevalue(df):
    """get all the attribute: 'product', 'buyingParty', 'sellingParty', 'quantity', 'strikePrice"""
    ohe_col = joblib.load(os.path.join(CURRENT_DIR, "allcol.pkl"))
    df_processed = pd.get_dummies(df)
    newdict = {}
    for i in ohe_col:
        if i in df_processed.columns:
            newdict[i] = df_processed[i].values
        else:
            newdict[i] = 0
    newdf = pd.DataFrame(newdict)
    return newdf

def strikecheck(unit):
    """ classifier to check strike price is not within ordinary bounds, return 0 or 1"""
    try:
        str_mdl = joblib.load(os.path.join(CURRENT_DIR, "StrPrice_model.pkl"))
        scalers = joblib.load(os.path.join(CURRENT_DIR, "scaler.pkl"))
        X = scalers.transform(unit)
        y_pred = str_mdl.predict(X)
        newdf = pd.DataFrame(y_pred, columns=['erroneous'])
        # newdf = newdf.replace({
        #     0:'Approved',
        #     1:'Rejected, there is something wrong with strike price'
        #     })
        K.clear_session()
        if newdf.values[0][0] == 0:
            return False
        else:
            return True
    except ValueError as e:
        return False

def quantitycheck(unit):
    try:
        str_mdl = joblib.load(os.path.join(CURRENT_DIR, "StrPrice_model.pkl"))
        scalers = joblib.load(os.path.join(CURRENT_DIR, "scaler.pkl"))
        X = scalers.transform(unit)
        y_pred = str_mdl.predict(X)
        newdf = pd.DataFrame(y_pred, columns=['erroneous'])
        newdf = newdf.replace({
            0:'Approved',
            1:'Rejected, there is something wrong with strike price'
            })
        K.clear_session()
        if newdf.values[0][0] == 0:
            return True
        else:
            return False
    except ValueError as e:
        return True

def isTradeErreneous(form):
    ''' Expecting an object of type TradeForm '''
    pName = form.cleaned_data.get('product_name')
    bParty = form.cleaned_data.get('buying_party')
    sParty = form.cleaned_data.get('selling_party')
    quantity = form.cleaned_data.get('quantity')
    strikePrice = form.cleaned_data.get('strikePrice')
    df = pd.DataFrame({"product": pName, "buyingParty": bParty, "sellingParty": sParty,
                       "quantity" : quantity, "strikePrice" : strikePrice}, index=[0])
    
    ohe = ohevalue(df)
    strike_error = strikecheck(ohe)
    quantity_error = quantitycheck(ohe)
    if strike_error and quantity_error:
        answer = 'both'
    if not strike_error and not quantity_error:
        answer = 'no_error'
    if strike_error:
        answer = 'strike_price'
    if quantity_error:
        answer = 'quantity'
    return answer

def error_validation(data):
    """ Verify if user entered parties, currency and product exist """
    buyer = data.get('buying_party').upper()
    seller = data.get('selling_party').upper()
    cur = data.get('underlying_currency').upper()
    product = data.get('product_name')

    product_exists = (
        (ProductsSold.objects.filter(product__iexact=product).exists()) or
        product == 'Stocks'
        )
    buyer_exists = Company.objects.filter(companyID__iexact=buyer).exists()
    seller_exists = Company.objects.filter(companyID__iexact=seller).exists()
    cur_exists = Currency.objects.filter(currency__iexact=cur).exists()

    if buyer_exists and seller_exists and cur_exists and product_exists:
        return {}
    return {'Product Name is invalid': product_exists,
            'Buyer ID is invalid': buyer_exists,
            'Seller ID is invalid': seller_exists,
            'Currency is invalid': cur_exists
            }

def add_error_correction(trade, field, old, new):
    """ adds an error to the error table"""
    error = Error.create(trade, field, old, new)
    error.save()

def has_correction(trade, field):
    """ If an repeated correction has occured this will find it for an entered trade"""
    corrections = []
    dict_corrections = defaultdict(lambda: 0)
    #default dict to store how many of 1 correction a user makes
    trades = Trade.objects.filter( #attributes we filter trades by
        selling_party=trade.selling_party,
        buying_party=trade.buying_party,
        product_name=trade.product_name
    )

    #get id of all trades that match above description
    #join with errors table on foreign key
    #aggregate remaining records in error table using count on field,old,new
    #go through the count until first == 3 is found and use that
    for t in trades: #for each trade
        errors = Error.objects.filter(trade_id=t, field=field)
        #if there is an error for the suspected field
        for e in errors: #for every error of of that type can be none
            if e.old == getattr(trade, field):
                #if that error original value matches user input (same mistake)
                corrections.append(e)
    for c in corrections: #for every possible matching error made in the past
        dict_corrections[(c.old, c.new)] += 1 #add one to occurence
        if dict_corrections[(c.old, c.new)] == 2:
            if field == 'quantity':
                trade.quantity = c.new
            else:
                trade.strike_price = c.new
            trade.save()
            return True #there is new value to correct
    return False #no new value

def corrections():
    cursor = connection.cursor()
    corrections = []
    q = "SELECT *, COUNT(*) " \
        "FROM (" \
            "SELECT product_name, buying_party, selling_party, field, old, new " \
            "FROM trades_error LEFT OUTER JOIN trades_trade " \
            "ON trades_trade.id = trades_error.trade_id_id) " \
            "GROUP BY product_name, buying_party, selling_party, field, old, new " \
            "HAVING COUNT(*) > 1"
        #sql query
    cursor.execute(q)
    for row in cursor:
        corrections.append(row)
    return corrections

