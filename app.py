# import streamlit as st
# import yfinance as yf
# import pandas as pd
# import numpy as np
# import plotly.express as px
# from alpha_vantage.fundamentaldata import FundamentalData
# from stocknews import StockNews
# import datetime
# from config import ALPHA_VANTAGE_KEY

# # Page config
# st.set_page_config(page_title="Stock Dashboard", page_icon="📈")

# # Title
# st.title("Stock Dashboard")

# # Sidebar inputs
# ticker = st.sidebar.text_input("Ticker", value="AAPL")
# start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
# end_date = st.sidebar.date_input("End Date", value=datetime.date.today())

# # Load data
# @st.cache_data
# def load_data(ticker, start, end):
#     data = yf.download(ticker, start=start, end=end)
    
#     # Handle multi-level columns
#     if isinstance(data.columns, pd.MultiIndex):
#         data.columns = data.columns.droplevel(1)
    
#     # Ensure Adj Close exists (use Close if not available)
#     if 'Adj Close' not in data.columns and 'Close' in data.columns:
#         data['Adj Close'] = data['Close']
    
#     return data

# data = load_data(ticker, start_date, end_date)

# # Main chart
# fig = px.line(data, x=data.index, y='Adj Close', title=f'{ticker} Stock Price')
# st.plotly_chart(fig, use_container_width=True)

# # Tabs
# tab1, tab2, tab3 = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# # Tab 1: Pricing Data
# with tab1:
#     st.header("Price Movements")
    
#     data2 = data.copy()
#     data2['% Change'] = data2['Adj Close'] / data2['Adj Close'].shift(1) - 1
#     data2.dropna(inplace=True)
    
#     annual_return = data2['% Change'].mean() * 252 * 100
#     std_dev = np.std(data2['% Change']) * np.sqrt(252) * 100
#     risk_adj_return = annual_return / std_dev if std_dev != 0 else 0
    
#     st.write(f"Annual Return: {annual_return:.2f}%")
#     st.write(f"Standard Deviation: {std_dev:.2f}%")
#     st.write(f"Risk Adjusted Return: {risk_adj_return:.2f}")
    
#     st.dataframe(data2)

# # Tab 2: Fundamental Data
# with tab2:
#     st.header("Fundamental Data")
    
#     if ALPHA_VANTAGE_KEY != "YOUR_API_KEY_HERE":
#         try:
#             fd = FundamentalData(key=ALPHA_VANTAGE_KEY, output_format='pandas')
            
#             st.subheader("Balance Sheet")
#             balance_sheet, _ = fd.get_balance_sheet_annual(ticker)
#             st.dataframe(balance_sheet)
            
#             st.subheader("Income Statement")
#             income_statement, _ = fd.get_income_statement_annual(ticker)
#             st.dataframe(income_statement)
            
#             st.subheader("Cash Flow")
#             cash_flow, _ = fd.get_cash_flow_annual(ticker)
#             st.dataframe(cash_flow)
#         except Exception as e:
#             st.error(f"Error loading fundamental data. Please check your API key.")
#     else:
#         st.warning("Add API key in config.py")

# # Tab 3: News
# with tab3:
#     st.header(f"News of {ticker}")
    
#     try:
#         sn = StockNews(ticker, save_news=False)
#         df_news = sn.read_rss()
        
#         for i in range(min(10, len(df_news))):
#             st.subheader(f"News {i+1}")
#             st.write(f"Published: {df_news['published'].iloc[i]}")
#             st.write(f"Title: {df_news['title'].iloc[i]}")
#             st.write(f"Summary: {df_news['summary'].iloc[i]}")
            
#             # Color-coded sentiment
#             title_sentiment = df_news['sentiment_title'].iloc[i]
#             news_sentiment = df_news['sentiment_summary'].iloc[i]
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 if title_sentiment > 0:
#                     st.success(f"Title Sentiment: {title_sentiment:.2f} (Positive)")
#                 elif title_sentiment < 0:
#                     st.error(f"Title Sentiment: {title_sentiment:.2f} (Negative)")
#                 else:
#                     st.info(f"Title Sentiment: {title_sentiment:.2f} (Neutral)")
            
