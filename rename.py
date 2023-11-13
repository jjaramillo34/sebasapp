# rename the columns
    rolling_df.columns = ['sale_year', 'sale_quarter', 'bldg_type', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    # pivot the dataframe of rolling 4 quarters if the year is 2023 Q1 the dataframe will be 2022 Q1, 2022 Q2, 2022 Q3, 2022 Q4, 2023 Q1
    rolling_df = rolling_df.pivot_table(index=['sale_year', 'bldg_type'], columns='sale_quarter', values=['count', 'avg_sale_price', 'gross_sales', 'avg_ppsf'])
    rolling_df = rolling_df.reset_index()
    
    # rename the columns
    rolling_df.columns = ['sale_year', 'bldg_type', 'count_q1', 'count_q2', 'count_q3', 'count_q4', 'avg_sale_price_q1', 'avg_sale_price_q2', 'avg_sale_price_q3', 'avg_sale_price_q4', 'gross_sales_q1', 'gross_sales_q2', 'gross_sales_q3', 'gross_sales_q4', 'avg_ppsf_q1', 'avg_ppsf_q2', 'avg_ppsf_q3', 'avg_ppsf_q4']
    
    # filter the dataframe by the last 4 quarters based on the year selected by the user
    rolling_df = rolling_df[rolling_df['sale_year'] == year_input]
    # sort the dataframe by sale_year and bldg_type
    rolling_df = rolling_df.sort_values(by=['sale_year', 'bldg_type'], ascending=True)
    
    # create the previous year dataframe
    previouse_year_rolling_df = data.copy()
    previouse_year_rolling_df = previouse_year_rolling_df[previouse_year_rolling_df['metro'] == metro_input]
    previouse_year_rolling_df = previouse_year_rolling_df[previouse_year_rolling_df['sale_year'] <= previouse_year]
    # filter by building type from list of building type selected
    previouse_year_rolling_df = previouse_year_rolling_df[previouse_year_rolling_df['bldg_type'].isin(blgtype_input)]
    # create a pivot table based on quarter and year and bldg_type and sale_price and ppsf and count of sales and gross sales amount and average sale price
    previouse_year_rolling_df = previouse_year_rolling_df.groupby(['sale_year', 'sale_quarter', 'bldg_type']).agg({'sale_price': ['count', 'mean', 'sum'], 'ppsf': ['mean']})
    previouse_year_rolling_df = previouse_year_rolling_df.reset_index()
    
    # rename the columns
    previouse_year_rolling_df.columns = ['sale_year', 'sale_quarter', 'bldg_type', 'count', 'avg_sale_price', 'gross_sales', 'avg_ppsf']
    # pivot the dataframe of rolling 4 quarters if the year is 2023 Q1 the dataframe will be 2022 Q1, 2022 Q2, 2022 Q3, 2022 Q4, 2023 Q1
    previouse_year_rolling_df = previouse_year_rolling_df.pivot_table(index=['sale_year', 'bldg_type'], columns='sale_quarter', values=['count', 'avg_sale_price', 'gross_sales', 'avg_ppsf'])
    previouse_year_rolling_df = previouse_year_rolling_df.reset_index()
    
    # rename the columns
    previouse_year_rolling_df.columns = ['sale_year', 'bldg_type', 'count_q1', 'count_q2', 'count_q3', 'count_q4', 'avg_sale_price_q1', 'avg_sale_price_q2', 'avg_sale_price_q3', 'avg_sale_price_q4', 'gross_sales_q1', 'gross_sales_q2', 'gross_sales_q3', 'gross_sales_q4', 'avg_ppsf_q1', 'avg_ppsf_q2', 'avg_ppsf_q3', 'avg_ppsf_q4']
    
    # filter the dataframe by the last 4 quarters based on the year selected by the user
    previouse_year_rolling_df = previouse_year_rolling_df[previouse_year_rolling_df['sale_year'] == previouse_year]
    # sort the dataframe by sale_year and bldg_type
    previouse_year_rolling_df = previouse_year_rolling_df.sort_values(by=['sale_year', 'bldg_type'], ascending=True)
    
    # concat the rolling_df and previouse_year_rolling_df
    rolling_df = pd.concat([rolling_df, previouse_year_rolling_df])
    
    st.columns(2)
    # plot the rolling 4 quarters of data
    with cols[0]:
      fig = px.bar(rolling_df, x='sale_year', y='avg_sale_price_q1', color='bldg_type', barmode='group', title='Average Sale Price by Quarter')
      fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Average Sale Price",
        legend_title="Building Type",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        )
      )
      
      st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    with cols[1]:
      fig = px.bar(rolling_df, x='sale_year', y='avg_ppsf_q1', color='bldg_type', barmode='group', title='Average Price ppsf by Quarter')
      fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Average Price ppsf",
        legend_title="Building Type",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        )
      )
      
      st.plotly_chart(fig, theme="streamlit", use_container_width=True)
      
    cols = st.columns(2)
    with cols[0]:
      fig = px.bar(rolling_df, x='sale_year', y='gross_sales_q1', color='bldg_type', barmode='group', title='Gross Sales Amount by Quarter')
      fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Gross Sales Amount",
        legend_title="Building Type",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        )
      )
      
      st.plotly_chart(fig, theme="streamlit", use_container_width=True)