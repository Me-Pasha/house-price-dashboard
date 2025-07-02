import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(layout="wide")


df_main = pd.read_csv("kc_house_data.csv")
df_main['date'] = pd.to_datetime(df_main['date'], format='%Y%m%dT%H%M%S').dt.strftime('%Y-%m-%d')

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

#main dashboard
col = st.columns((1, 5, 5), gap='small')

with col[1]:
    st.write("# House Price Dashboard")
    st.write("Dataset contains house sale prices for King County, which includes Seattle")
    zipcodes = df_main["zipcode"].unique()
    data_view_options = np.insert(zipcodes.astype(str), 0, "Entire Dataset")
    data_view = st.selectbox("Select a zipcode: ", data_view_options)
    
    if data_view == "Entire Dataset":
        st.dataframe(df_main.drop("zipcode", axis=1))
    else:
        st.dataframe(df_main[df_main["zipcode"] == int(data_view)].reset_index().drop(["index", "zipcode"], axis=1))

    #street-map
    st.write("Location of each houses")
    fig = px.scatter_map(
    df_main,
    lat="lat",
    lon="long",
    zoom=8,
    height=500
    )

    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig)

with col[0]:
    if data_view == "Entire Dataset":
        st.metric("Highest Sale", format_number(df_main["price"].max()))
        st.metric("Average Sale", format_number(df_main["price"].mean()))
        st.metric("Lowest Sale", format_number(df_main["price"].min()))
        st.metric("Best Grade", df_main["grade"].max())
        st.metric("Best Condition", df_main["condition"].max())
    else:
        max_sale = df_main[df_main["zipcode"] == int(data_view)]["price"].max()
        st.metric("Highest Sale", format_number(max_sale))
        mean_sale = df_main[df_main["zipcode"] == int(data_view)]["price"].mean()
        st.metric("Average Sale", format_number(mean_sale))
        min_sale = df_main[df_main["zipcode"] == int(data_view)]["price"].min()
        st.metric("Lowest Sale", format_number(min_sale))
        st.metric("Best Grade", df_main[df_main["zipcode"] == int(data_view)]["grade"].max())
        st.metric("Best Condition", df_main[df_main["zipcode"] == int(data_view)]["condition"].max())
    
        

with col[2]:
    st.write("**Visualization for Analizing Trends in Data**")
    visual_options = st.selectbox("Select for visualization: ", ["Scatter Plot", "Bar Graph", "Heatmap", "Line Graph"])

    if visual_options == "Scatter Plot":
        scatter_fields = ['price', 'bedrooms', 'bathrooms', 'sqft_living',
       'sqft_lot', 'floors', 'waterfront', 'view', 'condition', 'grade',
       'sqft_above', 'sqft_basement', 'yr_built', 'yr_renovated','sqft_living15', 'sqft_lot15']
        x_scatter = st.selectbox("Select of X: ", scatter_fields)
        y_scatter = st.selectbox("Select of Y: ", scatter_fields)
        st.scatter_chart(df_main, x=x_scatter, y=y_scatter)

    elif visual_options == "Bar Graph":
        df_zipcode = pd.DataFrame()
        df_zipcode["zipcode"] = df_main["zipcode"].unique()
        max_per_zipcode = []
        min_per_zipcode = []
        avg_per_zipcode = []
        for zip in df_zipcode["zipcode"]:
            max_per_zipcode.append(df_main[df_main["zipcode"] == zip]["price"].max())
            min_per_zipcode.append(df_main[df_main["zipcode"] == zip]["price"].min())    
            avg_per_zipcode.append(df_main[df_main["zipcode"] == zip]["price"].mean())  
        df_zipcode["max_sale"] = max_per_zipcode
        df_zipcode["min_sale"] = min_per_zipcode
        df_zipcode["avg_sale"] = avg_per_zipcode
        df_zipcode['zipcode'] = df_zipcode['zipcode'].astype(str)
        fig = px.bar(df_zipcode, x='zipcode', y=['max_sale', 'min_sale', 'avg_sale'], barmode='group')
        fig.update_layout(
        xaxis_title='Zipcode',
        yaxis_title='Sale Price',
        legend_title='Sale Type',
        xaxis_tickangle=-45,  # rotate labels for clarity
        xaxis_ticktext=df_main['zipcode'].unique(),
        height=600,
        width=1000,
        template='plotly_dark'  # or 'plotly_white'
        )
        st.plotly_chart(fig)

    elif visual_options == "Heatmap":
        corr = df_main.drop(["zipcode", "id", "date", "lat", "long"], axis=1).corr()
        fig = px.imshow(corr, text_auto=True)
        st.plotly_chart(fig)
    
    elif visual_options == "Line Graph":
        df_date = pd.DataFrame()
        df_date["date"] = np.sort(df_main["date"].unique())
        sum_per_date = []
        for record in df_date["date"]:
            sum_per_date.append(df_main[df_main["date"] == record]["price"].sum())
        df_date["sum"] = sum_per_date  
        df_date['date'] = pd.to_datetime(df_date['date'])
        
        date_selected = st.selectbox("Select Date", ["Entire Dataset", "May 2014", "June 2014", "July 2014", "August 2014", "September 2014", "October 2014", "November 2014", "December 2014", "January 2015", "February 2015", "March 2015", "April 2015", "May 2015"]) 
        month_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        
        if date_selected == "Entire Dataset":
            fig = px.line(df_date, x="date", y = "sum")
            st.plotly_chart(fig)
        else:
            month, year = date_selected.split()
            month_num = month_dict[month]
            print(month_num)
            year = int(year)
            df_monthly = df_date[(df_date['date'].dt.year == year) & (df_date['date'].dt.month == month_num)]
            fig = px.line(df_monthly, x="date", y = "sum")
            st.plotly_chart(fig)


    with st.expander('About', expanded=True):
        st.write('''
            - Data: [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction).
            - :orange[**id**]: Unique ID for each home sold
            - :orange[**bedrooms**]: Number of bedrooms
            - :orange[**bathrooms**]: Number of bathrooms, where .5 accounts for a room with a toilet but no shower
            - :orange[**sqft_living**]: Square footage of the apartments interior living space
            - :orange[**sqft_lot**]: Square footage of the land space
            - :orange[**bathrooms**]: Number of bathrooms, where .5 accounts for a room with a toilet but no shower
            - :orange[**view**]: An index from 0 to 4 of how good the view of the property was
            - :orange[**condition**]: An index from 1 to 5 on the condition of the apartment
            - :orange[**grade**]: An index from 1 to 13, where 1-3 falls short of building construction and design, 7 has an average level of construction and design, and 11-13 have a high quality level of construction and design.
            - :orange[**sqft_above**]: The square footage of the interior housing space that is above ground level
            - :orange[**sqft_basement**]: The square footage of the interior housing space that is below ground level
            - :orange[**yr_built**]: The year the house was initially built
            - :orange[**yr_renovated**]: The year of the house’s last renovation
            - :orange[**sqft_living15**]: The square footage of interior housing living space for the nearest 15 neighbors
            - :orange[**sqft_lot15**]: The square footage of the land lots of the nearest 15 neighbors
            ''')