#             with col2:
#                 if news_sentiment > 0:
#                     st.success(f"News Sentiment: {news_sentiment:.2f} (Positive)")
#                 elif news_sentiment < 0:
#                     st.error(f"News Sentiment: {news_sentiment:.2f} (Negative)")
#                 else:
#                     st.info(f"News Sentiment: {news_sentiment:.2f} (Neutral)")
            
#             st.write("---")
#     except Exception as e:
#         st.error(f"Error loading news: {e}")






import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews
import datetime
from config import ALPHA_VANTAGE_KEY
import re

# Page config
st.set_page_config(page_title="Stock Dashboard", page_icon="📈")

# Title
st.title("Stock Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input("Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.date.today())

# Validation functions
def validate_ticker(ticker):
    """Validate ticker input"""
    if not ticker or ticker.strip() == "":
        return False, "Please enter a ticker symbol"
    
    ticker = ticker.strip().upper()
    
    # Check if ticker contains only letters and is reasonable length
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        return False, "Ticker should be 1-5 letters only (e.g., AAPL, MSFT)"
    
    return True, ticker

def validate_dates(start_date, end_date):
    """Validate date inputs"""
    if start_date >= end_date:
        return False, "Start date must be before end date"
    
    if end_date > datetime.date.today():
        return False, "End date cannot be in the future"
    
    # Check if date range is too short
    if (end_date - start_date).days < 7:
        return False, "Date range should be at least 7 days"
    
    return True, "Valid dates"

# Load data with comprehensive error handling
@st.cache_data
def load_data(ticker, start, end):
    try:
        # Validate inputs first
        is_valid_ticker, ticker_msg = validate_ticker(ticker)
        if not is_valid_ticker:
            return None, ticker_msg
        
        ticker = ticker_msg  # Use cleaned ticker
        
        is_valid_dates, date_msg = validate_dates(start, end)
        if not is_valid_dates:
            return None, date_msg
        
        # Download data
        data = yf.download(ticker, start=start, end=end, progress=False)
        
        # Check if data is empty
        if data.empty:
            return None, f"No data found for '{ticker}'. Please check if it's a valid stock symbol."
        
        # Handle multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        
        # Ensure Adj Close exists
        if 'Adj Close' not in data.columns and 'Close' in data.columns:
            data['Adj Close'] = data['Close']
        elif 'Adj Close' not in data.columns and 'Close' not in data.columns:
            return None, f"No price data available for '{ticker}'"
        
        return data, "Success"
        
    except Exception as e:
        error_msg = str(e)
        if "No data found" in error_msg:
            return None, f"'{ticker}' is not a valid ticker symbol"
        elif "No objects to concatenate" in error_msg:
            return None, f"No data available for '{ticker}' in the selected date range"
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            return None, "Network connection error. Please check your internet connection."
        else:
            return None, f"Error loading data for '{ticker}': Please try again"

# Load data
data, message = load_data(ticker, start_date, end_date)

# Check if data loaded successfully
if data is None:
    st.error(f"❌ {message}")
    st.info("💡 Try these popular tickers: AAPL, MSFT, GOOGL, TSLA, AMZN")
    st.stop()

# Success - show dashboard
st.success(f"✅ Data loaded successfully for {ticker.upper()}")

# Main chart
try:
    fig = px.line(data, x=data.index, y='Adj Close', title=f'{ticker.upper()} Stock Price')
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error("Error creating chart. Please try refreshing the page.")

