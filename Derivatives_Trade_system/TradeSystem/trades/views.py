#!/usr/bin/python3

from collections import defaultdict, Counter

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.views import generic


from .forms import TradeForm, ReportForm, ErrorDetectedForm
from . serializers import tradesSerializers
from rest_framework import viewsets
from django import forms
from reportlab.lib.pagesizes import letter
from django.contrib import messages
from .filters import TradeFilter
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
import pickle
import json
import numpy as np
from sklearn import preprocessing
from collections import defaultdict, Counter
import datetime
from .func import *

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def index(request):
    return render(request, 'index.html')

def reports(request):
    if request.method == 'POST':
        date = getDate(request)
        if Report.objects.filter(date=date).exists(): #if the date already has a report
            if False: #replace False with a query on whether user confirms report 
                return redirect('/trades/reports/')
            
            Report.objects.get(date=date).csv.delete(save=True) #delete files
            Report.objects.get(date=date).pdf.delete(save=True)
            Report.objects.get(date=date).delete() #delete record
            
        form = ReportForm(request.POST)
        
        if form.is_valid():
            generate_report(str(form.cleaned_data.get('date')))
            return redirect('/trades/reports/')
    else:
        form = ReportForm()
        reports = Report.objects.all()
        return render(request,'reports.html',{'form': form, 'reports': reports})

class TradesView(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = tradesSerializers



##added one time flash pop up to alert user to trade input success. Also redirects the user upon a successful trade was added .
# receive the above data, if the method get, filter
def data_entry(request): #
    if request.method == 'POST':
        form = TradeForm(request.POST)
        data = request.POST.copy()
        errors = error_validation(data)
        if len(errors.values()) > 0:
            for error_msg, exists in errors.items():
                if not exists:
                    messages.error(request,error_msg)
            return render(request, 'data_entry.html',{'form':form})
        if form.is_valid():
                #if you refresh on error entry this prevents a crash lots of spaghetti
            trade = form.save()
            error_type = isTradeErreneous(form)
            if error_type == 'no_error':
                messages.success(request, f'Trade of {data.get("quantity")} {data.get("product_name")} derivatives, sold by : {data.get("selling_party")} to {data.get("buying_party")}, successfully added.')
                return redirect('/trades/trade/') 
            else:

                auto = False
                both_strike = False
                both_quant = False
                if error_type != 'both':#if only one field is potentially wrong
                    auto = has_correction(trade,error_type)
                else: #if both fields are potentially wrong
                    both_strike = has_correction(trade,'strike_price')
                    both_quant  = has_correction(trade,'quantity')

                if auto or both_strike or both_quant: #if any auto correct is pinged
                    messages.success(request,'We have auto corrected an error which you have performed more than 2 times. ')
                    return redirect('/trades/trade') #just return to trades, 
                    #correction already applied in has_correction
             
                form = ErrorDetectedForm(initial={'strike_price' : trade.strike_price,
                                          'quantity' : trade.quantity})
                if error_type == 'strike_price': #remove field we don't need
                    form.fields.pop('quantity')
                if error_type == 'quantity':
                    form.fields.pop('strike_price')

                # error_type will be one of: 'strike_price', 'quantity' or 'both'
                
                context  = {'id':trade.id, 'error':error_type, 'form': form}
                messages.warning(request, f'We have detected a possible error, check {error_type} field(s), if they are correct just press update ')
                return render(request,'error_detected.html',context)
                #return redirect(f'/trades/error_detected/{trade_id}/{error}')
                
    else:
        form = TradeForm() #invalid info return an empty form for the user
    return render(request, 'data_entry.html',{'form':form})

def error_detected(request, id, error_type):
    trade = Trade.objects.get(id=id)
    msg = False
    if request.method == 'POST':
        if error_type != 'both': #if only one possible correction
            new = float(request.POST[f'{error_type}'])
            old = float(trade.__dict__[f'{error_type}'])
            if old != new: #user actually made an update(changed valuse)

                add_error_correction(trade, error_type, getattr(trade,f'{error_type}'), new)
                trade.__dict__[f'{error_type}'] = new
                trade.save() #make sure change is applied
                msg=True
        else:
            new_strike = request.POST['strike_price']
            new_quant = request.POST['quantity']
            old_quant = trade.__dict__['quantity']
            old_strike = trade.__dict__['strike_price']

            if old_quant != new_quant: #two possible corrections
                add_error_correction(trade, 'quantity', trade.__dict__['quantity'], new_quant)
                msg = True
            if old_strike != new_strike:
                add_error_correction(trade, 'strike_price', trade.__dict__['strike_price'], new_strike)
                msg = True
        if msg:
            messages.success(request, 'Updated Trade with new values')
        return redirect('/trades/trade/')

        return redirect('/trades/trade/')
    return redirect('/trades/trade') #GET


def trades(request): #returns the filtered trades
    ''' localhost:8000/trades/trade '''
    trades = Trade.objects.all()
    myFilter = TradeFilter(request.GET, queryset=trades)
    trades = myFilter.qs
    context = {'trades': trades, 'myFilter': myFilter}
    return render(request, 'trades.html',context)

def edit(request, id):
    form = TradeForm()
    trade = Trade.objects.get(id=id)    
    date = getattr(trade, 'add_date')
    dt = datetime.datetime.combine(date, datetime.datetime.max.time())
    delta = (dt - datetime.datetime.today())
    if (delta > datetime.timedelta(days=1)):
        messages.error(request, 'Trade cannot be edited, as it was originally created more than 24 hours ago.')
        return redirect('/trades/trade/') 
    for field in dir(trade): 
        form.fields[f"{field}"].initial = getattr(trade,f'{field}')#set the initial values so user can edit
        #in the box to that of the trade so only wanted changes are made.
    return render(request,'edit.html',{'trade':trade,'form':form})

def update(request, id):
    trade = Trade.objects.get(id=id) #get trade
    form = TradeForm(request.POST, instance=trade)
    
    if form.is_valid(): #if changes are valid 
        form.save() #save changes
        return redirect("/trades/trade")
    return render(request,'edit.html',{'trade':trade})

def delete(request, id):
    trade = Trade.objects.get(id=id)
    trade.delete()
    return redirect("/trades/trade")

def history(request,id):
    trade = Trade.objects.get(id=id) #get wanted trade
    history = trade.history.all() #get history of trade
    context = {'history': history}
    return render(request,'history.html',context) #return history to output.

def correction(request):
    table = corrections() #output all corrections
    context = {'data': table}
    return render(request, 'corrections.html', context)

def delete_correction(request, field, old, new): #delete correction
    if request.method == 'GET':
        errors = Error.objects.filter(field=field, old=old, new=new).delete()
    return redirect("/trades/corrections")
