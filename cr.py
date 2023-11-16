import os
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly import graph_objs as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide", page_icon="💰", page_title="CR Report")
st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(28, 131, 225, 0.1);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: rgb(205, 104, 0);
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: black;
}
</style>
""", unsafe_allow_html=True)

# main variables
# get the quarter from today date as default
today = pd.Timestamp.today()
    
# get the year from today date as default
default_year = today.year
default_quarter = today.quarter
default_month = today.month

def format_row(row_data, col_widths):
    return "| " + " | ".join(data.ljust(width) for data, width in zip(row_data, col_widths)) + " |"

# load data from csv file from main file Acis_Sales_Master_Export_Matched.csv
def load_data_main():
    # load the data csv file online and return a dataframe
    #data = pd.read_csv('https://github.com/jjaramillo34/sebasapp/blob/master/Acris_Sales_Master_Export_Matched.csv', low_memory=False)
    #print(data.columns)
    data = pd.read_csv('Acris_Sales_Master_Export_Matched.csv', low_memory=False)
    # make a copy of the dataframe
    copy_df = data.copy()
    # make the column names lower case
    copy_df.columns = copy_df.columns.str.lower()
    # concatenate address and street name
    copy_df['address1'] = copy_df['address'] + ' ' + copy_df['street']
    # drop the columns address and street
    copy_df.drop(columns=['address', 'street'], inplace=True)
    # rename the column address1 to address
    copy_df.rename(columns={'address1': 'address'}, inplace=True)
    # certains rows column flag Orange Flag, Yellow Flag, Red Flag, Inactive Flag and Oulier Flag
    copy_df = copy_df[~copy_df['flag'].isin(['Red Flag', 'Inactive', 'Outlier'])]
    # drop the columns history_id, unit_id, CONCIERGE	FT_DOORMAN	PT_DOORMAN	ATTENDED_LOBBY
    copy_df = copy_df.drop(columns=['history_id', 'unit_id', 'concierge', 'ft_doorman', 'pt_doorman', 'attended_lobby'])
    # remove metro group QN, SI and BX
    copy_df = copy_df[~copy_df['metro'].isin(['QN', 'SI', 'BX'])]
    # remove blg_type blanks
    copy_df = copy_df[~pd.isna(copy_df['bldg_type'])]
    # blg_type column as string
    copy_df['bldg_type'] = copy_df['bldg_type'].astype(str)
    # replace condop with condo using lambda function
    copy_df['bldg_type'] = copy_df['bldg_type'].apply(lambda x: x.replace('condop', 'condo'))
    # save the dataframe to a csv file
    # remove data before 2002
    copy_df = copy_df[copy_df['sale_year'] > 2002]
    # remove sales lower than 100,000
    copy_df = copy_df[copy_df['sale_price'] > 100000]
    # remove metro group blanks
    copy_df = copy_df[~pd.isna(copy_df['metro'])]
    # change metro MAN, BK to Manhattan and Brooklyn proper case
    copy_df['metro'] = copy_df['metro'].apply(lambda x: x.replace("MAN", "Manhattan"))
    copy_df['metro'] = copy_df['metro'].apply(lambda x: x.replace("BK", "Brooklyn"))
    copy_df.to_csv('acris_sales_master_export_matched_clean.csv', index=False)
    return copy_df
  
# execute the function to load the data csv file main
load_data_main()
  
def load_data():
    # load the data csv file online and return a dataframe
    data = pd.read_csv('acris_sales_master_export_matched_clean.csv', low_memory=False)
    # change metro MAN to MANHATTAN, BK to BROOKLYN
    data['metro'] = data['metro'].apply(lambda x: x.replace("MN", "MANHATTAN"))
    data['metro'] = data['metro'].apply(lambda x: x.replace("BK", "BROOKLYN"))
    
    # change DWN to Downtown, ES to Upper East Side, WS to Upper West Side, MN to Midtown, FIDI to Financial District/BPC
    data['market'] = data['market'].apply(lambda x: x.replace('DWN', 'Downtown'))
    data['market'] = data['market'].apply(lambda x: x.replace('ES', 'Upper East Side'))
    data['market'] = data['market'].apply(lambda x: x.replace('WS', 'Upper West Side'))
    data['market'] = data['market'].apply(lambda x: x.replace('MID', 'Midtown'))
    data['market'] = data['market'].apply(lambda x: x.replace('FIDI', 'Financial District/BPC'))
    data['market'] = data['market'].apply(lambda x: x.replace('BKLYN', 'Brooklyn'))
    # remove metro group blanks
    data = data[~pd.isna(data['metro'])]
    

    # get a message that the data is loading and show the progress bar
    st.text('Loading data...')
    # progress bar
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)
    # make a copy of the dataframe
    # make the message disappear
    st.text('')
    # make the column names lower case
    return data
  
def change_to_billions(x, pos):
    'The two args are the value and tick position'
    return '${:1.1f}B'.format(x * 1e-9)

def main():
    data = load_data()
    st.title("CR Report")
    # make a copy of the dataframe
    new_df = data.copy()

    # make the column names lower case
    new_df.columns = new_df.columns.str.lower()
    
    # remove year 2013 or less
    st.sidebar.subheader('Select Year')
    year_input = st.sidebar.slider('Year', 2013, default_year, 2013)
    st.sidebar.subheader('Select Metro')
    
    unique_metro = new_df['metro'].unique()
    # remove QN, SI and BX and Nan
    unique_metro = unique_metro[unique_metro != 'QN']
    # drop nan values
    unique_metro = unique_metro[~pd.isna(unique_metro)]
    metro_input = st.sidebar.radio('Metro', unique_metro)
    
    metro_old = new_df[new_df['metro'] == metro_input]
    metro_old = metro_old[metro_old['sale_year'] < 2013]
    
    #metro_old = new_df[new_df['metro'].isin(['MAN', 'BK'])]
    #metro_old = metro_old[metro_old['sale_year'] < 2013]
    
    metro = new_df[new_df['metro'] == metro_input]
    metro = metro[metro['sale_year'] > 2012]
    #metro = new_rdf[new_df['metro'].isin(['MAN', 'BK'])]
    #metro = metro[metro['sale_year'] > 2012]
    # create a pivot table for average sale price each year by metro
    yearly_avg_price = pd.pivot_table(metro, index=['metro', 'sale_year', "bldg_type"], values=['sale_price'], aggfunc='mean')
    yearly_avg_price = yearly_avg_price.reset_index()
    yearly_avg_price = yearly_avg_price[yearly_avg_price['sale_year'] == year_input]
    previouse_year = year_input - 1
    if year_input == 2013:
        previouse_year_avg_price = pd.pivot_table(metro_old, index=['metro', 'sale_year', "bldg_type"], values=['sale_price'], aggfunc='mean')
        previouse_year_avg_price = previouse_year_avg_price.reset_index()
        previouse_year_avg_price = previouse_year_avg_price[previouse_year_avg_price['sale_year'] == previouse_year]
    else:
        previouse_year_avg_price = pd.pivot_table(metro, index=['metro', 'sale_year', "bldg_type"], values=['sale_price'], aggfunc='mean')
        previouse_year_avg_price = previouse_year_avg_price.reset_index()
        previouse_year_avg_price = previouse_year_avg_price[previouse_year_avg_price['sale_year'] == previouse_year]
    # total sales amount by year and metro group    
    total_sales = pd.pivot_table(metro, index=['metro', 'sale_year', "bldg_type"], values=['sale_price'], aggfunc='count')
    total_sales = total_sales.reset_index()
    total_sales = total_sales[total_sales['sale_year'] == year_input]
    
    if year_input == 2013:
        previouse_year_total_sales = pd.pivot_table(metro_old, index=['metro', 'sale_year', "bldg_type"], values=['sale_price'], aggfunc='count')
        previouse_year_total_sales = previouse_year_total_sales.reset_index()
        previouse_year_total_sales = previouse_year_total_sales[previouse_year_total_sales['sale_year'] == previouse_year]
    else:
        previouse_year_total_sales = pd.pivot_table(metro, index=['metro', 'sale_year', "bldg_type"], values=['sale_price'], aggfunc='count')
        previouse_year_total_sales = previouse_year_total_sales.reset_index()
        previouse_year_total_sales = previouse_year_total_sales[previouse_year_total_sales['sale_year'] == previouse_year]

    # price ppsf by year and metro group
    price_per_sqft = pd.pivot_table(metro, index=['metro', 'sale_year', "bldg_type"], values=['ppsf'], aggfunc='mean')
    price_per_sqft = price_per_sqft.reset_index()
    price_per_sqft = price_per_sqft[price_per_sqft['sale_year'] == year_input]
    
    if year_input == 2013:
        previouse_year_price_per_sqft = pd.pivot_table(metro_old, index=['metro', 'sale_year', "bldg_type"], values=['ppsf'], aggfunc='mean')
        previouse_year_price_per_sqft = previouse_year_price_per_sqft.reset_index()
        previouse_year_price_per_sqft = previouse_year_price_per_sqft[previouse_year_price_per_sqft['sale_year'] == previouse_year]
    else:
        previouse_year_price_per_sqft = pd.pivot_table(metro, index=['metro', 'sale_year', "bldg_type"], values=['ppsf'], aggfunc='mean')
        previouse_year_price_per_sqft = previouse_year_price_per_sqft.reset_index()
        previouse_year_price_per_sqft = previouse_year_price_per_sqft[previouse_year_price_per_sqft['sale_year'] == previouse_year]
    
    # create a pivot table for average sale price each year by metro
    cols = st.columns(2)
    with cols[0]:
        # metrics for average sale price
        st.subheader('Average Sale Price')
        # metrics by building type condo, coop and condop for each metro group 
        condo = round(int(yearly_avg_price[yearly_avg_price['bldg_type'] == 'condo']['sale_price'].mean()), 2)
        coop = round(int(yearly_avg_price[yearly_avg_price['bldg_type'] == 'coop']['sale_price'].mean()), 2)
        #condop = round(int(yearly_avg_price[yearly_avg_price['bldg_type'] == 'condop']['sale_price'].mean()), 2)
        # variables for pv
        condo_prev = round(int(previouse_year_avg_price[previouse_year_avg_price['bldg_type'] == 'condo']['sale_price'].mean()), 2)
        coop_prev = round(int(previouse_year_avg_price[previouse_year_avg_price['bldg_type'] == 'coop']['sale_price'].mean()), 2)
        #condop_prev = round(int(previouse_year_avg_price[previouse_year_avg_price['bldg_type'] == 'condop']['sale_price'].mean()), 2)
        # calculate the deltas
        delta1 = round((int(condo) - int(condo_prev)) / int(condo_prev) * 100, 2)
        delta2 = round((int(coop) - int(coop_prev)) / int(coop_prev) * 100, 2)
        #delta3 = round((int(condop) - int(condop_prev)) / int(condop_prev) * 100, 2)
        # display the metrics
        st.metric(label='Condo', value=f"${format(condo, ',d')}", delta=f"{delta1}% pv average sale price of ${format(condo_prev, ',d')}")
        st.metric(label='Coop', value=f"${format(coop, ',d')}", delta=f"{delta2}% pv average sale price of ${format(coop_prev, ',d')}")
        #st.metric(label='Condop', value=f"${format(condop, ',d')}", delta=f"{delta3}% pv average sale price of ${format(condop_prev, ',d')}")
        
    with cols[1]:
        import plotly.express as px
        st.subheader('Total Sales Amount by Average Sale Price')
        # plot average sale price by year and metro group by bldg_type different colors
        fig = px.bar(yearly_avg_price, x='sale_year', y='sale_price', color='bldg_type', barmode='group', title='Average Sale Price by Year and Building Type')

        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        
    cols = st.columns(2)
    with cols[0]:
      st.subheader('Average Total Sales Amount')
      condo = round(int(total_sales[total_sales['bldg_type'] == 'condo']['sale_price'].sum()), 2)
      coop = round(int(total_sales[total_sales['bldg_type'] == 'coop']['sale_price'].sum()), 2)
      #condop = round(int(total_sales[total_sales['bldg_type'] == 'condop']['sale_price'].sum()), 2)
      # variables for pv
      condo_prev = round(int(previouse_year_total_sales[previouse_year_total_sales['bldg_type'] == 'condo']['sale_price'].sum()), 2)
      coop_prev = round(int(previouse_year_total_sales[previouse_year_total_sales['bldg_type'] == 'coop']['sale_price'].sum()), 2)
      #condop_prev = round(int(previouse_year_total_sales[previouse_year_total_sales['bldg_type'] == 'condop']['sale_price'].sum()), 2)
      # calculate the deltas
      delta1 = round((int(condo) - int(condo_prev)) / int(condo_prev) * 100, 2)
      delta2 = round((int(coop) - int(coop_prev)) / int(coop_prev) * 100, 2)
      #delta3 = round((int(condop) - int(condop_prev)) / int(condop_prev) * 100, 2)
      
      st.metric(label='Condo', value=f"{format(condo, ',d')}", delta=f"{delta1}% pv total sales amount of {format(condo_prev, ',d')}")
      st.metric(label='Coop', value=f"{format(coop, ',d')}", delta=f"{delta2}% pv total sales amount of {format(coop_prev, ',d')}")
      #st.metric(label='Condop', value=f"{format(condop, ',d')}", delta=f"{delta3}% pv total sales amount of {format(condop_prev, ',d')}")
      
    with cols[1]:
      st.subheader('Total Sales Amount by Building Type')
      # plot average sale price by year and metro group by bldg_type different colors
      fig = px.bar(total_sales, x='sale_year', y='sale_price', color='bldg_type', barmode='group', title='Total Sales Amount by Year and Building Type')

      st.plotly_chart(fig, theme="streamlit", use_container_width=True)
      
    cols = st.columns(2)
    with cols[0]:
      st.subheader('Average Price ppsf')
      condo = round(int(price_per_sqft[price_per_sqft['bldg_type'] == 'condo']['ppsf'].mean()), 2)
      coop = round(int(price_per_sqft[price_per_sqft['bldg_type'] == 'coop']['ppsf'].mean()), 2)
      #condop = round(int(price_per_sqft[price_per_sqft['bldg_type'] == 'condop']['ppsf'].mean()), 2)
      # variables for pv
      condo_prev = round(int(previouse_year_price_per_sqft[previouse_year_price_per_sqft['bldg_type'] == 'condo']['ppsf'].mean()), 2)
      coop_prev = round(int(previouse_year_price_per_sqft[previouse_year_price_per_sqft['bldg_type'] == 'coop']['ppsf'].mean()), 2)
      #condop_prev = round(int(previouse_year_price_per_sqft[previouse_year_price_per_sqft['bldg_type'] == 'condop']['ppsf'].mean()), 2)
      # calculate the deltas
      delta1 = round((int(condo) - int(condo_prev)) / int(condo_prev) * 100, 2)
      delta2 = round((int(coop) - int(coop_prev)) / int(coop_prev) * 100, 2)
      #delta3 = round((int(condop) - int(condop_prev)) / int(condop_prev) * 100, 2)
      
      st.metric(label='Condo', value=f"${format(condo, ',d')}", delta=f"{delta1}% pv average price ppsf of ${format(condo_prev, ',d')}")
      st.metric(label='Coop', value=f"${format(coop, ',d')}", delta=f"{delta2}% pv average price ppsf of ${format(coop_prev, ',d')}")
      #st.metric(label='Condop', value=f"${format(condop, ',d')}", delta=f"{delta3}% pv average price ppsf of ${format(condop_prev, ',d')}")
    
    with cols[1]:
      st.subheader('Average Price ppsf by Building Type')
      # plot average sale price by year and metro group by bldg_type different colors
      fig = px.bar(price_per_sqft, x='sale_year', y='ppsf', color='bldg_type', barmode='group', title='Average Price ppsf by Year and Building Type')
      
      st.plotly_chart(fig, theme="streamlit", use_container_width=True)
      
    # filter the dataframe by metro group month and year and bldg_type and sale price, and ppsf get the average sale price and ppsf by month and year count the sales by month and plot the average sale price by month and year
    #cols = st.columns(1)
    month_data = new_df[new_df['metro'] == metro_input]
    month_data = month_data[month_data['sale_year'] == year_input]
    month_data = month_data[month_data['bldg_type'] == 'condo']
    month_data = month_data[['sale_month', 'sale_price', 'ppsf']]
    month_data = month_data.groupby(['sale_month']).mean()
    month_data = month_data.reset_index()
      
    st.write(month_data)
    
    # convert the month number to month name
    month_data['sale_month'] = month_data['sale_month'].astype(str)
    # replace the month number with the month name for all months
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('12', 'December'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('11', 'November'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('10', 'October'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('9', 'September'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('8', 'August'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('7', 'July'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('6', 'June'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('5', 'May'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('4', 'April'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('3', 'March'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('2', 'February'))
    month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('1', 'January'))
    #month_data['sale_month'] = month_data['sale_month'].apply(lambda x: x.replace('1', 'January'))
    
    # plot average sale price by year and metro group by bldg_type different colors
    fig = px.bar(month_data, x='sale_month', y='sale_price', color='sale_month', barmode='group', title='Average Sale Price by Month')
    fig.update_layout(
      xaxis_title="Month",
      yaxis_title="Average Sale Price",
      legend_title="Month",
      font=dict(
          family="Courier New, monospace",
          size=12,
          color="RebeccaPurple"
      )
    )
    # make the plot bar wider
    fig.update_layout(barmode='group', xaxis_tickangle=-45)  
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    fig = px.bar(month_data, x='sale_month', y='ppsf', color='sale_month', barmode='group', title='Average Price ppsf by Month')
    fig.update_layout(
      xaxis_title="Month",
      yaxis_title="Average Price ppsf",
      legend_title="Month",
      font=dict(
          family="Courier New, monospace",
          size=12,
          color="RebeccaPurple"
      )
    )
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
  
  
def dashboard_monthly():
  data = load_data()
  st.title("CR Report")
  st.subheader('Dashboard Monthly/Qurterly Report Condo/Coop by Metro Group') 
  
  # choose between monthly or quarterly report
  st.sidebar.subheader('Select Report Type')
  report_type = st.sidebar.radio('Report Type', ['Monthly', 'Quarterly'])
  # sidebar for month and year
  st.sidebar.subheader('Select Year')
  year_input = st.sidebar.slider('Year', 2013, default_year, 2023)
  st.sidebar.subheader('Select Metro')
  metro_unique = data['metro'].unique()
  # remove QN, SI and BX and Nan
  metro_unique = metro_unique[metro_unique != 'QN']
  # drop nan values
  metro_unique = metro_unique[~pd.isna(metro_unique)]
  # sort the metro in order
  metro_unique = np.sort(metro_unique)
  metro_input = st.sidebar.selectbox("Select Metro:", options=list(metro_unique), index=1)
  if report_type == 'Monthly':  
    # sidebar select month
    st.sidebar.subheader('Select Month')
    unique_month = data['sale_month'].unique()
    unique_month = np.sort(unique_month)
    # find the index of the current month
    month_input = st.sidebar.selectbox("Select Month:", options=list(unique_month), index=default_month - 3)
    # make a copy of the dataframe
    blgtype_unique = data['bldg_type'].unique()
    # remove none values
    blgtype_unique = blgtype_unique[~pd.isna(blgtype_unique)]
    # sort the month in order
    blgtype_unique = sorted(blgtype_unique)
    #st.write(blgtype_unique)
    # sort the month in order
    #blgtype_unique = sorted(blgtype_unique)
    blgtype_input = st.sidebar.multiselect("Select Building Type:", list(blgtype_unique), default=list(blgtype_unique)) 
    
    #st.write(blgtype_input)
    
    new_df = data.copy()
    # filter data base on year, metro and month
    new_df = new_df[new_df['metro'] == metro_input]
    new_df = new_df[new_df['sale_year'] == year_input]
    new_df = new_df[new_df['sale_month'] == month_input]
    # filter by building type from list of building type selected
    new_df = new_df[new_df['bldg_type'].isin(blgtype_input)]
    
    cols = st.columns(4)
    
    with cols[0]:
      total_sales = new_df['sale_price'].count()
      st.metric(label='Total Sales', value=f"{format(total_sales, ',d')}")
    with cols[1]:
      avg_sale_price = round(new_df['sale_price'].mean(), 0)
      # convert to int and format with comma
      avg_sale_price = format(int(avg_sale_price), ',d')
      st.metric(label='Average Sale Price', value=f"${avg_sale_price}")
    with cols[2]:
      avg_ppsf = round(new_df['ppsf'].mean(), 2)
      avg_ppsf = format(int(avg_ppsf), ',d')
      st.metric(label='Average Price ppsf', value=f"${avg_ppsf}")
    with cols[3]:
      # gross sales amount
      gross_sales = round(new_df['sale_price'].sum(), 0)
      gross_sales = format(int(gross_sales), ',d')
      # change the format to billions
      #gross_sales = change_to_billions(gross_sales, 0)
      st.metric(label='Gross Sales Amount', value=f"${gross_sales}")
      
    cols = st.columns(2)
    # show the top 10 buildings by gross sales amount and average sale price, ppsf and count of sales. If count is less than 3 do not show
    # filter the dataframe by address and bldg_type only condos
    top10 = new_df.groupby(['address', 'bldg_type']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    top10 = top10.reset_index()
    # rename the columns
    top10.columns = ['address', 'bldg_type', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # filter the dataframe by count greater than 3
    top10 = top10[top10['count'] > 2]
    # sort the dataframe by gross sales amount
    top10 = top10.sort_values(by=['gross_sales'], ascending=False)
    # get the top 10 buildings
    top10 = top10.head(10)
    
    #st.write(top10, use_container_width=True)
    
    # add a column to the dataframe with the rank
    top10['rank'] = top10['gross_sales'].rank(ascending=False)
    
    with cols[0]:
      st.subheader('Top 10 Buildings by Sale Price')
      st.dataframe(top10, use_container_width=True)
      
    # most expensive sales of the month
    most_expensive = new_df[['address', 'bldg_type', 'sale_price', 'ppsf']]
    # sort the dataframe by sale price
    most_expensive = most_expensive.sort_values(by=['sale_price'], ascending=False)
    # get the top 10 buildings
    most_expensive = most_expensive.head(10)
    # add a column to the dataframe with the rank
    most_expensive['rank'] = most_expensive['sale_price'].rank(ascending=False)
    
    with cols[1]:
      st.subheader('Most Expensive Buildings by Sale Price')
      st.dataframe(most_expensive, use_container_width=True)
  else:
    # sidebar select quarter
    st.sidebar.subheader('Select Quarter')
    unique_quarter = data['sale_quarter'].unique()
    unique_quarter = np.sort(unique_quarter)
    quarter_input = st.sidebar.selectbox("Select Quarter:", options=list(unique_quarter), index=default_quarter - 2)
    # make a copy of the dataframe
    blgtype_unique = data['bldg_type'].unique()
    # remove none values
    blgtype_unique = blgtype_unique[~pd.isna(blgtype_unique)]
    # sort the month in order
    blgtype_unique = sorted(blgtype_unique)
    #st.write(blgtype_unique)
    # sort the month in order
    #blgtype_unique = sorted(blgtype_unique)
    blgtype_input = st.sidebar.multiselect("Select Building Type:", list(blgtype_unique), default=list(blgtype_unique))
    
    new_df = data.copy()
    # filter data base on year, metro and quarter
    new_df = new_df[new_df['metro'] == metro_input]
    new_df = new_df[new_df['sale_year'] == year_input]
    new_df = new_df[new_df['sale_quarter'] == quarter_input]
    # filter by building type from list of building type selected
    new_df = new_df[new_df['bldg_type'].isin(blgtype_input)]
    
    # last year same quarter data
    previouse_year = year_input - 1
    previouse_year_df = data.copy()
    # filter data base on year, metro and quarter
    previouse_year_df = previouse_year_df[previouse_year_df['metro'] == metro_input]
    previouse_year_df = previouse_year_df[previouse_year_df['sale_year'] == previouse_year]
    previouse_year_df = previouse_year_df[previouse_year_df['sale_quarter'] == quarter_input]
    # filter by building type from list of building type selected
    previouse_year_df = previouse_year_df[previouse_year_df['bldg_type'].isin(blgtype_input)]
    
    # show the metrics for both building types condo and coop dont use the input user
    st.subheader('Condo/Coop Metrics')
    cols = st.columns(4)
    with cols[0]:
      total_sales = new_df['sale_price'].count()
      total_sales_prev = previouse_year_df['sale_price'].count()
      delta1 = round((int(total_sales) - int(total_sales_prev)) / int(total_sales_prev) * 100, 2)
      st.metric(label='Total Sales', value=f"{format(total_sales, ',d')}", delta=f"{delta1}% pv total sales of {format(total_sales_prev, ',d')}")
    with cols[1]:
      avg_sale_price = round(new_df['sale_price'].mean(), 0)
      avg_sale_price_prev = round(previouse_year_df['sale_price'].mean(), 0)
      delta2 = round((int(avg_sale_price) - int(avg_sale_price_prev)) / int(avg_sale_price_prev) * 100, 2)
      avg_sale_price = format(int(avg_sale_price), ',d')
      avg_sale_price_prev = format(int(avg_sale_price_prev), ',d')
      st.metric(label='Average Sale Price', value=f"${avg_sale_price}", delta=f"{delta2}% pv average sale price of ${avg_sale_price_prev}")
    with cols[2]:
      avg_ppsf = round(new_df['ppsf'].mean(), 2)
      avg_ppsf_prev = round(previouse_year_df['ppsf'].mean(), 2)
      delta3 = round((int(avg_ppsf) - int(avg_ppsf_prev)) / int(avg_ppsf_prev) * 100, 2)
      avg_ppsf = format(int(avg_ppsf), ',d')
      avg_ppsf_prev = format(int(avg_ppsf_prev), ',d')
      st.metric(label='Average Price ppsf', value=f"${avg_ppsf}", delta=f"{delta3}% pv average price ppsf of ${avg_ppsf_prev}")
    with cols[3]:
      # gross sales amount
      gross_sales = round(new_df['sale_price'].sum(), 0)
      gross_sales_prev = round(previouse_year_df['sale_price'].sum(), 0)
      delta4 = round((int(gross_sales) - int(gross_sales_prev)) / int(gross_sales_prev) * 100, 2)
      gross_sales = format(int(gross_sales), ',d')
      gross_sales_prev = format(int(gross_sales_prev), ',d')
      # change the format to billions
      #gross_sales = change_to_billions(gross_sales, 0)
      st.metric(label='Gross Sales Amount', value=f"${gross_sales}", delta=f"{delta4}% pv gross sales amount of ${gross_sales_prev}")
      
    # show the metrics for the quarter by each building type according to blgtype_input selected by the user if condo, coop or condop
    condo = new_df[new_df['bldg_type'] == 'condo']
    previouse_year_condo = previouse_year_df[previouse_year_df['bldg_type'] == 'condo']
    if 'condo' in blgtype_input:
      # create the metrics for condo
      st.subheader('Condo Metrics')
      cols = st.columns(4)
      with cols[0]:
        total_sales = condo['sale_price'].count()
        total_sales_prev = previouse_year_condo['sale_price'].count()
        delta1 = round((int(total_sales) - int(total_sales_prev)) / int(total_sales_prev) * 100, 2)
        st.metric(label='Total Sales', value=f"{format(total_sales, ',d')}", delta=f"{delta1}% pv total sales of {format(total_sales_prev, ',d')}")
      with cols[1]:
        avg_sale_price = round(condo['sale_price'].mean(), 0)
        avg_sale_price_prev = round(previouse_year_condo['sale_price'].mean(), 0)
        delta2 = round((avg_sale_price - avg_sale_price_prev) / avg_sale_price_prev * 100, 2)
        avg_sale_price = format(int(avg_sale_price), ',d')
        avg_sale_price_prev = format(int(avg_sale_price_prev), ',d')
        st.metric(label='Average Sale Price', value=f"${avg_sale_price}", delta=f"{delta2}% pv average sale price of ${avg_sale_price_prev}")
      with cols[2]:
        avg_ppsf = round(condo['ppsf'].mean(), 2)
        avg_ppsf_prev = round(previouse_year_condo['ppsf'].mean(), 2)
        delta3 = round((avg_ppsf - avg_ppsf_prev) / avg_ppsf_prev * 100, 2)
        avg_ppsf = format(int(avg_ppsf), ',d')
        avg_ppsf_prev = format(int(avg_ppsf_prev), ',d')
        st.metric(label='Average Price ppsf', value=f"${avg_ppsf}", delta=f"{delta3}% pv average price ppsf of ${avg_ppsf_prev}")
      with cols[3]:
        # gross sales amount
        gross_sales = round(condo['sale_price'].sum(), 0)
        gross_sales_prev = round(previouse_year_condo['sale_price'].sum(), 0)
        delta4 = round((int(gross_sales) - int(gross_sales_prev)) / int(gross_sales_prev) * 100, 2)
        gross_sales = format(int(gross_sales), ',d')
        gross_sales_prev = format(int(gross_sales_prev), ',d')
        st.metric(label='Gross Sales Amount', value=f"${gross_sales}", delta=f"{delta4}% pv gross sales amount of ${gross_sales_prev}")
        
    coop = new_df[new_df['bldg_type'] == 'coop']
    coop_prev = previouse_year_df[previouse_year_df['bldg_type'] == 'coop']
    if 'coop' in blgtype_input:
      # create the metrics for coop
      st.subheader('Coop Metrics')
      cols = st.columns(3)
      with cols[0]:
        total_sales = coop['sale_price'].count()
        total_sales_prev = coop_prev['sale_price'].count()
        delta1 = round((int(total_sales) - int(total_sales_prev)) / int(total_sales_prev) * 100, 2)
        st.metric(label='Total Sales', value=f"{format(total_sales, ',d')}", delta=f"{delta1}% pv total sales of {format(total_sales_prev, ',d')}")
      with cols[1]:
        avg_sale_price = round(coop['sale_price'].mean(), 0)
        avg_sale_price_prev = round(coop_prev['sale_price'].mean(), 0)
        delta2 = round((avg_sale_price - avg_sale_price_prev) / avg_sale_price_prev * 100, 2)
        avg_sale_price = format(int(avg_sale_price), ',d')
        avg_sale_price_prev = format(int(avg_sale_price_prev), ',d')
        st.metric(label='Average Sale Price', value=f"${avg_sale_price}", delta=f"{delta2}% pv average sale price of ${avg_sale_price_prev}")
      #with cols[2]:
      #  avg_ppsf = round(coop['ppsf'].mean(), 2)
      #  avg_ppsf = format(int(avg_ppsf), ',d')
      #  st.metric(label='Average Price ppsf', value=f"${avg_ppsf}")
      with cols[2]:
        # gross sales amount
        gross_sales = round(coop['sale_price'].sum(), 0)
        # change the format to billions
        #gross_sales = change_to_billions(gross_sales, 0)
        gross_sales_prev = round(coop_prev['sale_price'].sum(), 0)
        delta4 = round((int(gross_sales) - int(gross_sales_prev)) / int(gross_sales_prev) * 100, 2)
        gross_sales = format(int(gross_sales), ',d')
        gross_sales_prev = format(int(gross_sales_prev), ',d')
        st.metric(label='Gross Sales Amount', value=f"${gross_sales}", delta=f"{delta4}% pv gross sales amount of ${gross_sales_prev}")
        
      
    cols = st.columns(2)
    # show the top 10 buildings by gross sales amount and average sale price, ppsf and count of sales. If count is less than 3 do not show
    # filter the dataframe by address and bldg_type only condos
    top10 = new_df.groupby(['address', 'bldg_type']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    top10 = top10.reset_index()
    # rename the columns
    top10.columns = ['address', 'bldg_type', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # filter the dataframe by count greater than 3
    top10 = top10[top10['count'] > 2]
    # sort the dataframe by gross sales amount
    top10 = top10.sort_values(by=['gross_sales'], ascending=False)
    # get the top 10 buildings
    top10 = top10.head(10)
    
    #st.write(top10, use_container_width=True)
    with cols[0]:
      st.subheader('Top 10 Buildings by Sale Price')
      st.dataframe(top10, use_container_width=True)
      
    # most expensive sales of the month
    most_expensive = new_df[['address', 'bldg_type', 'sale_price', 'ppsf']]
    # sort the dataframe by sale price
    most_expensive = most_expensive.sort_values(by=['sale_price'], ascending=False)
    # get the top 10 buildings
    most_expensive = most_expensive.head(10)
    # add a column to the dataframe with the rank
    most_expensive['rank'] = most_expensive['sale_price'].rank(ascending=False)
    
    with cols[1]:
      st.subheader('Most Expensive Buildings by Sale Price')
      st.dataframe(most_expensive, use_container_width=True)
      
    #  create pivottable dataframe based of rolling 4 quarters of data based on the quarter selected take into account a rolling 4 quarters of data for the year selected and previous year
    # example if the user selects 2021 Q1 the dataframe will be 2020 Q1, 2020 Q2, 2020 Q3, 2020 Q4, 2021 Q1
    # filter the dataframe by metro and year
    rolling_df = data.copy()
    rolling_df = rolling_df[rolling_df['metro'] == metro_input]
    rolling_df = rolling_df[rolling_df['sale_year'] <= year_input]
    # filter by building type from list of building type selected
    rolling_df = rolling_df[rolling_df['bldg_type'].isin(blgtype_input)]
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    rolling_df = rolling_df.groupby(['sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    rolling_df = rolling_df.reset_index()
    # rename the columns
    rolling_df.columns = ['sale_year', 'sale_quarter', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # calculate the max year in the dataframe
    #rolling_df = rolling_df[rolling_df['sale_quarter'] == quarter_input].loc[-1:]
    rolling_df = rolling_df[(rolling_df['sale_year'] == year_input - 1 )   | (rolling_df['sale_year'] == year_input) | (rolling_df['sale_year'] == year_input - 2 ) | (rolling_df['sale_year'] == year_input - 3 ) ]
    
    rolling_df['year_quarter'] = rolling_df['sale_year'].astype(str) + '-Q' + rolling_df['sale_quarter'].astype(str)
    # remove the first 2 row and 2 last rows
    if quarter_input == 1:
      rolling_df = rolling_df.iloc[1:-3]
    elif quarter_input == 2:
      rolling_df = rolling_df.iloc[2:-2]
    elif quarter_input == 3:
      rolling_df = rolling_df.iloc[3:-1]
    else:
      rolling_df = rolling_df.iloc[4:]
    
    st.subheader('Average Sale Price and Price ppsf by Quarter')
    st.dataframe(rolling_df, use_container_width=True)
    
    cols = st.columns(2)
    with cols[0]:
      # plot average sale price by year and metro group by bldg_type different colors
      max_count = rolling_df['count'].max()
      max_gross_sales = rolling_df['gross_sales'].max()
      fig = go.Figure(
        data=go.Bar(
          x=rolling_df['year_quarter'], 
          y=rolling_df['gross_sales'],
          marker=dict(color="paleturquoise"),
          name='Gross Sales Amount'
        )
      )
      
      fig.add_trace(
        go.Scatter(
          x=rolling_df['year_quarter'],
          y=rolling_df['count'],
          yaxis='y2',
          #mode='lines+markers',
          name='Count of Sales',
          marker=dict(color="crimson"),
        )
      )
      
      fig.update_layout(
        legend=dict(orientation="h"),
        yaxis=dict(
          title=dict(text='Gross Sales Amount'),
          titlefont_size=16,
          tickfont_size=14,
          side='left',
          range=[0, max_gross_sales + 100000000]
        ),
        yaxis2=dict(
          title=dict(text='Count of Sales'),
          titlefont_size=16,
          tickfont_size=14,
          side='right',
          overlaying='y',
          tickformat=',d',
          tickmode='sync',
          range=[0, max_count + 100]
        ),
        
        #barmode='group',
        
        )
      
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
      
      
    with cols[1]:
      max_avg_sale_price = rolling_df['avg_sale_price'].max()
      max_avg_ppsf = rolling_df['avg_ppsf'].max()
      # plot average sale price by year and metro group by bldg_type different colors
      fig = go.Figure(
        data=go.Bar(
          x=rolling_df['year_quarter'], 
          y=rolling_df['avg_sale_price'],
          marker=dict(color="lavender"),
          name='Average Sale Price'
        )
      )
      
      fig.add_trace(
        go.Scatter(
          x=rolling_df['year_quarter'],
          y=rolling_df['avg_ppsf'],
          yaxis='y2',
          name='Average Price ppsf',
          marker=dict(color="mediumaquamarine"),
        )
      )
      
      fig.update_layout(
        legend=dict(orientation="h"),
        yaxis=dict(
          title=dict(text='Average Sale Price'),
          titlefont_size=16,
          tickfont_size=14,
          side='left',
          range=[0, max_avg_sale_price + 100000]
        ),
        yaxis2=dict(
          title='Average Price ppsf',
          titlefont_size=16,
          tickfont_size=14,
          side='right',
          overlaying='y',
          range=[0, max_avg_ppsf + 100],
          tickmode='sync',
        ),
        )
        
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    st.subheader('Quarterly Total Condo Sales by Region')
    
    # get the total sales by metro and year and quarter
    metro_df = data.copy()
    # filter data base on year, metro and quarter
    metro_df = metro_df[metro_df['metro'] == metro_input]
    metro_df = metro_df[metro_df['sale_year'] == year_input]
    metro_df = metro_df[metro_df['sale_quarter'] == quarter_input]
    # filter by building only condos
    metro_df = metro_df[metro_df['bldg_type'] == 'condo']
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    metro_df = metro_df.groupby(['metro', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    metro_df = metro_df.reset_index()
    
    # Remove UPM
    metro_df = metro_df[metro_df['metro'] != 'UPM']
    
    # rename the columns
    metro_df.columns = ['metro','sale_year', 'sale_quarter' ,'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # get the total sales by metro and year and quarter
    metro_df_prev = data.copy()
    # filter data base on year, metro and quarter
    metro_df_prev = metro_df_prev[metro_df_prev['metro'] == metro_input]
    metro_df_prev = metro_df_prev[metro_df_prev['sale_year'] == year_input - 1]
    metro_df_prev = metro_df_prev[metro_df_prev['sale_quarter'] == quarter_input]
    # filter by building only condos
    metro_df_prev = metro_df_prev[metro_df_prev['bldg_type'] == 'condo']
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    metro_df_prev = metro_df_prev.groupby(['metro', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    metro_df_prev = metro_df_prev.reset_index()
    
    # Remove UPM
    metro_df_prev = metro_df_prev[metro_df_prev['metro'] != 'UPM']
    
    # rename the columns
    metro_df_prev.columns = ['metro', 'sale_year', 'sale_quarter','count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # concat the 2 dataframes
    metro_df = pd.concat([metro_df, metro_df_prev])
    
    # use AI to predict the next quarter
    metro_df1 = pd.concat([metro_df, metro_df_prev])
    metro_df1 = metro_df1.reset_index()
    metro_df1 = metro_df1.drop(columns=['index'])
    # sorted the dataframe by year and quarter
    
    metro_df1 = metro_df1.sort_values(by=['metro', 'sale_year', 'sale_quarter'])
    
    # sort the dataframe by sale year and quarter
    metro_df = metro_df.sort_values(by=['sale_year', 'sale_quarter'])
    st.dataframe(metro_df, use_container_width=True)
    metro_dict = {}
    
    for i, metro in enumerate(metro_df['metro'].unique()):
      change_count = round((metro_df[metro_df['metro'] == metro]['count'].iloc[1] - metro_df[metro_df['metro'] == metro]['count'].iloc[0]) / metro_df[metro_df['metro'] == metro]['count'].iloc[0] * 100, 2)
      change_gross_sales = round((metro_df[metro_df['metro'] == metro]['gross_sales'].iloc[1] - metro_df[metro_df['metro'] == metro]['gross_sales'].iloc[0]) / metro_df[metro_df['metro'] == metro]['gross_sales'].iloc[0] * 100, 2)
      change_ppsf = round((metro_df[metro_df['metro'] == metro]['avg_ppsf'].iloc[1] - metro_df[metro_df['metro'] == metro]['avg_ppsf'].iloc[0]) / metro_df[metro_df['metro'] == metro]['avg_ppsf'].iloc[0] * 100, 2)
      change_price = round((metro_df[metro_df['metro'] == metro]['avg_sale_price'].iloc[1] - metro_df[metro_df['metro'] == metro]['avg_sale_price'].iloc[0]) / metro_df[metro_df['metro'] == metro]['avg_sale_price'].iloc[0] * 100, 2)
      
      sentence = f'{metro} Q{quarter_input-1} {str(year_input)}' + ' vs ' + f'{metro} Q{quarter_input} {str(year_input)}'
      # join the strings 
      #setence = sentence + blur
      
      st.subheader(sentence)
      
      blur_1 = f""" Count of Sales: {format(metro_df[metro_df['metro'] == metro]['count'].iloc[0], ',d')} 
        vs {format(metro_df[metro_df['metro'] == metro]['count'].iloc[1], ',d')}
        Change over previous year: {change_count}%
      """
      blur_2 = f""" Gross Sales Amount: {format(int(metro_df[metro_df['metro'] == metro]['gross_sales'].iloc[0]), ',d')} vs {format(int(metro_df[metro_df['metro'] == metro]['gross_sales'].iloc[1]), ',d')}
        Change over previous year: {change_gross_sales}%
      """
      blur_3 = f" Average Price ppsf: {format(int(metro_df[metro_df['metro'] == metro]['avg_ppsf'].iloc[0]), ',d')} vs {format(int(metro_df[metro_df['metro'] == metro]['avg_ppsf'].iloc[1]), ',d')}"
      blur_4 = f" Average Sale Price: {format(int(metro_df[metro_df['metro'] == metro]['avg_sale_price'].iloc[0]), ',d')} vs {format(int(metro_df[metro_df['metro'] == metro]['avg_sale_price'].iloc[1]), ',d')}"
      
      metro_dict.update({metro: {
        'change_count': {
            'value': change_count,
            'change': f'{change_count}%',
            #f'count_{quarter_input}_{str(year_input)}': f'{format(metro_df[metro_df["metro"] == metro]["count"].iloc[0], ",d")}',
            # count of sales previous year same quarter
            #f'count_{quarter_input}_{str(year_input - 1)}': f'{format(metro_df[metro_df["metro"] == metro]["count"].iloc[1], ",d")}',
            f'sentence': f'{blur_1}',
        },
        'change_gross_sales': {
            'value': change_gross_sales,
            'delta': f'{change_gross_sales}%',
            f'gross_sales_{quarter_input}_{str(year_input)}': f'{format(metro_df[metro_df["metro"] == metro]["gross_sales"].iloc[0], ",d")}',
            # gross sales previous year same quarter
            f'gross_sales_{quarter_input}_{str(year_input - 1)}': f'{format(metro_df[metro_df["metro"] == metro]["gross_sales"].iloc[1], ",d")}',
            f'sentence': f'{blur_2}',
            
        },
        'change_ppsf': {
            'value': change_ppsf,
            'delta': f'{change_ppsf}%',
            f'ppsf_{quarter_input}_{str(year_input)}': f'{format(int(metro_df[metro_df["metro"] == metro]["avg_ppsf"].iloc[0]), ",d")}',
            # ppsf previous year same quarter
            f'ppsf_{quarter_input}_{str(year_input - 1)}': f'{format(int(metro_df[metro_df["metro"] == metro]["avg_ppsf"].iloc[1]), ",d")}',
            f'sentence': f'{blur_3}',
        },
        'change_price': {
            'value': change_price,
            'delta': f'{change_price}%',
            f'price_{quarter_input}_{str(year_input)}': f'{format(int(metro_df[metro_df["metro"] == metro]["avg_sale_price"].iloc[0]), ",d")}',
            # price previous year same quarter
            f'price_{quarter_input}_{str(year_input - 1)}': f'{format(int(metro_df[metro_df["metro"] == metro]["avg_sale_price"].iloc[1]), ",d")}',
            f'sentence': f'{blur_4}',
        }
      }})
      
    st.json(metro_dict)
    #st.dataframe(metro_df1, use_container_width=True)
    
    
    region_df = data.copy()
    # filter data base on year, metro and quarter
    region_df = region_df[region_df['metro'] == metro_input]
    region_df = region_df[region_df['sale_year'] == year_input]
    region_df = region_df[region_df['sale_quarter'] == quarter_input]
    # filter by building only condos
    region_df = region_df[region_df['bldg_type'] == 'condo']
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    region_df = region_df.groupby(['market', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    region_df = region_df.reset_index()
    
    # Remove UPM
    region_df = region_df[region_df['market'] != 'UPM']
    
    # rename the columns
    region_df.columns = ['market','sale_year', 'sale_quarter' ,'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    region_df_prev = data.copy()
    # filter data base on year, metro and quarter
    region_df_prev = region_df_prev[region_df_prev['metro'] == metro_input]
    region_df_prev = region_df_prev[region_df_prev['sale_year'] == year_input - 1]
    region_df_prev = region_df_prev[region_df_prev['sale_quarter'] == quarter_input]
    # filter by building only condos
    region_df_prev = region_df_prev[region_df_prev['bldg_type'] == 'condo']
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    region_df_prev = region_df_prev.groupby(['market', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    region_df_prev = region_df_prev.reset_index()
    
    # Remove UPM
    region_df_prev = region_df_prev[region_df_prev['market'] != 'UPM']
    
    # rename the columns
    region_df_prev.columns = ['market', 'sale_year', 'sale_quarter','count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # concat the 2 dataframes
    #region_df = pd.concat([region_df, region_df_prev])
    # use AI to predict the next quarter
    region_df1 = pd.concat([region_df, region_df_prev])
    region_df1 = region_df1.reset_index()
    region_df1 = region_df1.drop(columns=['index'])
    # sorted the dataframe by year and quarter
    region_df1 = region_df1.sort_values(by=['market', 'sale_year', 'sale_quarter'])
    # print market and count
    st.dataframe(region_df, use_container_width=True)
    #st.dataframe(region_df1, use_container_width=True)
    
    change_arr = {}
    
    for i, market in enumerate(region_df1['market'].unique()):
      change_count = round((region_df1[region_df1['market'] == market]['count'].iloc[1] - region_df1[region_df1['market'] == market]['count'].iloc[0]) / region_df1[region_df1['market'] == market]['count'].iloc[0] * 100, 2)
      change_gross_sales = round((region_df1[region_df1['market'] == market]['gross_sales'].iloc[1] - region_df1[region_df1['market'] == market]['gross_sales'].iloc[0]) / region_df1[region_df1['market'] == market]['gross_sales'].iloc[0] * 100, 2)
      change_ppsf = round((region_df1[region_df1['market'] == market]['avg_ppsf'].iloc[1] - region_df1[region_df1['market'] == market]['avg_ppsf'].iloc[0]) / region_df1[region_df1['market'] == market]['avg_ppsf'].iloc[0] * 100, 2)
      change_price = round((region_df1[region_df1['market'] == market]['avg_sale_price'].iloc[1] - region_df1[region_df1['market'] == market]['avg_sale_price'].iloc[0]) / region_df1[region_df1['market'] == market]['avg_sale_price'].iloc[0] * 100, 2)
      
      st.write(f'{market} change in sales count {change_count}%')  
      st.write(f'{market} change in gross sales {change_gross_sales}%')
      st.write(f'{market} change in price ppsf {change_ppsf}%')
      st.write(f'{market} change in price {change_price}%')
      
      # create a dictionary with the changes
      #change_arr[market] = [change_count, change_gross_sales, change_ppsf, change_price]
      change_arr.update({market: [{
        'change_count': change_count,
        'change_gross_sales': change_gross_sales,
        'change_ppsf': change_ppsf,
        'change_price': change_price
      }]})
      
    st.write(change_arr)
      
    st.dataframe(region_df1, use_container_width=True)
    
    cols = st.columns(2)
    
    with cols[0]:
      # pie chart of sales by region
      fig = px.pie(region_df, values='gross_sales', names='market', title='Sales by Region', color_discrete_sequence=px.colors.sequential.RdBu)
      fig.update_traces(textposition='inside', textinfo='percent+label')
      st.plotly_chart(fig, theme="streamlit", use_container_width=True)
      
    with cols[1]:
      # donut chart count of sales by region
      fig = px.scatter(region_df, x="market", y="count", size="count", color="market", hover_name="market", size_max=60)
      #fig.update_traces(textposition='inside', textinfo='percent+label')
      st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        
    # average price ppsf by region last 10 years
    year_df = data.copy()
    # filter data base on year, metro and quarter
    year_df = year_df[year_df['metro'] == metro_input]
    year_df = year_df[year_df['sale_year'] >= year_input - 10]
    # filter by building type from list of building type selected
    year_df = year_df[year_df['bldg_type'].isin(blgtype_input)]
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    year_df = year_df.groupby(['sale_year','sale_quarter', 'market']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    
    year_df = year_df.reset_index()
  
    # Remove UPM
    year_df = year_df[year_df['market'] != 'UPM']
    
    # rename the columns
    year_df.columns = ['sale_year', 'sale_quarter', 'market', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # concat the sale_year and sale_quarter
    year_df['year_quarter'] = year_df['sale_year'].astype(str) + '-Q' + year_df['sale_quarter'].astype(str)
    
    if quarter_input == 1:
      year_df = year_df.iloc[1*5:-3*5]
    elif quarter_input == 2:
      year_df = year_df.iloc[2*5:-2*5]
    elif quarter_input == 3:
      year_df = year_df.iloc[3*5:-1*5]
    else:
      year_df = year_df.iloc[4*5:]
    
    fig = px.line(year_df, x="year_quarter", y="avg_ppsf", color='market', title='Average Price ppsf by Region', symbol='market', color_discrete_sequence=px.colors.sequential.RdBu)
    
    fig.update_layout(
      #legend=dict(orientation="h"),
      yaxis=dict(
        title=dict(text='Average Price ppsf'),
        titlefont_size=16,
        tickfont_size=14,
        side='left',
        #range=[0, max_avg_sale_price + 100000]
      ),
      )
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    # summary market and submarket by quarter and quarter over quarter
    summary_df = data.copy()
    # filter data base on year, metro and quarter
    summary_df = summary_df[summary_df['metro'] == metro_input]
    summary_df = summary_df[summary_df['sale_year'] == year_input]
    summary_df = summary_df[summary_df['sale_quarter'] == quarter_input]
    # filter by building type from list of building type selected
    summary_df = summary_df[summary_df['bldg_type'].isin(blgtype_input)]
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    summary_df = summary_df.groupby(['market', 'submarket', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    summary_df = summary_df.reset_index()
    
    # Remove UPM
    summary_df = summary_df[summary_df['market'] != 'UPM']
    
    # rename the columns
    summary_df.columns = ['market', 'submarket', 'sale_year', 'sale_quarter', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    summary_last_year_df = data.copy()
    # filter data base on year, metro and quarter
    summary_last_year_df = summary_last_year_df[summary_last_year_df['metro'] == metro_input]
    summary_last_year_df = summary_last_year_df[summary_last_year_df['sale_year'] == year_input - 1]
    summary_last_year_df = summary_last_year_df[summary_last_year_df['sale_quarter'] == quarter_input]
    # filter by building type from list of building type selected
    summary_last_year_df = summary_last_year_df[summary_last_year_df['bldg_type'].isin(blgtype_input)]
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    summary_last_year_df = summary_last_year_df.groupby(['market', 'submarket', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    summary_last_year_df = summary_last_year_df.reset_index()
    
    # Remove UPM
    summary_last_year_df = summary_last_year_df[summary_last_year_df['market'] != 'UPM']
    
    # rename the columns
    summary_last_year_df.columns = ['market', 'submarket', 'sale_year', 'sale_quarter', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # concat the sale_year and sale_quarter
    summary_df['year_quarter'] = summary_df['sale_year'].astype(str) + '-Q' + summary_df['sale_quarter'].astype(str)
    
    #concat the sale_year and sale_quarter
    summary_last_year_df['year_quarter'] = summary_last_year_df['sale_year'].astype(str) + '-Q' + summary_last_year_df['sale_quarter'].astype(str)
    
    # concat both dataframes
    summary_df = pd.concat([summary_df, summary_last_year_df])
    
    # sort by submarket and year_quarter
    summary_df = summary_df.sort_values(by=['submarket', 'year_quarter'])
    
    unique_market = summary_df['market'].unique()
    
    st.dataframe(summary_df, use_container_width=True)
    
    for market in unique_market:
      data_table = []    
      # filter the dataframe by market
      market_df = summary_df[summary_df['market'] == market]
      
      # get the unique submarket
      unique_submarket = market_df['submarket'].unique()
      
      for i, submarket in enumerate(unique_submarket):
        try: 
          change_ppsf = round((market_df[market_df['submarket'] == submarket]['avg_ppsf'] - market_df[market_df['submarket'] == submarket]['avg_ppsf'].shift(1)) / market_df[market_df['submarket'] == submarket]['avg_ppsf'].shift(1) * 100, 2)
          change_avg_sale_price = round((market_df[market_df['submarket'] == submarket]['avg_sale_price'] - market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1)) / market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1) * 100, 2)
        except:
          # no change in percentage
          change_ppsf = "No Change PV"
          change_avg_sale_price = "No Change PV"
        try: 
          change_count = round((market_df[market_df['submarket'] == submarket]['count'] - market_df[market_df['submarket'] == submarket]['count'].shift(1)) / market_df[market_df['submarket'] == submarket]['count'].shift(1) * 100, 2)
          change_avg_sale_price = round((market_df[market_df['submarket'] == submarket]['avg_sale_price'] - market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1)) / market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1) * 100, 2)
        except:
          # no change in percentage
          change_count = "No Change PV"
          change_avg_sale_price = "No Change PV"
        count_sales = market_df[market_df['submarket'] == submarket]['count'].iloc[-1]
        price_ppsf = market_df[market_df['submarket'] == submarket]['avg_ppsf'].iloc[-1]
        price_avg_sale_price = market_df[market_df['submarket'] == submarket]['avg_sale_price'].iloc[-1]
        val_ppsf = format(int(price_ppsf), ',d')
        val_avg_sale_price = format(int(price_avg_sale_price), ',d')
        
        change_text0_pos = f'(<span style="color:green">{change_ppsf.iloc[-1]}%</span>)'
        change_text0_neg = f'(<span style="color:red">{change_ppsf.iloc[-1]}%</span>)'
        change_count_text0_pos = f'<span style="color:green">({change_count.iloc[-1]}%)</span>'
        change_count_text0_neg = f'<span style="color:red">({change_count.iloc[-1]}%)</span>'
        change_price_text1_pos = f'<span style="color:green">({change_avg_sale_price.iloc[-1]}%)</span>'
        change_price_text1_neg = f'<span style="color:red">({change_avg_sale_price.iloc[-1]}%)</span>'
        
        count_text0_pos = f'{count_sales}'
        count_text0_neg = f'{count_sales}'
        ppfs_text1_pos = f'{val_ppsf}'
        ppfs_text1_neg = f'{val_ppsf}'
        price_text1_pos = f'{val_avg_sale_price}'
        price_text1_neg = f'{val_avg_sale_price}'
        
        concat_ppsf_text0_pos = f'{count_text0_pos} {change_text0_pos}'
        concat_ppsf_text0_neg = f'{count_text0_neg} {change_text0_neg}'
        concat_count_text0_pos = f'{ppfs_text1_pos} {change_count_text0_pos}'
        concat_count_text0_neg = f'{ppfs_text1_neg} {change_count_text0_neg}'
        concat_price_text1_pos = f'{price_text1_pos} {change_price_text1_pos}'
        concat_price_text1_neg = f'{price_text1_neg} {change_price_text1_neg}'
        
        if change_ppsf.iloc[-1] > 0:
          data_table.append([submarket, concat_ppsf_text0_pos, concat_count_text0_pos, concat_price_text1_pos])
        else:
          data_table.append([submarket, concat_ppsf_text0_neg, concat_count_text0_neg, concat_price_text1_neg])
          
      # Determine the longest string in each column
      max_lengths = [max(len(str(row[i])) for row in data_table) for i in range(len(data_table[0]))]

      # Create formatted rows
      formatted_rows = []
      for row in data_table:
          formatted_row = "|".join([str(item).ljust(max_lengths[i]) for i, item in enumerate(row)])
          formatted_rows.append("| " + formatted_row + " |")

      # Combine rows into a single string
      formatted_table = "\n".join(formatted_rows)

      header = f"| {market} | Q{quarter_input} {year_input} PPSF Avg | Q{quarter_input} {year_input} Count of Sales | Q{quarter_input} {year_input} Price Avg |" 
      separator = "|:" + ":|:".join(["-" * length for length in max_lengths]) + ":|"

      # Complete Markdown table
      markdown_table = header + "\n" + separator + "\n" + formatted_table      
      st.subheader(f'{market} Metrics')
      st.markdown(markdown_table, unsafe_allow_html=True)
      
    # quarter over quarter change in count of sales, average price ppsf and average sale price
    quarter_change_df = data.copy()
    # filter market only manhattan
    #quarter_change_df = quarter_change_df[quarter_change_df['market'] == metro_input]
    # filter data base on year, metro and quarter
    quarter_change_df = quarter_change_df[quarter_change_df['sale_year'] == year_input]
    quarter_change_df = quarter_change_df[quarter_change_df['sale_quarter'] == quarter_input]
    # filter by building type only condos
    quarter_change_df = quarter_change_df[quarter_change_df['bldg_type'] == 'condo']
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    quarter_change_df = quarter_change_df.groupby(['market', 'submarket', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    quarter_change_df = quarter_change_df.reset_index()
    
    # Remove UPM
    quarter_change_df = quarter_change_df[quarter_change_df['market'] != 'UPM']
    
    # rename the columns
    quarter_change_df.columns = ['market', 'submarket', 'sale_year', 'sale_quarter', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # concat the sale_year and sale_quarter
    quarter_change_df['year_quarter'] = quarter_change_df['sale_year'].astype(str) + '-Q' + quarter_change_df['sale_quarter'].astype(str)
    
    # sort by submarket and year_quarter
    quarter_change_df = quarter_change_df.sort_values(by=['submarket', 'year_quarter'])
    
    # get the unique market
    unique_market = quarter_change_df['market'].unique()
    
    # last quarter same year data
    last_quarter_df = data.copy()
    # filter only metro manhattan
    #last_quarter_df = last_quarter_df[last_quarter_df['market'] == metro_input]
    # filter data base on year, metro and quarter
    last_quarter_df = last_quarter_df[last_quarter_df['sale_year'] == year_input]
    last_quarter_df = last_quarter_df[last_quarter_df['sale_quarter'] == quarter_input - 1]
    # filter by building type only condos
    last_quarter_df = last_quarter_df[last_quarter_df['bldg_type'] == 'condo']
    
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    last_quarter_df = last_quarter_df.groupby(['market', 'submarket', 'sale_year', 'sale_quarter']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    last_quarter_df = last_quarter_df.reset_index()
    
    # Remove UPM
    last_quarter_df = last_quarter_df[last_quarter_df['market'] != 'UPM']
    
    # rename the columns
    last_quarter_df.columns = ['market', 'submarket', 'sale_year', 'sale_quarter', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    
    # concat the sale_year and sale_quarter
    last_quarter_df['year_quarter'] = last_quarter_df['sale_year'].astype(str) + '-Q' + last_quarter_df['sale_quarter'].astype(str)
    
    # sort by submarket and year_quarter
    last_quarter_df = last_quarter_df.sort_values(by=['submarket', 'year_quarter'])
    
    # concat both dataframes
    quarter_change_df = pd.concat([quarter_change_df, last_quarter_df])
    
    # sort by submarket and year_quarter
    quarter_change_df = quarter_change_df.sort_values(by=['submarket', 'year_quarter'])
    # remove market Brooklyn
    quarter_change_df = quarter_change_df[quarter_change_df['market'] != 'Brooklyn']
    
    # get the unique market
    unique_market = quarter_change_df['market'].unique()
    
    st.dataframe(quarter_change_df, use_container_width=True)
    
    for i, market in enumerate(unique_market):
      data_table = []    
      # filter the dataframe by market
      market_df = quarter_change_df[quarter_change_df['market'] == market]
      
      # get the unique submarket
      unique_submarket = market_df['submarket'].unique()
      
      
      for i, submarket in enumerate(unique_submarket):
        try: 
          change_ppsf = round((market_df[market_df['submarket'] == submarket]['avg_ppsf'] - market_df[market_df['submarket'] == submarket]['avg_ppsf'].shift(1)) / market_df[market_df['submarket'] == submarket]['avg_ppsf'].shift(1) * 100, 2)
          change_avg_sale_price = round((market_df[market_df['submarket'] == submarket]['avg_sale_price'] - market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1)) / market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1) * 100, 2)
        except:
          # no change in
          change_ppsf = "No Change PV"
          change_avg_sale_price = "No Change PV"
        try:
          change_count = round((market_df[market_df['submarket'] == submarket]['count'] - market_df[market_df['submarket'] == submarket]['count'].shift(1)) / market_df[market_df['submarket'] == submarket]['count'].shift(1) * 100, 2)
          change_avg_sale_price = round((market_df[market_df['submarket'] == submarket]['avg_sale_price'] - market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1)) / market_df[market_df['submarket'] == submarket]['avg_sale_price'].shift(1) * 100, 2)
        except:
          # no change in
          change_count = "No Change PV"
          change_avg_sale_price = "No Change PV"
          
        count_sales = market_df[market_df['submarket'] == submarket]['count'].iloc[-1]
        price_ppsf = market_df[market_df['submarket'] == submarket]['avg_ppsf'].iloc[-1]
        price_avg_sale_price = market_df[market_df['submarket'] == submarket]['avg_sale_price'].iloc[-1]
        val_ppsf = format(int(price_ppsf), ',d')
        val_avg_sale_price = format(int(price_avg_sale_price), ',d')
        
        if change_ppsf.iloc[-1] > 0:
          change_text0_pos = f'(<span style="color:green">{change_ppsf.iloc[-1]}%</span>)'
        else:
          change_text0_neg = f'(<span style="color:red">{change_ppsf.iloc[-1]}%</span>)'
        if change_count.iloc[-1] > 0:
          change_count_text0_pos = f'<span style="color:green">({change_count.iloc[-1]}%)</span>'
        else:
          change_count_text0_neg = f'<span style="color:red">({change_count.iloc[-1]}%)</span>'
        if change_avg_sale_price.iloc[-1] > 0:
          change_price_text1_pos = f'<span style="color:green">({change_avg_sale_price.iloc[-1]}%)</span>'
        else:
          change_price_text1_neg = f'<span style="color:red">({change_avg_sale_price.iloc[-1]}%)</span>'
        
        count_text0_pos = f'{count_sales}'
        count_text0_neg = f'{count_sales}'
        ppfs_text1_pos = f'{val_ppsf}'
        ppfs_text1_neg = f'{val_ppsf}'
        price_text1_pos = f'{val_avg_sale_price}'
        price_text1_neg = f'{val_avg_sale_price}'
        
        concat_ppsf_text0_pos = f'{count_text0_pos} {change_text0_pos}'
        concat_ppsf_text0_neg = f'{count_text0_neg} {change_text0_neg}'
        concat_count_text0_pos = f'{ppfs_text1_pos} {change_count_text0_pos}'
        concat_count_text0_neg = f'{ppfs_text1_neg} {change_count_text0_neg}'
        concat_price_text1_pos = f'{price_text1_pos} {change_price_text1_pos}'
        concat_price_text1_neg = f'{price_text1_neg} {change_price_text1_neg}'
        
        if change_ppsf.iloc[-1] > 0:
          data_table.append([submarket, concat_ppsf_text0_pos, concat_count_text0_pos, concat_price_text1_pos])
        else:
          data_table.append([submarket, concat_ppsf_text0_neg, concat_count_text0_neg, concat_price_text1_neg])
          
      # Determine the longest string in each column
      max_lengths = [max(len(str(row[i])) for row in data_table) for i in range(len(data_table[0]))]
      
      # Create formatted rows
      formatted_rows = []
      
      for row in data_table:
          formatted_row = "|".join([str(item).ljust(max_lengths[i]) for i, item in enumerate(row)])
          formatted_rows.append("| " + formatted_row + " |")
          
      # Combine rows into a single string
      formatted_table = "\n".join(formatted_rows)
      
      header = f"| {market} | Q{quarter_input} {year_input} PPSF Avg | Q{quarter_input} {year_input} Count of Sales | Q{quarter_input} {year_input} Price Avg |"
      separator = "|:" + ":|:".join(["-" * length for length in max_lengths]) + ":|"
      
      # Complete Markdown table
      markdown_table = header + "\n" + separator + "\n" + formatted_table
      st.subheader(f'{market} Metrics')
      st.markdown(markdown_table, unsafe_allow_html=True)
      
    cols = st.columns(2)
    with cols[0]:
      # graph of average price ppsf by submarket
      
      fig = px.histogram(quarter_change_df, x="submarket", y="avg_sale_price", color="market", title='Average Price ppsf by Submarket', color_discrete_sequence=px.colors.sequential.RdBu, text_auto=".2s", marginal='box', hover_data=quarter_change_df.columns, barmode='group')
      fig.update_layout(
        #legend=dict(orientation="h"),
        yaxis=dict(
          title=dict(text='Average Price ppsf'),
          titlefont_size=16,
          tickfont_size=14,
          side='left',
          #range=[0, max_avg_sale_price + 100000]
        ),
        )
      
      st.plotly_chart(fig, theme="streamlit", use_container_width=True, height=600)
      
    # write the most expensive deals in Chelsea
    # filter the dataframe by market and submarket
    neighborhood_df = data.copy()
    # get only manhattan submarkets
    submarket_df = neighborhood_df[neighborhood_df['metro'] == 'Manhattan']
    submarket = st.multiselect('Select Submarket', sorted(submarket_df['submarket'].unique()), default=['Chelsea'])
    #chealsea_df = chealsea_df[chealsea_df['market'] == 'Chelsea']
    
    submarket_df = submarket_df[submarket_df['submarket'].isin(submarket)]
    # filter by building type from list of building type selected
    submarket_df = submarket_df[submarket_df['bldg_type'].isin(blgtype_input)]
    # filter by year
    submarket_df = submarket_df[submarket_df['sale_year'] == year_input]
    # filter by quarter
    submarket_df = submarket_df[submarket_df['sale_quarter'] == quarter_input]
    
    submarket_df = submarket_df.sort_values(by=['sale_price'], ascending=False)
    # get the top 25 sales
    submarket_df = submarket_df.head(25)
    
    st.subheader('Most Expensive Q3 2023 Sales by Neighborhood in Manhattan')
    st.dataframe(submarket_df, use_container_width=True)
    
            
          
if __name__ == "__main__":
  menu_items = ["Dashboard Yearly", "Dashboard Monthly","Market/SubMarket", "Neighborhood", "Other"]
  menu_icons = ['app', 'app', 'app', 'app', 'app']
  
  selected = option_menu("CR", menu_items,
      icons=menu_icons, menu_icon="cast", default_index=0, orientation="horizontal")
  if selected == "Dashboard Yearly":
    main()
  elif selected == "Dashboard Monthly":
    dashboard_monthly()
  