# Tabs
tab1, tab2, tab3 = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# Tab 1: Pricing Data
with tab1:
    st.header("Price Movements")
    
    try:
        data2 = data.copy()
        data2['% Change'] = data2['Adj Close'] / data2['Adj Close'].shift(1) - 1
        data2.dropna(inplace=True)
        
        if len(data2) == 0:
            st.warning("Not enough data to calculate metrics")
        else:
            annual_return = data2['% Change'].mean() * 252 * 100
            std_dev = np.std(data2['% Change']) * np.sqrt(252) * 100
            risk_adj_return = annual_return / std_dev if std_dev != 0 else 0
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Annual Return", f"{annual_return:.2f}%")
            with col2:
                st.metric("Standard Deviation", f"{std_dev:.2f}%")
            with col3:
                st.metric("Risk Adjusted Return", f"{risk_adj_return:.2f}")
            
            st.dataframe(data2, use_container_width=True)
    except Exception as e:
        st.error("Error calculating price metrics")

# Tab 2: Fundamental Data
with tab2:
    st.header("Fundamental Data")
    
    if ALPHA_VANTAGE_KEY != "YOUR_API_KEY_HERE":
        try:
            with st.spinner("Loading fundamental data..."):
                fd = FundamentalData(key=ALPHA_VANTAGE_KEY, output_format='pandas')
                
                st.subheader("Balance Sheet")
                balance_sheet, _ = fd.get_balance_sheet_annual(ticker)
                st.dataframe(balance_sheet, use_container_width=True)
                
                st.subheader("Income Statement")
                income_statement, _ = fd.get_income_statement_annual(ticker)
                st.dataframe(income_statement, use_container_width=True)
                
                st.subheader("Cash Flow")
                cash_flow, _ = fd.get_cash_flow_annual(ticker)
                st.dataframe(cash_flow, use_container_width=True)
                
        except Exception as e:
            st.error("Unable to load fundamental data")
            st.info("This could be due to API rate limits or invalid ticker symbol")
    else:
        st.warning("⚠️ Alpha Vantage API key not configured!")
        st.info("Add your API key in config.py to view fundamental data")

# Tab 3: News
with tab3:
    st.header(f"News of {ticker.upper()}")
    
    try:
        with st.spinner("Loading latest news..."):
            sn = StockNews(ticker, save_news=False)
            df_news = sn.read_rss()
            
            if len(df_news) == 0:
                st.info(f"No recent news found for {ticker.upper()}")
            else:
                for i in range(min(10, len(df_news))):
                    st.subheader(f"📰 News {i+1}")
                    st.write(f"**Published:** {df_news['published'].iloc[i]}")
                    st.write(f"**Title:** {df_news['title'].iloc[i]}")
                    st.write(f"**Summary:** {df_news['summary'].iloc[i]}")
                    
                    # Color-coded sentiment
                    title_sentiment = df_news['sentiment_title'].iloc[i]
                    news_sentiment = df_news['sentiment_summary'].iloc[i]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if title_sentiment > 0:
                            st.success(f"Title Sentiment: {title_sentiment:.2f} (Positive)")
                        elif title_sentiment < 0:
                            st.error(f"Title Sentiment: {title_sentiment:.2f} (Negative)")
                        else:
                            st.info(f"Title Sentiment: {title_sentiment:.2f} (Neutral)")
                    
                    with col2:
                        if news_sentiment > 0:
                            st.success(f"News Sentiment: {news_sentiment:.2f} (Positive)")
                        elif news_sentiment < 0:
                            st.error(f"News Sentiment: {news_sentiment:.2f} (Negative)")
                        else:
                            st.info(f"News Sentiment: {news_sentiment:.2f} (Neutral)")
                    
                    st.write("---")
                    
    except Exception as e:
        st.error("Unable to load news data")
        st.info("This might be due to network issues or API limitations")

# Sidebar help
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Popular Tickers")
st.sidebar.markdown("**Tech:** AAPL, MSFT, GOOGL")
st.sidebar.markdown("**Auto:** TSLA, F, GM") 
st.sidebar.markdown("**Finance:** JPM, BAC, WFC")
st.sidebar.markdown("**ETFs:** SPY, QQQ, VTI")
