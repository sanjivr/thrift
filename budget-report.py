#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from datetime import datetime
import gspread
import os


# In[ ]:


def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            #print("Jupyter notebook or qtconsole")
            return True
        elif shell == 'TerminalInteractiveShell':
            #print("Terminal running IPython")
            return False
        else:
            #print("Other type (?)")
            return False
    except NameError:
        #print("Probably standard")
        return False
    


# In[ ]:


CREDS_FILE = 'service_account.json'
if is_notebook():
    import IPython
    HTML = IPython.display.HTML
    creds_file_path = CREDS_FILE
else:
    creds_file_path = os.path.dirname(os.path.realpath(__file__)) + '/' +  CREDS_FILE


# In[ ]:


gc = gspread.service_account(filename=creds_file_path)

years = []
years.append(datetime.now().year)
#years.append(2022)

rdfs = []
for year in years:
    sh = gc.open(str(year))
    worksheet = sh.worksheet('USD')
    report_id = 'Report'
    try:
        report_worksheet = sh.add_worksheet(title=report_id, rows=200, cols=14)
    except:
        report_worksheet = sh.worksheet(report_id)
    rdfs.append(pd.DataFrame(worksheet.get_all_records()))
    #rdfs.append(pd.read_excel(f'~/playground/Expenses/{year}.xlsx', sheet_name="USD"))



# In[ ]:


rdf = pd.concat(rdfs)

rdf["Merchant"] = rdf["Merchant"].str.strip()
rdf['Date'] =  pd.DatetimeIndex(rdf.Date)
rdf = rdf.drop(columns=["Notes", "Description"])


# In[ ]:


credits = rdf[(rdf["Transaction Type"] == "credit") & (rdf["Category"] != "Salary")]
credits = credits.assign(Amount=lambda x: x.Amount * -1)
credits['Amount'].sum()


# In[ ]:


debits = rdf[rdf["Transaction Type"] == "debit"]
debits['Amount'].sum()


# In[ ]:


df = pd.concat([debits, credits])
df = df.assign(parsed=df['Category'].str.split('+')).explode('parsed')
df = df.drop(columns="Category")
#df


# In[ ]:


def category(parsed):
    return parsed.split('(').str[0].str.strip()


# In[ ]:


def amount(parsed):
    return parsed.split('(').str[1]


# In[ ]:


df = df.assign(Category=lambda x: category(x.parsed.str))
df = df.assign(RAmount=lambda x: amount(x.parsed.str))

df['RAmount'] = df['RAmount'].str.split(')').str[0].astype('float')
df['RAmount'].fillna(df['Amount'], inplace=True)
df = df.drop(columns='parsed')


# In[ ]:


monthly_report = df.groupby([df.Date.dt.to_period('M'), "Category"])['RAmount'].sum().reset_index(name='Amount').sort_values(by=['Date', 'Amount'], ascending=False)
monthly_report['Amount'].sum()
#monthly_report


# In[ ]:


pv_table = pd.pivot_table(monthly_report, index = 'Category', columns = 'Date', values = 'Amount', fill_value=0, dropna=False)
#fig = pv_table.plot(kind = 'bar', figsize=(20,10),  yticks=(100, 250, 500, 1000, 1500, 2000, 2500, 5000))


# In[ ]:


#fig.get_figure().savefig("monthly_category_report.png", format="png")


# In[ ]:


category_report = df.groupby(["Category"])['RAmount'].sum().reset_index(name='Amount').sort_values(by=['Amount'], ascending=False)
#with pd.option_context("display.max_rows", 1000):
#    display(HTML(category_report.to_html(index=False, header=True)))


# In[ ]:


annual_monthly_report=category_report.merge(pv_table, on='Category')

annual_monthly_report.loc['Total'] = annual_monthly_report.sum(numeric_only=True)
annual_monthly_report = annual_monthly_report.fillna(value={"Category": "Total"}, limit=1).sort_values(by=['Amount'], ascending=False)

columns = annual_monthly_report.columns.values.tolist()
for idx, val in enumerate(columns):
    if isinstance(val, pd.Period):
        # pd.Period is not json serializable for writing to Google Sheets
        columns[idx] = val.strftime('%B')
        
report_worksheet.update( [columns] + annual_monthly_report.values.tolist())
if is_notebook():
    with pd.option_context("display.max_rows", 1000):   
        display(HTML(annual_monthly_report.to_html(index=False, header=True)))


# In[ ]:


# Bar Chart of Annual Category Report
#category_report.plot.bar(x='Category', y='Amount', figsize=(20,10),  yticks=(100, 250, 500, 1000, 1500, 2000, 2500, 5000))


# In[ ]:


category_report['Amount'].sum()


# In[ ]:


merchant_report = df.groupby(["Merchant"])['RAmount'].sum().reset_index(name='Amount').sort_values(by=['Amount'], ascending=False)
#with pd.option_context("display.max_rows", 1000):
#    display(HTML(merchant_report.to_html(index=False, header=True)))


# In[ ]:


monthly_merchant_report = df.groupby([df.Date.dt.to_period('M'), "Merchant"])['RAmount'].sum().reset_index(name='Amount').sort_values(by=['Date', 'Amount'], ascending=False)
#monthly_report


# In[ ]:


pv_merchant_table = pd.pivot_table(monthly_merchant_report, index = 'Merchant', columns = 'Date', values = 'Amount', fill_value=0, dropna=False)
#fig = pv_merchant_table.plot(kind = 'bar', figsize=(20,10),  yticks=(100, 250, 500, 1000, 1500, 2000, 2500, 5000))


# In[ ]:


annual_monthly_merchant_report=merchant_report.merge(pv_merchant_table, on='Merchant')
annual_monthly_merchant_report.loc['Total'] = annual_monthly_merchant_report.sum(numeric_only=True)
annual_monthly_merchant_report = annual_monthly_merchant_report.fillna(value={"Merchant": "All"}, limit=1)


with pd.option_context("display.max_rows", 1000):
#    display(HTML(annual_monthly_merchant_report
#                .sort_values(by=['Amount'], ascending=False)
#                 .to_html(index=False, header=True)))
    pass

