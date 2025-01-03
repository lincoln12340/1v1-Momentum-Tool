import streamlit as st
import yfinance as yf
import pandas_ta as ta
from openai import OpenAI
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import tempfile
import json
from pydantic import BaseModel
import os 
import re
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
google_sheet_url = os.getenv("GOOGLE_SHEET_URL")
private_key = os.getenv("PRIVATE_KEY")
project_id = os.getenv("PROJECT_ID")
private_key_id = os.getenv("PRIVATE_KEY_ID")
client_email = os.getenv("CLIENT_EMAIL")
client_id = os.getenv("CLIENT_ID")
auth_uri = os.getenv("AUTH_URI")
token_uri = os.getenv("TOKEN_URI")
auth_provider_x509_cert_url = os.getenv("AUTH_PROVIDER_X509_CERT_URL")
client_x509_cert_url = os.getenv("CLIENT_X509_CERT_URL")
universe_domain = os.getenv("UNIVERSE_DOMAIN")
type_sa = os.getenv("TYPE")

print(api_key)

client = OpenAI(api_key= api_key)



def stock_page():
    #client = OpenAI(api_key=api_key)

    if "run_analysis_complete" not in st.session_state:
        st.session_state["run_analysis_complete"] = False

# Main application
    #st.set_page_config(page_title="Stock Market Analysis", layout="wide", page_icon="📈")

    # Sidebar with interactive options
    with st.sidebar:
        st.title("Market Analysis Dashboard")
        st.markdown("Analyze stock trends using advanced technical indicators powered by AI.")


        st.subheader("Company 1")
        ticker = st.text_input(" Enter Ticker Symbol", "", help="Example: 'AAPL' for Apple Inc.")
        company = st.text_input(" Enter Full Company Name", "", help="Example: 'Apple Inc.'")

        st.subheader("Company 2")
        ticker_2 = st.text_input("Enter Ticker Symbol for Company 2", "", help="e.g., 'MSFT'")
        company_2 = st.text_input("Enter Full Company Name for Company 2", "", help="e.g., 'Microsoft Corp.'")
        
        # Timeframe Selection
        st.subheader("Select Timeframe for Analysis")
        timeframe = st.radio(
            "Choose timeframe:",
            ( "3 Months", "6 Months", "1 Year"),
            index=2,
            help="Select the period of historical data for the stock analysis"
        )
        
        # Analysis Type Selection
        st.subheader("Analysis Options")
        technical_analysis = st.checkbox("Technical Analysis", help="Select to run technical analysis indicators")
        news_and_events = st.checkbox("News and Events", help="Get recent news and event analysis for the company")
        fundamental_analysis = st.checkbox("Fundamental Analysis", help="Select to upload a file for fundamental analysis")

        uploaded_file = None
        uploaded_file2 = None
        if fundamental_analysis:
            uploaded_file = st.file_uploader("Upload 1st PDF file for Fundamental Analysis", type="pdf")
            uploaded_file2 = st.file_uploader("Upload 2nd PDF file for Fundamental Analysis", type="pdf")

        

        
        # Run Button with styled alert text
        run_button = st.button("Run Analysis")
        st.markdown("---")
        st.info("Click 'Run Analysis' after selecting options to start.")


    col1, col2 = st.columns([3, 1])

    
    st.title("Stock Market Analysis with AI-Powered Insights")
    st.markdown("**Gain actionable insights into stock trends with advanced indicators and AI interpretations.**")

    progress_bar = st.progress(0)
    status_text = st.empty()

    if run_button:
        
        if timeframe == "3 Months":
            data = yf.download(ticker, period="3mo")
            data2 = yf.download(ticker_2, period="3mo")
        elif timeframe == "6 Months":
            data = yf.download(ticker, period="6mo")
            data2 = yf.download(ticker_2, period="6mo")
        elif timeframe == "1 Year":
            data = yf.download(ticker, period="1y")
            data2 = yf.download(ticker_2, period="1y")
        # Check if the "Run" button is pressed
       
        data.columns = data.columns.droplevel(1)
        data2.columns = data2.columns.droplevel(1)
       
        
    
        
        if not technical_analysis and not news_and_events and not fundamental_analysis:
            st.warning("Please select at least one analysis type to proceed.")
        if data.empty:
            st.warning(f"No data available for {ticker}. Please check the ticker symbol and try again.")
        if not company:
            st.warning(f" Please add Name of company.")
        elif technical_analysis:
            
            if technical_analysis and not news_and_events and not fundamental_analysis:
                with st.expander("Downloading Data... Click to View Progress"):
                    update_progress(progress_bar, 50, 50, "Analyzing...")
                    results, recent_data, availability = calculate_technical_indicators(data,ticker)
                    results2, recent_data2, availability2 = calculate_technical_indicators(data2,ticker_2)
                    update_progress(progress_bar, 100, 100, "Finalising...")

                    bd_result = results["bd_result"]
                    sma_result = results["sma_result"]
                    rsi_result = results["rsi_result"]
                    macd_result = results["macd_result"]
                    obv_result = results["obv_result"]
                    adx_result = results["adx_result"]

                    bd_result_2 = results2["bd_result"]
                    sma_result_2 = results2["sma_result"]
                    rsi_result_2 = results2["rsi_result"]
                    macd_result_2 = results2["macd_result"]
                    obv_result_2 = results2["obv_result"]
                    adx_result_2 = results2["adx_result"]

                    gathered_data = {
                        "Ticker for Company 1": ticker,
                        "Ticker for Company 2": ticker_2,
                        "Company 1": company,
                        "Company 2": company_2,
                        "Timeframe": timeframe,
                        "Technical Analysis for ": technical_analysis,
                        "News and Events": news_and_events,
                        "Fundamental Analysis": fundamental_analysis,
                        f"data for {company}": recent_data.to_dict(orient="records"),
                        f"data for {company_2}": recent_data2.to_dict(orient="records"),
                        "Results": {
                            f"SMA Results for {company}": sma_result if 'sma_result' in locals() else "",
                            f"RSI Results for {company}": rsi_result if 'rsi_result' in locals() else "",
                            f"MACD Results for {company}": macd_result if 'macd_result' in locals() else "",
                            f"OBV Results for {company}": obv_result if 'obv_result' in locals() else "",
                            f"ADX Results for {company}": adx_result if 'adx_result' in locals() else "",
                            f"SMA Results for {company_2}": sma_result_2 if 'sma_result_2' in locals() else "",
                            f"RSI Results for {company_2}": rsi_result_2 if 'rsi_result_2' in locals() else "",
                            f"MACD Results for {company_2}": macd_result_2 if 'macd_result_2' in locals() else "",
                            f"OBV Results for {company_2}": obv_result_2 if 'obv_result_2' in locals() else "",
                            f"ADX Results for {company_2}": adx_result_2 if 'adx_result_2' in locals() else ""
                        }
                    }

                    summary = SUMMARY(gathered_data)
                    
                    update_progress(progress_bar, 100, 100, "Analysis Complete...")
                    
                sma_available = availability['sma_available']
                rsi_available = availability['rsi_available']
                macd_available = availability['macd_available']
                obv_available = availability['obv_available']
                adx_available = availability['adx_available']
                bbands_available = availability['bbands_available']

                sma_available_2 = availability2['sma_available']
                rsi_available_2 = availability2['rsi_available']
                macd_available_2 = availability2['macd_available']
                obv_available_2 = availability2['obv_available']
                adx_available_2 = availability2['adx_available']
                bbands_available_2 = availability2['bbands_available']

                

            
                st.subheader(f"Summary for {ticker}")
                with st.expander(f"Summary"):
                    st.write(summary)

                st.session_state["run_analysis_complete"] = True

                

                recent_data.reset_index(inplace=True)
                recent_data['Date'] = recent_data['Date'].astype(str)

                recent_data2.reset_index(inplace=True)
                recent_data2['Date'] = recent_data2['Date'].astype(str)

                st.session_state["gathered_data"] = gathered_data
                st.session_state["analysis_complete"] = True  # Mark analysis as complete
                st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")

                # Use an expander to show detailed analysis for each indicator
                #if bbands_available:
                    #with st.expander("View Detailed Analysis for Bollinger Bands"):
                        #fig_bbands = plot_bbands(data)
                        #st.plotly_chart(fig_bbands)
                        #st.write(bd_result)  # Display Bollinger Bands result or interpretation

                #if sma_available:
                    #with st.expander("View Detailed Analysis for SMA"):
                        #fig_sma = plot_sma(data)
                        #st.plotly_chart(fig_sma)
                        #st.write(sma_result)  # Display SMA result or interpretation

                #if rsi_available:
                    #with st.expander("View Detailed Analysis for RSI"):
                        #fig_rsi = plot_rsi(data)
                        #st.plotly_chart(fig_rsi)
                        #st.write(rsi_result)  # Display RSI result or interpretation

                #if macd_available:
                    #with st.expander("View Detailed Analysis for MACD"):
                        #fig_macd = plot_macd(data)
                        #st.plotly_chart(fig_macd)
                        #st.write(macd_result)  # Display MACD result or interpretation

                #if obv_available:
                    #with st.expander("View Detailed Analysis for OBV"):
                        #fig_obv = plot_obv(data)
                        #st.plotly_chart(fig_obv)
                        #st.write(obv_result)  # Display OBV result or interpretation

                #if adx_available:
                    #with st.expander("View Detailed Analysis for ADX"):
                        #fig_adx = plot_adx(data)
                        #st.plotly_chart(fig_adx)
                        #st.write(adx_result)  # Display ADX result or interpretation

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun() 

            if technical_analysis and news_and_events and not fundamental_analysis:
                with st.expander("Downloading Data... Click to View Progress"):
                    update_progress(progress_bar, 15, 15, "Analyzing...")
                    results, recent_data, availability = calculate_technical_indicators(data,ticker)
                    results2, recent_data2, availability2 = calculate_technical_indicators(data2,ticker_2)

                    bd_result = results["bd_result"]
                    sma_result = results["sma_result"]
                    rsi_result = results["rsi_result"]
                    macd_result = results["macd_result"]
                    obv_result = results["obv_result"]
                    adx_result = results["adx_result"]

                    bd_result_2 = results2["bd_result"]
                    sma_result_2 = results2["sma_result"]
                    rsi_result_2 = results2["rsi_result"]
                    macd_result_2 = results2["macd_result"]
                    obv_result_2 = results2["obv_result"]
                    adx_result_2 = results2["adx_result"]


                    #summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                    update_progress(progress_bar, 35, 35, "Technical Analysis complete!")
                    update_progress(progress_bar, 45, 45, "Gathering News Data...")    
                    txt_summary = generate_company_news_message(company, timeframe)
                    txt_summary_2 = generate_company_news_message(company_2, timeframe)
                    update_progress(progress_bar, 75, 75, "Analysing News Data...")
                    txt_summary = format_news(txt_summary)
                    txt_summary_2 = format_news(txt_summary_2)
                    #txt_ovr = txt_conclusion(txt_summary,company)
                    #txt_ovr_2 = txt_conclusion(txt_summary_2,company_2)
                    update_progress(progress_bar, 85, 85, "Finalising...")

                    gathered_data = {
                        "Ticker for Company 1": ticker,
                        "Ticker for Company 2": ticker_2,
                        "Company 1": company,
                        "Company 2": company_2,
                        "Timeframe": timeframe,
                        "Technical Analysis for ": technical_analysis,
                        "News and Events": news_and_events,
                        "Fundamental Analysis": fundamental_analysis,
                        f"data for {company}": recent_data.to_dict(orient="records"),
                        f"data for {company_2}": recent_data2.to_dict(orient="records"),
                        f"News data for {company}": txt_summary,
                        f"News data for {company_2}": txt_summary_2,
                        "Results": {
                            f"SMA Results for {company}": sma_result if 'sma_result' in locals() else "",
                            f"RSI Results for {company}": rsi_result if 'rsi_result' in locals() else "",
                            f"MACD Results for {company}": macd_result if 'macd_result' in locals() else "",
                            f"OBV Results for {company}": obv_result if 'obv_result' in locals() else "",
                            f"ADX Results for {company}": adx_result if 'adx_result' in locals() else "",
                            f"SMA Results for {company_2}": sma_result_2 if 'sma_result_2' in locals() else "",
                            f"RSI Results for {company_2}": rsi_result_2 if 'rsi_result_2' in locals() else "",
                            f"MACD Results for {company_2}": macd_result_2 if 'macd_result_2' in locals() else "",
                            f"OBV Results for {company_2}": obv_result_2 if 'obv_result_2' in locals() else "",
                            f"ADX Results for {company_2}": adx_result_2 if 'adx_result_2' in locals() else ""
                        }
                    }


                    ovr_summary = merge_news_and_technical_analysis_summary(gathered_data,timeframe)
                    update_progress(progress_bar, 100, 100, "Analysis Complete...")
                

                sma_available = availability['sma_available']
                rsi_available = availability['rsi_available']
                macd_available = availability['macd_available']
                obv_available = availability['obv_available']
                adx_available = availability['adx_available']
                bbands_available = availability['bbands_available']



            

                #st.subheader(f"News and Events Analysis and Technical Analysis for {ticker} over the past {timeframe}")
                #text = convert_to_raw_text(txt_summary)
                #st.write(text)
                #st.subheader("Technical Analysis Summary")
                #st.write(summary)
               
                text_ovr_s = convert_to_raw_text(ovr_summary)
                st.write(text_ovr_s)

                
                

                st.session_state["run_analysis_complete"] = True
                st.session_state["gathered_data"] = gathered_data
                st.session_state["analysis_complete"] = True  # Mark analysis as complete
                st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")

                # Use an expander to show detailed analysis for each indicator
                #if bbands_available:
                    #with st.expander("View Detailed Analysis for Bollinger Bands"):
                        #fig_bbands = plot_bbands(data)
                        #st.plotly_chart(fig_bbands)
                        #st.write(bd_result)  # Display Bollinger Bands result or interpretation

                #if sma_available:
                    #with st.expander("View Detailed Analysis for SMA"):
                        #fig_sma = plot_sma(data)
                        #st.plotly_chart(fig_sma)
                        #st.write(sma_result)  # Display SMA result or interpretation

                #if rsi_available:
                    #with st.expander("View Detailed Analysis for RSI"):
                        #fig_rsi = plot_rsi(data)
                        #st.plotly_chart(fig_rsi)
                        #st.write(rsi_result)  # Display RSI result or interpretation

                #if macd_available:
                    #with st.expander("View Detailed Analysis for MACD"):
                        #fig_macd = plot_macd(data)
                        #st.plotly_chart(fig_macd)
                        #st.write(macd_result)  # Display MACD result or interpretation

                #if obv_available:
                    #with st.expander("View Detailed Analysis for OBV"):
                        #fig_obv = plot_obv(data)
                        #st.plotly_chart(fig_obv)
                        #st.write(obv_result)  # Display OBV result or interpretation

                #if adx_available:
                    #with st.expander("View Detailed Analysis for ADX"):
                        #fig_adx = plot_adx(data)
                        #st.plotly_chart(fig_adx)
                        #st.write(adx_result)  # Display ADX result or interpretation

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun() 

            if technical_analysis and fundamental_analysis and not news_and_events:
                with st.expander("Downloading Data... Click to View Progress"):
                    update_progress(progress_bar, 15, 15, "Analyzing...")
                    results, recent_data, availability = calculate_technical_indicators(data,ticker)
                    results2, recent_data2, availability2 = calculate_technical_indicators(data2,ticker_2)

                    bd_result = results["bd_result"]
                    sma_result = results["sma_result"]
                    rsi_result = results["rsi_result"]
                    macd_result = results["macd_result"]
                    obv_result = results["obv_result"]
                    adx_result = results["adx_result"]

                    bd_result_2 = results2["bd_result"]
                    sma_result_2 = results2["sma_result"]
                    rsi_result_2 = results2["rsi_result"]
                    macd_result_2 = results2["macd_result"]
                    obv_result_2 = results2["obv_result"]
                    adx_result_2 = results2["adx_result"]


                    summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                    update_progress(progress_bar, 35, 35, "Technical Analysis complete!")
                    file_content = uploaded_file
                    file_name = uploaded_file.name
                    file_content_2 = uploaded_file2
                    file_name_2 = uploaded_file2.name
                    update_progress(progress_bar, 50, 50, "Analysing Financial Information...")  
                    fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)
                    fa_summary2 = FUNDAMENTAL_ANALYSIS(file_content_2, company_2, file_name_2)


                    update_progress(progress_bar, 80, 80, "Finalising...")

                    gathered_data = {
                        "Ticker for Company 1": ticker,
                        "Ticker for Company 2": ticker_2,
                        "Company 1": company,
                        "Company 2": company_2,
                        "Timeframe": timeframe,
                        "Technical Analysis for ": technical_analysis,
                        "News and Events": news_and_events,
                        "Fundamental Analysis": fundamental_analysis,
                        f"data for {company}": recent_data.to_dict(orient="records"),
                        f"data for {company_2}": recent_data2.to_dict(orient="records"),
                        f"Fundamental Analysis for {company}": fa_summary,
                        f"Fundamental Analysis for {company_2}": fa_summary2,
                        "Results": {
                            f"SMA Results for {company}": sma_result if 'sma_result' in locals() else "",
                            f"RSI Results for {company}": rsi_result if 'rsi_result' in locals() else "",
                            f"MACD Results for {company}": macd_result if 'macd_result' in locals() else "",
                            f"OBV Results for {company}": obv_result if 'obv_result' in locals() else "",
                            f"ADX Results for {company}": adx_result if 'adx_result' in locals() else "",
                            f"SMA Results for {company_2}": sma_result_2 if 'sma_result_2' in locals() else "",
                            f"RSI Results for {company_2}": rsi_result_2 if 'rsi_result_2' in locals() else "",
                            f"MACD Results for {company_2}": macd_result_2 if 'macd_result_2' in locals() else "",
                            f"OBV Results for {company_2}": obv_result_2 if 'obv_result_2' in locals() else "",
                            f"ADX Results for {company_2}": adx_result_2 if 'adx_result_2' in locals() else ""
                        }
                    }  

                    fa_ta_summary = merge_ta_fa_summary(gathered_data)
                    update_progress(progress_bar, 100, 100, "Analysis Complete...")

                
                
                sma_available = availability['sma_available']
                rsi_available = availability['rsi_available']
                macd_available = availability['macd_available']
                obv_available = availability['obv_available']
                adx_available = availability['adx_available']
                bbands_available = availability['bbands_available']
                #st.subheader(f"Fundamental Analysis and Technical Analysis for {ticker} over the past {timeframe}")
                text_fa = convert_to_raw_text(fa_ta_summary)
                st.write(text_fa)

                st.session_state["run_analysis_complete"] = True
                st.session_state["gathered_data"] = gathered_data
                st.session_state["analysis_complete"] = True  # Mark analysis as complete
                st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")
            
            if technical_analysis and fundamental_analysis and news_and_events:
                with st.expander("Downloading Data... Click to View Progress"):
                    update_progress(progress_bar, 15, 15, "Analyzing...")
                    results, recent_data, availability = calculate_technical_indicators(data,ticker)
                    results2, recent_data2, availability2 = calculate_technical_indicators(data2,ticker)

                    bd_result = results["bd_result"]
                    sma_result = results["sma_result"]
                    rsi_result = results["rsi_result"]
                    macd_result = results["macd_result"]
                    obv_result = results["obv_result"]
                    adx_result = results["adx_result"]

                    bd_result_2 = results2["bd_result"]
                    sma_result_2 = results2["sma_result"]
                    rsi_result_2 = results2["rsi_result"]
                    macd_result_2 = results2["macd_result"]
                    obv_result_2= results2["obv_result"]
                    adx_result_2 = results2["adx_result"]



                    summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                    summary2 = SUMMARY(ticker, bd_result_2, sma_result_2, rsi_result_2, macd_result_2, obv_result_2, adx_result_2)
                    update_progress(progress_bar, 35, 35, "Technical Analysis complete!")
                    update_progress(progress_bar, 45, 45, "Gathering News Data...")    
                    txt_summary = generate_company_news_message(company, timeframe)
                    txt_summary_2 = generate_company_news_message(company_2, timeframe)
                    update_progress(progress_bar, 75, 75, "Analysing News Data...")
                    txt_summary = format_news(txt_summary)
                    txt_summary_2 = format_news(txt_summary_2)
                    #text_ovr_s = convert_to_raw_text(txt_ovr)
                    #text_ovr_2s = convert_to_raw_text(txt_ovr_2)
                    update_progress(progress_bar, 80, 80, "Analysing Financial Information...")  
                    file_content = uploaded_file
                    file_content_2 = uploaded_file2
                    file_name = uploaded_file.name
                    file_name_2 = uploaded_file2.name
                    fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)
                    fa_summary2 = FUNDAMENTAL_ANALYSIS(file_content_2, company_2, file_name_2)

                    gathered_data = {
                        "Ticker": ticker,
                        "Company": company,
                        "Timeframe": timeframe,
                        "Technical Analysis": technical_analysis,
                        "Fundamental Analysis": fundamental_analysis,
                        f"data for {company}": recent_data.to_dict(orient="records"),
                        f"data for {company_2}": recent_data2.to_dict(orient="records"),
                        f"News data for {company}": txt_summary,
                        f"News data for {company_2}": txt_summary_2,
                        f"Fundamental Analysis for {company}": fa_summary,
                        f"Fundamental Analysis for {company_2}": fa_summary2,
                        "Results": {
                            f"SMA Results for {company}": sma_result if 'sma_result' in locals() else "",
                            f"RSI Results for {company}": rsi_result if 'rsi_result' in locals() else "",
                            f"MACD Results for {company}": macd_result if 'macd_result' in locals() else "",
                            f"OBV Results for {company}": obv_result if 'obv_result' in locals() else "",
                            f"ADX Results for {company}": adx_result if 'adx_result' in locals() else "",
                            f"SMA Results for {company_2}": sma_result_2 if 'sma_result_2' in locals() else "",
                            f"RSI Results for {company_2}": rsi_result_2 if 'rsi_result_2' in locals() else "",
                            f"MACD Results for {company_2}": macd_result_2 if 'macd_result_2' in locals() else "",
                            f"OBV Results for {company_2}": obv_result_2 if 'obv_result_2' in locals() else "",
                            f"ADX Results for {company_2}": adx_result_2 if 'adx_result_2' in locals() else ""
                        }
                    }
                    update_progress(progress_bar, 90, 90, "Finalising...")  
                    fa_ta_na_summary = merge_ta_fa_na_summary(gathered_data)
                    update_progress(progress_bar, 100, 100, "Analysis Complete...")  
                
                
                
                #st.subheader(f"Fundamental Analysis and Technical Analysis for {ticker} over the past {timeframe}")
                text_ovr_s = convert_to_raw_text(fa_ta_na_summary)
                st.write(text_ovr_s)

                st.session_state["run_analysis_complete"] = True
                st.session_state["gathered_data"] = gathered_data
                st.session_state["analysis_complete"] = True  # Mark analysis as complete
                st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")



        if news_and_events and not technical_analysis and not fundamental_analysis:
            with st.expander("Downloading Data"):
                update_progress(progress_bar, 30, 30, "Gathering News Data...")    
                txt_summary = generate_company_news_message(company, timeframe)
                txt_summary_2 = generate_company_news_message(company_2, timeframe)
                update_progress(progress_bar, 50, 50, "Analysing News Data...")
                txt_summary = format_news(txt_summary)
                txt_summary_2 = format_news(txt_summary_2)
                update_progress(progress_bar, 100, 100, "Finalising...")

            gathered_data = {
                "Ticker": ticker,
                "Company": company,
                "Timeframe": timeframe,
                "Technical Analysis": technical_analysis,
                "Fundamental Analysis": fundamental_analysis,
                f"News data for {company}": txt_summary,
                f"News data for {company_2}": txt_summary_2,
                "Results": {
                    "Summary": summary if 'summary' in locals() else "",
                    "SMA Results": sma_result if 'sma_result' in locals() else "",
                    "RSI Results": rsi_result if 'rsi_result' in locals() else "",
                    "MACD Results": macd_result if 'macd_result' in locals() else "",
                    "OBV Results": obv_result if 'obv_result' in locals() else "",
                    "ADX Results": adx_result if 'adx_result' in locals() else ""
                }
            }
                    
            st.subheader(f"News and Events Analysis for {ticker} over the past {timeframe}")
            result = txt_conclusion(gathered_data)
            text = convert_to_raw_text(result)
            st.write(text)
        

            st.session_state["run_analysis_complete"] = True

            st.session_state["gathered_data"] = gathered_data
            st.session_state["analysis_complete"] = True  # Mark analysis as complete
            st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")

            if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun() 

        if news_and_events and fundamental_analysis and not technical_analysis: 
                with st.expander("Downloading Data"):
                    update_progress(progress_bar, 25, 25, "Gathering News Data...")    
                    txt_summary = generate_company_news_message(company, timeframe)
                    txt_summary_2 = generate_company_news_message(company_2, timeframe)
                    update_progress(progress_bar, 35, 35, "Analysing News Data...")
                    txt_summary = format_news(txt_summary)
                    txt_summary_2 = format_news(txt_summary_2)
                    update_progress(progress_bar, 45, 45, "Finalising News Analysis...")
                    file_content = uploaded_file
                    file_name = uploaded_file.name
                    file_content_2 = uploaded_file2
                    file_name_2 = uploaded_file2.name
                    update_progress(progress_bar, 60, 60, "Starting Fundamental Analysis...")
                    fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)
                    fa_summary2 = FUNDAMENTAL_ANALYSIS(file_content_2, company_2, file_name_2)

                    gathered_data = {
                        "Ticker": ticker,
                        "Company": company,
                        "Timeframe": timeframe,
                        "Technical Analysis": technical_analysis,
                        f"News data for {company}": txt_summary,
                        f"News data for {company_2}": txt_summary_2,
                        f"Fundamental Analysis for {company}": fa_summary,
                        f"Fundamental Analysis for {company_2}": fa_summary2,
                        "Results": {
                            "Summary": summary if 'summary' in locals() else "",
                            "Fundamental Analysis & News": fa_txt_summary if 'fa_txt_summary' in locals() else "",
                            "SMA Results": sma_result if 'sma_result' in locals() else "",
                            "RSI Results": rsi_result if 'rsi_result' in locals() else "",
                            "MACD Results": macd_result if 'macd_result' in locals() else "",
                            "OBV Results": obv_result if 'obv_result' in locals() else "",
                            "ADX Results": adx_result if 'adx_result' in locals() else "",
                            "Fundamental Analysis": fa_summary if 'fa_summary' in locals() else ""

                        }
                    }

                    update_progress(progress_bar, 80, 80, "Finalising Analysis...")
                    fa_txt_summary = fa_summary_and_news_summary(gathered_data)
                    update_progress(progress_bar, 100, 100, "Analysis Complete...")
                
                
                text_ovr_t = convert_to_raw_text(fa_txt_summary)
                st.write(text_ovr_t)

                st.session_state["run_analysis_complete"] = True
                st.session_state["gathered_data"] = gathered_data
                st.session_state["analysis_complete"] = True  # Mark analysis as complete
                st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun() 

                

        if fundamental_analysis and not technical_analysis and not news_and_events:
            with st.expander("Downloading Data"): 
                update_progress(progress_bar, 25, 25, "Analysis Started...")  
                file_content = uploaded_file
                file_name = uploaded_file.name
                file_content_2 = uploaded_file2
                file_name_2 = uploaded_file2.name
                update_progress(progress_bar, 50, 50, "Analysing Financial Information...")  
                fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)
                fa_summary2 = FUNDAMENTAL_ANALYSIS(file_content_2, company_2, file_name_2)

                gathered_data = {
                "Ticker": ticker,
                "Company": company,
                "Timeframe": timeframe,
                "Technical Analysis": technical_analysis,
                f"Fundamental Analysis for {company}": fa_summary,
                f"Fundamental Analysis for {company_2}": fa_summary2,
                "Results": {
                    "Summary": summary if 'summary' in locals() else "",
                    "Fundamental Analysis & News": fa_txt_summary if 'fa_txt_summary' in locals() else "",
                    "SMA Results": sma_result if 'sma_result' in locals() else "",
                    "RSI Results": rsi_result if 'rsi_result' in locals() else "",
                    "MACD Results": macd_result if 'macd_result' in locals() else "",
                    "OBV Results": obv_result if 'obv_result' in locals() else "",
                    "ADX Results": adx_result if 'adx_result' in locals() else "",
                    "Fundamental Analysis": fa_summary if 'fa_summary' in locals() else ""

                }
            }
                
                update_progress(progress_bar, 100, 100, "Analysing Financial Information...")  
            
            fa_ovr = fundamental_compare(gathered_data)
            text_fs = convert_to_raw_text(fa_ovr)
            st.write(text_fs)

            st.session_state["run_analysis_complete"] = True
            st.session_state["gathered_data"] = gathered_data
            st.session_state["analysis_complete"] = True  # Mark analysis as complete
            st.success("Stock analysis completed! You can now proceed to the AI Chatbot.")

            if st.button("Run Another Stock"):
                        analysis_complete = False
                        st.session_state.technical_analysis = False
                        st.session_state.news_and_events = False
                        st.session_state["1_month"] = False
                        st.session_state["3_months"] = False
                        st.session_state["6_months"] = False
                        st.session_state["1_year"] = False
                        st.experimental_rerun() 


def convert_to_raw_text(text):
    # Remove markdown headers (e.g., ###, ##, #)
    text = re.sub(r'\$', '', text)

    return text


def fa_summary_and_news_summary(gather_data):

           
    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    """You are an AI model trained to create a comprehensive investment report comparing two assets by integrating recent news and events data with fundamental analysis. Your role is to merge insights from each asset’s financial health and the impact of current developments to produce a well-rounded assessment and actionable recommendations. Use the following format and guidelines to structure your response:

                    Formatting Requirements:
                    Headings and Subheadings:
                    Organize the report with clear headings (e.g., “Asset 1: Fundamental Analysis Summary,” “Asset 2: Recent News and Events,” “Comparative Investment Insights”).
                    Consistent Formatting:
                    Bold critical metrics and key event names (e.g., Revenue Growth, Product Launch).
                    Bullet Points and Numbered Lists:
                    Use bullet points for lists of events and data points, and numbered lists for any recommended steps or prioritized actions.
                    Structure Guidelines:
                    1. Introduction:
                    Briefly summarize both assets, their industry context, and the relevance of integrating fundamental analysis and recent events.
                    State the objective: to provide a comparative perspective on the investment potential of both assets by combining fundamental performance and recent developments.
                    2. Fundamental Analysis Summary (For Each Asset):
                    Financial Performance:
                    Summarize key financial metrics (e.g., revenue growth, net income) reflecting each asset’s stability and growth.
                    Valuation Metrics:
                    Include metrics like Price-to-Earnings (P/E) ratio, Price-to-Book (P/B) ratio, and Dividend Yield, with industry comparisons for each asset.
                    Market Position and Competitive Standing:
                    Outline each asset’s market position, competitive strengths, and a brief SWOT summary.
                    Key Takeaways:
                    Summarize the overall financial health and growth outlook for each asset.
                    3. Recent News and Events Summary (For Each Asset):
                    Recent Developments:
                    Summarize major events impacting each asset (e.g., product launches, regulatory changes).
                    Market Sentiment and Impact:
                    Describe how each event has affected market sentiment for the respective asset, whether positively or negatively.
                    Macro and Industry-Level News:
                    Include broader economic or industry-specific developments relevant to each asset.
                    Key Takeaways:
                    Highlight the potential influence of recent events on each asset’s outlook.
                    4. Comparative Integrated Investment Insights:
                    Alignment of Fundamentals with Recent Events:
                    Compare how recent events for each asset support or challenge their respective fundamental outlooks.
                    Market Sentiment vs. Intrinsic Value:
                    Evaluate the alignment of current sentiment with intrinsic value for both assets.
                    Risk Factors:
                    Identify any risks that recent events may introduce for either asset, such as regulatory risks or changes in competitive positioning.
                    5. Actionable Recommendations:
                    Investment Decision:
                    Provide a recommendation (Buy, Hold, Sell) for each asset, considering both fundamental and recent event insights.
                    Highlight which asset presents the stronger investment opportunity and why.
                    Entry and Exit Points:
                    Suggest entry/exit levels for both assets based on news and valuation metrics.
                    Risk Management and Monitoring:
                    Recommend any risk management strategies and important future events or updates to track for each asset.
                    Style Requirements:
                    Maintain a professional, data-driven tone without personal opinions.
                    Minimize jargon, and briefly clarify terms where necessary.
                    Keep sentences and paragraphs clear and concise to maintain logical flow and readability.
                    Using these instructions, deliver a concise, actionable comparative report combining news, events, and fundamental analysis for strategic investment decision-making between the two assets."""
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Data for Analysis {json.dumps(gather_data)}"
                ),
            },
        ]
    )

    response = chat_completion.choices[0].message.content
    return response




                
def merge_ta_fa_na_summary(gather_data):
     
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    """ You are an AI model designed to provide technical, fundamental, and news/events-based analysis to compare two assets, delivering actionable, long-term investment insights. Your role is to integrate financial health, competitive positioning, market trends, technical indicators, and relevant news/events into cohesive, data-driven recommendations for strategic, long-term investment strategies. Follow the specified structure and formatting guidelines to ensure clarity, professionalism, and usability."
                    Formatting Requirements:
                    Organized Headings and Subheadings:
                    Separate sections clearly with headings (e.g., “Asset 1: Financial Overview,” “Asset 2: Technical Trends Analysis,” “Comparative Recommendations”).
                    Use descriptive subheadings for detailed insights (e.g., “Key Financial Metrics Comparison,” “Sector-Specific Developments for Asset 1 vs. Asset 2”).
                    Bullet Points and Numbered Lists:
                    Use bullet points for comprehensive lists and numbered lists for prioritized recommendations or comparisons.
                    Formatting for Key Metrics and Indicators:
                    Bold key financial terms (e.g., Earnings Per Share (EPS), Relative Strength Index (RSI)) for emphasis.
                    Structure Guidelines:
                    1. Introduction:
                    Briefly describe the profiles of both assets, their market sectors, and their significance for long-term investors.
                    Highlight the objective of integrating fundamental, technical, and events-based analysis for a well-rounded comparison.
                    2. Fundamental Analysis:
                    2.1 Financial Performance and Stability:
                    Review financial statements for both assets to assess profitability, solvency, and growth.
                    Compare metrics such as revenue growth, net margins, and debt ratios.
                    2.2 Valuation Metrics:
                    Analyze ratios like P/E, P/B, and Dividend Yield for both assets, comparing them to industry norms and to each other.
                    2.3 Competitive Position and Risks:
                    Evaluate market share, competitive advantages, and challenges for each asset.
                    Include a SWOT analysis for each asset to outline growth drivers and risks.
                    3. Technical Analysis:
                    3.1 Long-Term Indicators:
                    For each asset, analyze:
                    MACD: Trends via signal line crossovers and price divergence.
                    ADX: Measure trend strength (e.g., readings > 20 = strong trend).
                    Bollinger Bands: Volatility for entry/exit opportunities.
                    RSI: Extended RSI values to determine overbought/oversold conditions.
                    SMA Crossovers: Monitor trends (e.g., "golden cross" patterns).
                    Compare the technical indicators between both assets.
                    4. News and Events Analysis:
                    4.1 Market Events and Macroeconomic Trends:
                    Summarize key news/events affecting both assets or their sectors (e.g., earnings releases, regulatory changes).
                    Highlight the implications for long-term investment strategies.
                    4.2 Sector-Specific Developments:
                    Address sector-wide disruptions or opportunities (e.g., technological advances, geopolitical risks) and their impact on each asset.
                    5. Integrated Comparative Analysis:
                    5.1 Correlation of Insights:
                    Combine fundamental, technical, and event-based analysis for both assets to determine alignment or divergence.
                    Assess how news/events impact the intrinsic value and technical trends of each asset.
                    5.2 Market Sentiment and Timing:
                    Evaluate whether market sentiment for each asset aligns with its fundamental strengths or highlights discrepancies.
                    6. Comparative Long-Term Actionable Recommendations:
                    6.1 Investment Decision:
                    Provide a clear Buy, Hold, or Sell recommendation for each asset, supported by key findings.
                    Highlight a preference for one asset over the other with specific reasons.
                    6.2 Entry and Exit Points:
                    Specify ideal entry/exit points for each asset using long-term technical indicators (e.g., SMA crossovers, RSI levels).
                    6.3 Risk Management:
                    Suggest risk mitigation strategies for each asset (e.g., stop-loss levels, portfolio diversification).
                    6.4 Performance Monitoring:
                    Highlight key updates (e.g., quarterly earnings) and technical changes (e.g., MACD signals) to monitor for each asset periodically.
                    Style Requirements:
                    Maintain a professional, analytical tone, avoiding personal opinions.
                    Use clear, concise language to ensure readability.
                    Minimize jargon and explain technical terms for clarity where needed.
                    Using these instructions, you will deliver a detailed, actionable comparative report that enables readers to make well-informed, strategic investment decisions based on an integrated approach to fundamental, technical, and events-based analysis for both assets."""
                ),

            },
            {
                "role": "user",
                "content": (
                    f"The data to analyse: {json.dumps(gather_data)}"
                ),
            },
        ]
     )

    response = chat_completion.choices[0].message.content
    return response



                
                



def merge_ta_fa_summary(gather_data,):

    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    """You are an AI model designed to provide comprehensive, long-term investment analysis by merging fundamental and technical analysis to compare two assets. Your role is to combine insights from the financial health, competitive positioning, and market trends of both assets with their respective technical indicators to deliver actionable, data-driven recommendations tailored for long-term investment strategies. Use the following structure and formatting guidelines to provide a detailed, practical, and comparative report:
                    Formatting Requirements:
                    Organized Headings and Subheadings: Use clear headings and subheadings to separate sections (e.g., “Asset 1: Financial Overview,” “Asset 2: Technical Indicators,” “Comparative Long-Term Recommendations”).
                    Bullet Points and Numbered Lists: Use bullet points for lists and numbered lists for prioritized or sequential steps, especially in recommendation sections.
                    Formatting for Key Metrics and Indicators: Bold critical financial terms and technical indicators (e.g., Net Profit Margin, RSI) for emphasis.
                    Structure Guidelines:
                    Introduction:

                    Briefly summarize the profiles of both assets, their market sectors, and their relevance for long-term investors.
                    Highlight the objective of integrating fundamental strength and technical trends to support long-term holding decisions and provide a comparative context.
                    Fundamental Analysis (For Each Asset):

                    Financial Performance and Stability:
                    Examine key financial statements (e.g., income statement, balance sheet, cash flow) for both assets to evaluate profitability, solvency, and growth.
                    Compare metrics like revenue growth, earnings stability, and debt management.
                    Valuation Metrics:
                    Highlight relevant ratios (e.g., P/E, P/B, Dividend Yield) for each asset and compare them to industry averages and to each other.
                    Competitive Position and Market Standing:
                    Assess market share, competitive advantages, and potential risks for both assets.
                    Include a comparative SWOT analysis to identify long-term growth drivers and challenges.
                    Technical Analysis (For Each Asset):

                    Key Indicators for Long-Term Trends:
                    Analyze MACD for trend direction, ADX for trend strength, OBV for volume alignment, Bollinger Bands for volatility, RSI for overbought/oversold conditions, and SMA crossovers for bullish or bearish trends.
                    Provide side-by-side comparisons of the indicators for both assets.
                    Integrated Comparative Analysis:

                    Correlation of Fundamental Strength with Technical Trends:
                    Discuss how the intrinsic values and financial health of both assets align with their technical trends.
                    Highlight consistencies or divergences between long-term value indicators and current market trends for each asset.
                    Market Sentiment and Timing Implications:
                    Summarize how technical signals (e.g., RSI, ADX, MACD) for each asset align with their long-term valuation and growth potential.
                    Identify discrepancies between market sentiment and intrinsic value and how these may affect timing decisions for both assets.
                    Comparative Long-Term Actionable Recommendations:

                    Investment Decision:
                    Clearly state a Buy, Hold, or Sell recommendation for each asset based on fundamental and technical analysis.
                    Include a preference for one asset over the other with specific reasons for the recommendation.
                    Entry and Exit Points:
                    Identify ideal entry and exit points for each asset based on long-term technical indicators (e.g., Bollinger Bands, RSI levels).
                    Risk Management Strategies:
                    Outline risk mitigation techniques for both assets, such as diversification, stop-loss levels based on SMA trends, or sector allocation strategies.
                    Performance Monitoring for Long-Term:
                    Provide a list of key fundamental updates (e.g., earnings reports) and technical indicators (e.g., ADX changes, MACD crossovers) to monitor periodically for alignment with the long-term outlook for both assets.
                    Style Requirements:
                    Maintain a professional, analytical tone, avoiding personal opinions.
                    Minimize jargon, explaining technical terms in plain language where necessary for clarity.
                    Keep sentences and paragraphs concise, ensuring the report remains readable and logically structured for a comparative, long-term investment context.
                    Using these instructions, you will deliver a detailed, actionable comparative report that enables readers to make well-informed, strategic investment decisions based on an integrated approach to fundamental and technical analysis for both assets"""
                                        #Add Press releases, investor oppinions (X), First World Pharma, Bloomberg, Market Watch, seperate segment,add sources, add graphs
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"data for Analysis: {json.dumps(gather_data)}"
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response

                        
                

        #if t_col1.button("Technical Analysis"):
            #analysis_type = "Technical Analysis"
        #elif n_col2.button("News and Events"):
            #analysis_type = "News and Events"

def txt_conclusion(gather_data):
    # OpenAI API call to create a merged summary
    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    """You are an AI model specializing in investment insights, tasked with analyzing recent news and events about two specified companies and providing comparative recommendations for investors. Your goal is to review relevant data, including press releases, market trends, earnings reports, and industry events, to assess each company’s financial health, growth prospects, and potential risks. Based on this analysis, you will determine an ideal investor position (e.g., buy, hold, or sell) for each company and highlight which presents a stronger investment opportunity."
                        Instructions:
                        1. Data Collection:
                        Search for and analyze recent press releases, earnings reports, regulatory filings, and news articles for both companies, focusing on the following:

                        Financial Performance:

                        Review quarterly or annual earnings, revenue, and profit trends for each company.
                        Highlight any significant differences in financial performance metrics.
                        Product & Service Developments:

                        Identify new product launches, service expansions, or market innovations for each company.
                        Compare how these developments contribute to their growth prospects.
                        Management Statements:

                        Note key statements from executives or significant personnel changes for each company that might impact their strategic direction.
                        Highlight differences in leadership approaches or priorities.
                        Industry Events & Competitor Actions:

                        Examine news of industry-wide developments, competitor performance, and market conditions affecting each company.
                        Compare how each company is positioned within the industry.
                        Regulatory & Legal News:

                        Assess any legal challenges, regulatory updates, or policy changes impacting each company.
                        Highlight differences in regulatory or legal risks.
                        Sentiment Analysis:

                        Evaluate the tone and sentiment of news data for each company—whether positive, neutral, or negative.
                        Compare investor confidence and sentiment trends between the two companies.
                        Market Impact:

                        Summarize immediate or anticipated effects of recent events on each company’s stock price.
                        Highlight key differences in short-term volatility, growth indicators, or risk factors that could affect long-term performance.
                        2. Investor Recommendation:
                        Provide comparative recommendations for both companies:

                        Buy:

                        Recommend for a company with positive news, strong financial performance, and promising growth potential that outweigh risks.
                        Hold:

                        Suggest for a company with mixed indicators, where potential growth is tempered by risks or uncertain factors.
                        Sell:

                        Advise for a company with significant risks, declining performance, or negative news dominating, suggesting potential for a downturn.
                        3. Final Conclusion:
                        Provide a clear, comparative summary and reasoning behind the recommended position for each company.
                        Address key data points, highlighting the rationale for an investor’s action.
                        Clearly identify which company presents a stronger long-term investment opportunity and explain why.
                        4. Additional Sources:
                        Include a separate section listing sources like press releases, earnings reports, and media opinions for each company.
                        Ensure proper citations to enhance credibility and facilitate further investigation."""
                    #Add Press releases, investor oppinions (X), First World Pharma, Bloomberg, Market Watch, seperate segment,add sources, add graphs
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"The data to analyse {json.dumps(gather_data)}"   
                ),
            },
        ]
    )

# Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response 

    

def merge_news_and_technical_analysis_summary(gather_data,time_period):
    """
    Combines the news and events summary with the technical analysis summary using OpenAI's GPT model.
    
    Parameters:
    - company_name: The name of the company being analyzed.
    - news_summary: The summarized news and events information.
    - technical_summary: The summarized technical analysis output.

    Returns:
    - An overall summary that integrates both the news and technical analysis in a cohesive manner.
    """
    # OpenAI API call to create a merged summary
    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    """As an AI assistant dedicated to supporting traders and investors in comparing stocks, your primary objective is to synthesize relevant market data by merging current news and events with thorough technical analysis for two selected stocks.
                    When analyzing the stocks, you will:

                    Begin by analyzing the latest market news for both stocks, focusing on economic indicators, press releases, and significant announcements that may influence their performance.
                    Simultaneously, evaluate the technical trends of each stock, including price movements, volume patterns, and key indicators (such as moving averages and RSI).
                    Gather and analyze this information to compile a comparative summary that is clear and concise, highlighting the fundamental news and technical trends for both stocks.
                    Present a detailed and focused overall assessment that compares the strengths and weaknesses of each stock, including actionable recommendations based on anticipated future news, historical trends, and their relative performance.
                    Include insights from various sources such as press releases, investor opinions, First World Pharma, Bloomberg, and Market Watch, and ensure proper citation of all sources for credibility and further investigation.
                    Structure your output as follows:

                    Introduction: A brief overview of both stocks and their relevance in the current market context.
                    News Analysis: A comparison of significant news and events affecting each stock.
                    Technical Analysis: Insights on the price movements and relevant technical indicators for both stocks, highlighting differences and similarities.
                    Comparative Summary: A synthesis of the news and technical analysis, providing actionable recommendations about which stock shows stronger potential and why.
                    Additional Sources: A separate section listing sources used for insights, with proper citations.
                    Ensure that your analysis is accessible to readers without technical knowledge, avoiding jargon where possible. Emphasize clear and actionable recommendations, clearly identifying which stock is better suited for a long-term position and why, based on the comparative analysis"""
                    #Add Press releases, investor oppinions (X), First World Pharma, Bloomberg, Market Watch, seperate segment,add sources, add graphs
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"here is the data {json.dumps(gather_data)}"
                    "Merge these details into one cohesive summary, make it flow, highlighting how the news may impact the stock's technical indicators and providing "
                    f"an in-depth overall outlook on the stock's potential future performance for the next coming {time_period}, plus provide actionable recommendations as well."
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response

def generate_company_news_message(company_name, time_period):
    # Define the messages for different time periods 
    def post_to_webhook(data):
        webhook_url = "https://hook.eu2.make.com/s4xsnimg9v87rrrckcwo88d9k57186q6"
        if webhook_url:
    
            response = requests.post(webhook_url,data)
            return response
        else:
            print("Error")

    data = {"Ticker": company_name, "Time Frame": time_period}


    response = post_to_webhook(data)
    print(response.text)

    time.sleep(65)

    scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]


    credentials = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\linco\\OneDrive\\Desktop\\Aescap\\Momentum\\stock-momentum-438620-d28ed2443e1a.json")
    gc = gspread.authorize(credentials)
    #gc = gspread.service_account.from_json_keyfile_name(filename="C:\\Users\\linco\\OneDrive\\Desktop\\Aescap\\Momentum\\stock-momentum-438620-d28ed2443e1a.json")
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1-cDCZDq8r1rGDVYpY_JhQvb0srhqsIiPhGWaxRC1TPw/edit?usp=sharing")
    previous = sh.sheet1.get('A2')
    future = sh.sheet1.get('B2')
          
    chats = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an artificial intelligence assistant, and your role is to "
                    f"present the latest news and updates along with the future news and update for {company_name} in a detailed, organized, and engaging manner."
            },
            {
                "role": "user",
                "content": f"Present the news and events aswell {company_name} over the past {time_period} retatining all the Dates aswell as the future news and events: Latest News and Updates text {previous}, Future News and Updates text {future}?"
            },
        ]
    )
    response = chats.choices[0].message.content
    return response
     

def bollingerbands(company_name, data_text):
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an AI model designed to assist long-term day traders in analyzing stock market data. "
                    "Your primary task is to interpret stock trading data, especially focusing on Bollinger Bands, "
                    "to identify key market trends. When provided with relevant data you will: "
                    "Analyze the stock's current position relative to its Bollinger Bands (upper, middle, or lower bands) and provide insights."
            },
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing the Bollinger Bands?"
            },
        ]
    )
    response = chat_completion.choices[0].message.content
    return response
def SMA(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on 20, 50, and 200 Simple Moving Averages (SMA),"
                    "to identify key market trends. When provided with relevant data you will:"
                    "\n- Analyze the stock's current position relative to its 20, 50, and 200 SMAs."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a breakout based on the relationships between the SMAs."
                    "\n- Determine if the stock is prone to a reversal by analyzing price movements, SMA crossovers, and the stock's position relative to key SMAs."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific SMA characteristics (e.g., crossovers, price deviation from SMAs, trend strength)"
                    "indicate potential market moves."
                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing SMA?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def RSI(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on the Relative Strength Index (RSI),"
                    "to identify key market trends. When provided with relevant data you will:"

                    "\n- Analyze the stock's current RSI values to determine if it is overbought, oversold, or in a neutral range."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a potential reversal based on RSI levels and patterns."
                    "\n- Determine if the stock is prone to a reversal by analyzing RSI divergences (bullish or bearish), overbought/oversold conditions, and the stock's momentum."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific RSI characteristics (e.g., divergence, trend strength, threshold breaches)"
                    "indicate potential market moves."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing RSI?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response

def MACD(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on the MACD (Moving Average Convergence Divergence), MACD Signal Line, and MACD Histogram,"
                    "to identify key market trends. When provided with relevant data you will:"
                    "\n- Analyze the stock's MACD line, Signal Line, and Histogram to assess trend strength and potential price direction."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a crossover by analyzing the MACD line relative to the Signal Line."
                    "\n- Determine if the stock is prone to a reversal by examining MACD crossovers, divergences, and changes in the MACD Histogram."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific MACD characteristics (e.g., crossover points, divergence, histogram changes)"
                    "indicate potential market moves."
                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing MACD?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def OBV(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on On-Balance Volume (OBV),"
                    "to identify key market trends. When provided with relevant data you will:"

                    "\n\n- Read and extract relevant data from PDF and CSV files."
                    "\n- Analyze the stock's OBV to assess the relationship between volume and price movement."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a breakout by evaluating OBV trends and volume momentum."
                    "\n- Determine if the stock is prone to a reversal by analyzing OBV divergences (where OBV moves in the opposite direction of price), which can signal potential trend changes."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific OBV characteristics (e.g., divergence, volume spikes, confirmation of price moves)"
                    "indicate potential market moves."

                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing the OBV?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def ADX(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on the Average Directional Index (ADX),"
                    "to identify key market trends. When provided with relevant data you will:"

                    "\n- Analyze the stock's ADX values to assess the strength of the current trend, regardless of its direction."
                    "\n- Assess if the stock is in a strong or weak trend based on ADX levels, with particular attention to rising or falling ADX values."
                    "\n- Determine if the stock is prone to a trend reversal by analyzing ADX indicating whether the market is gaining or losing trend strength."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific ADX characteristics (e.g., ADX crossovers, trend strength, or weakening trends)"
                    "indicate potential market moves."

                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing ADX?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response

def fundamental_compare(gather_data):
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """ 
                Here’s the revised instruction tailored for comparing two financial assets:

                "You are an AI model trained to format text for the fundamental analysis of two financial assets, focusing on providing actionable recommendations. Your role is to structure content in a clear, logical, and standardized manner, organizing financial, operational, and strategic insights for both assets and concluding with practical, comparative recommendations. Your output should adhere to the following format:"

                Formatting Requirements:
                Headings and Subheadings:

                Organize the analysis with concise, descriptive headings (e.g., “Asset 1: Financial Overview,” “Asset 2: Competitive Analysis,” “Comparative Investment Recommendations”).
                Bullet Points and Numbered Lists:

                Use bullet points for concise lists of information and numbered lists for sequential steps or prioritized actions. This enhances readability, particularly in sections with extensive data.
                Consistent Formatting for Key Metrics:

                Bold critical financial terms and ratios (e.g., Earnings Per Share (EPS), Price-to-Earnings Ratio (P/E)).
                Structure Guidelines:
                1. Introduction:
                Provide a concise overview of both assets, including their industry context and the primary purpose of the analysis.
                State the objective: to provide a comparative evaluation of their financial health, market position, and strategic direction.
                2. Financial Analysis (For Each Asset):
                2.1 Income Statement:
                Summarize trends in revenue, cost of goods sold, operating income, and net income for each asset.
                Point out significant changes or growth patterns, comparing the two.
                2.2 Balance Sheet:
                Summarize assets, liabilities, and equity, focusing on liquidity and leverage metrics for each asset.
                Highlight differences in financial stability and leverage.
                2.3 Cash Flow Statement:
                Highlight cash flow from operating, investing, and financing activities for each asset.
                Emphasize cash generation capability and any unusual patterns, comparing their financial flexibility.
                2.4 Key Ratios and Metrics:
                Compare profitability ratios (e.g., Gross Margin, Return on Assets).
                Compare liquidity ratios (e.g., Current Ratio, Quick Ratio).
                Compare leverage ratios (e.g., Debt-to-Equity Ratio).
                Compare valuation ratios (e.g., P/E, Price-to-Book Ratio).
                3. Competitive Positioning and Market Analysis:
                Provide an overview of each asset’s competitive position, market share, and primary competitors.
                Summarize industry trends and conduct a SWOT analysis for both assets, highlighting comparative strengths and weaknesses.
                4. Management and Governance:
                Describe the executive team and board structure for each asset, noting experience, past performance, and recent changes.
                Mention recent strategic decisions (e.g., acquisitions, new product lines) impacting each asset’s performance, comparing their effectiveness.
                5. Conclusion and Outlook:
                Offer a concise summary of each asset’s strengths and potential risks based on financial and strategic positioning.
                Provide a comparative outlook considering financial stability, industry conditions, and management’s strategic direction.
                6. Actionable Recommendations:
                6.1 Investment Recommendation:
                Clearly state whether to Buy, Hold, or Sell each asset based on the findings.
                Justify each recommendation with reference to valuation metrics, market conditions, or management actions.
                Highlight which asset presents the stronger investment opportunity and explain why.
                6.2 Risk Management Suggestions:
                Outline potential risk mitigation strategies for both assets (e.g., sector diversification, stop-loss orders).
                6.3 Strategic Suggestions for Management:
                If relevant, suggest strategic actions for each company, such as exploring new markets, reducing debt, or optimizing operational costs.
                6.4 Performance Monitoring Tips:
                Recommend specific metrics or events (e.g., quarterly earnings, regulatory updates) that investors should watch to evaluate the ongoing performance of both assets.
                Style Requirements:
                Maintain a professional, objective tone focused on analysis without personal opinions.
                Avoid excessive jargon, opting for straightforward explanations where necessary.
                Keep sentences and paragraphs clear and direct, ensuring the reader can easily follow your logic and conclusions.
                Following these guidelines, your output will be a professional, data-driven comparative analysis, providing readers with clear insights and practical next steps for informed decision-making between the two assets."""

        },
        {
            "role": "user",
            "content": f"Data to analyse: {json.dumps(gather_data)}"
        },
        
        ]
    )

def FUNDAMENTAL_ANALYSIS(file_name, company_name, file):

    temp_file_path = os.path.join(tempfile.gettempdir(), file)

# Write the contents to the temporary file
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_name.read())
    
    message_file = client.files.create(
    file=open(temp_file_path, "rb"), purpose="assistants"
    )

    file_id = message_file.id


    data = {"File_id": file_id, "Company Name": company_name, "File_name": file}

    webhook_url = "https://hook.eu2.make.com/d68cwl3ujkpqmgrnbpgy9mx3d06vs198"
    if webhook_url:
        response = requests.post(webhook_url,data)
    else: 
        print("Error")

    time.sleep(65)

    credentials_dict = {
        "type": type_sa,
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": auth_uri,
        "token_uri": token_uri,
        "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
        "client_x509_cert_url": client_x509_cert_url,
        "universe_domain": universe_domain
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(google_sheet_url)
    anaylsis = sh.sheet1.get('C2')

    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI model trained to format text for fundamental analysis of financial assets, with a focus on providing actionable recommendations. Your role is to structure content in a clear, logical, and standardized manner, organizing financial, operational, and strategic insights and concluding with practical recommendations. Your output should adhere to the following format:"
                    "Formatting Requirements:"
                    "Headings and Subheadings: Organize the analysis with concise, descriptive headings (e.g., “Financial Overview,” “Competitive Analysis,” “Investment Recommendations”)."
                    "Bullet Points and Numbered Lists: Use bullet points for concise lists of information and numbered lists for sequential steps or prioritized actions. This enhances readability, particularly in sections with extensive data."
                    "Consistent Formatting for Key Metrics:"
                    "Bold critical financial terms and ratios (e.g., Earnings Per Share (EPS), Price-to-Earnings Ratio (P/E))."
                    "Structure Guidelines:"
                    "Introduction: Provide a concise overview of the asset, including industry context and the primary purpose of the analysis."
                    "Financial Analysis:"
                    "Income Statement: Summarize trends in revenue, cost of goods sold, operating income, and net income. Point out significant changes or growth patterns."
                    "Balance Sheet: Summarize assets, liabilities, and equity, focusing on liquidity and leverage metrics."
                    "Cash Flow Statement: Highlight cash flow from operating, investing, and financing activities, emphasizing cash generation capability and any unusual patterns."
                    "Key Ratios and Metrics:"
                    "Profitability Ratios (e.g., Gross Margin, Return on Assets)."
                    "Liquidity Ratios (e.g., Current Ratio, Quick Ratio)."
                    "Leverage Ratios (e.g., Debt-to-Equity Ratio)."
                    "Valuation Ratios (e.g., Price-to-Earnings Ratio, Price-to-Book Ratio)."
                    "Competitive Positioning and Market Analysis:"
                    "Provide an overview of the asset’s competitive position, market share, and primary competitors."
                    "Summarize industry trends and conduct a strengths, weaknesses, opportunities, and threats (SWOT) analysis to give context to the assets strategic position."
                    "Management and Governance:"
                    "Describe the executive team and board structure, noting experience, past performance, and any recent changes."
                    "Mention recent strategic decisions (e.g., acquisitions, new product lines) impacting performance."
                    "Conclusion and Outlook:"
                    "Offer a concise summary of the asset's strengths and potential risks based on financial and strategic positioning."
                    "Provide an outlook considering financial stability, industry conditions, and management’s strategic direction."
                    "Actionable Recommendations:"
                    "Investment Recommendation: Clearly state whether to Buy, Hold, or Sell the asset based on the findings. Justify this decision with reference to valuation metrics, market conditions, or management actions."
                    "Risk Management Suggestions: Outline potential risk mitigation strategies (e.g., sector diversification, stop-loss orders)."
                    "Strategic Suggestions for Management: If relevant, suggest strategic actions for the company itself, such as exploring new markets, reducing debt, or optimizing operational costs."
                    "Performance Monitoring Tips: Recommend specific metrics or events (e.g., quarterly earnings, regulatory updates) that investors should watch to evaluate ongoing asset performance."
                    "Style Requirements:"
                    "Maintain a professional, objective tone focused on analysis without personal opinions."
                    "Avoid excessive jargon, opting for straightforward explanations where necessary."
                    "Keep sentences and paragraphs clear and direct, ensuring the reader can easily follow your logic and conclusions."
                    "Following these guidelines will ensure that your output is professional, data-driven, and actionable, providing readers with clear insights and practical next steps for informed decision-making."
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"fromat this text {anaylsis}"   
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response 
    
   

    
    

def SUMMARY(gather_data):

    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"""You are an AI model designed to assist long-term day traders in analyzing and comparing stock market data of two companies.
                Your primary task is to interpret and provide a well-rounded conclusion from texts that report on both lagging indicators (MACD, SMA) and leading indicators (ADX, RSI, OBV, Bollinger Bands) for both companies, and offer clear and easy-to-understand insights on their relative trends.

                When provided with relevant data you will:

                Read and extract key information from texts or reports that discuss MACD, SMA (lagging indicators), and ADX, RSI, OBV, Bollinger Bands (leading indicators) for both companies.
                Synthesize findings from multiple sources into a cohesive conclusion, drawing connections between the behaviors of lagging and leading indicators for both companies.
                Provide a comparative analysis of the two companies’ trends, focusing on which company shows a stronger, weaker, or more volatile trend based on the combined data.
                Offer a clear and concise conclusion about which company might have better long-term growth potential or stability, and suggest a preferred position based on the analysis.
                Ensure that your conclusions are clear and easy to understand, assuming the person reading has no prior knowledge of trading, and avoid complex jargon where necessary.
                Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders.

                Only output the end conclusion, with no need to detail individual insights from each indicator.
                Limit the output to just 3 paragraphs, and bold your recommendation for which company to take a long-term position on and why"""
                    
                   
                                    
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Here is the data {json.dumps(gather_data)}"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response

def format_news(txt_summary):
    chat_completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content": (
                    "You are an expert in formatting text for clarity and professional presentation. "
                    "Your task is to prepare a well-organized, easy-to-read document summarizing recent events in font size 12 with attention to layout consistency. "
                    "Follow these instructions:"
                    "\n- Text Formatting: Use font size 12 consistently across all text for readability."
                    "\n- Begin each entry with the Date and Event Title in bold to highlight key information upfront."
                    "\n- Event Description Structure: Organize each event entry in a structured format:"
                    "\n  - Date: Bolded, immediately followed by the Event Title in bold on the same line."
                    "\n  - Overview: Provide a concise summary of the event, outlining its main points."
                    "\n  - Impact: Discuss potential implications or significance, especially regarding the market."
                    "\nExample Entry Format:"
                    "\n[Date: October 15, 2024] [Event Title: Q3 Earnings Release]"
                    "\nOverview: The company reported a strong year-over-year increase in Q3 revenue, primarily due to heightened demand in its core market."
                    "\nImpact: Analysts predict this trend may lead to a stock price increase, as revenue growth outpaces industry averages."
                    "\nSource: Company press release, MarketWatch article."
                )
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"text to format {txt_summary}"
                
            },
        ],  
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response



def calculate_technical_indicators(data,ticker):
    """
    Calculate various technical indicators and prepare them for AI analysis.

    Args:
        data (pd.DataFrame): The input financial data with columns ['Open', 'High', 'Low', 'Close', 'Volume'].
        ticker (str): The stock ticker.

    Returns:
        Dict[str, str]: A dictionary containing analysis results for each technical indicator.
    """
    # Initialize availability flags
    sma_available = False
    rsi_available = False
    macd_available = False
    obv_available = False
    adx_available = False
    bbands_available = False

    # Calculate SMA
    if 'Close' in data.columns:
        data['SMA_20'] = ta.sma(data['Close'], length=20)
        data['SMA_50'] = ta.sma(data['Close'], length=50)
        data['SMA_200'] = ta.sma(data['Close'], length=200)
        sma_available = data[['SMA_20', 'SMA_50', 'SMA_200']].notna().any().any()

    # Calculate RSI
    if 'Close' in data.columns:
        data['RSI'] = ta.rsi(data['Close'], length=14)
        rsi_available = 'RSI' in data.columns and data['RSI'].notna().any()

    # Calculate MACD
    macd = ta.macd(data['Close'])
    if macd is not None and all(col in macd.columns for col in ['MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9']):
        data['MACD'] = macd['MACD_12_26_9']
        data['MACD_signal'] = macd['MACDs_12_26_9']
        data['MACD_hist'] = macd['MACDh_12_26_9']
        macd_available = True
    
    print(data)

    # Calculate OBV
    if 'Close' in data.columns and 'Volume' in data.columns:
        data['OBV'] = ta.obv(data['Close'], data['Volume'])
        obv_available = 'OBV' in data.columns and data['OBV'].notna().any()

    # Calculate ADX
    adx = ta.adx(data['High'], data['Low'], data['Close'])
    if adx is not None and 'ADX_14' in adx.columns:
        data['ADX'] = adx['ADX_14']
        adx_available = True

    # Calculate Bollinger Bands
    bbands = ta.bbands(data['Close'], length=20, std=2)
    if bbands is not None and all(col in bbands.columns for col in ['BBU_20_2.0', 'BBM_20_2.0', 'BBL_20_2.0']):
        data['upper_band'] = bbands['BBU_20_2.0']
        data['middle_band'] = bbands['BBM_20_2.0']
        data['lower_band'] = bbands['BBL_20_2.0']
        bbands_available = True

    # Resample data
    data = data.resample('W').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'SMA_20': 'last',
        'SMA_50': 'last',
        'SMA_200': 'last',
        'RSI': 'last',
        'MACD': 'last',
        'MACD_signal': 'last',
        'MACD_hist': 'last',
        'OBV': 'last',
        'ADX': 'last',
        'upper_band': 'last',
        'middle_band': 'last',
        'lower_band': 'last'
    })

    # Prepare data for analysis
    recent_data = data
    results = {
        "bd_result": bollingerbands(ticker, recent_data[["Open", "High", "Low", "Close", "Volume", "upper_band", "middle_band", "lower_band"]].to_markdown()),
        "sma_result": SMA(ticker, recent_data[["Open", "High", "Low", "Close", "SMA_20", "SMA_50", "SMA_200"]].to_markdown()) if sma_available else "SMA analysis not available.",
        "rsi_result": RSI(ticker, recent_data[["Open", "High", "Low", "Close", "RSI"]].to_markdown()) if rsi_available else "RSI analysis not available.",
        "macd_result": MACD(ticker, recent_data[["Open", "High", "Low", "Close", "MACD", "MACD_signal", "MACD_hist"]].to_markdown()) if macd_available else "MACD analysis not available.",
        "obv_result": OBV(ticker, recent_data[["Open", "High", "Low", "Close", "Volume", "OBV"]].to_markdown()) if obv_available else "OBV analysis not available.",
        "adx_result": ADX(ticker, recent_data[["Open", "High", "Low", "Close", "ADX"]].to_markdown()) if adx_available else "ADX analysis not available."
    }

    availability = {
        "sma_available": sma_available,
        "rsi_available": rsi_available,
        "macd_available": macd_available,
        "obv_available": obv_available,
        "adx_available": adx_available,
        "bbands_available": bbands_available
    }

    return results, recent_data, availability


def update_progress(progress_bar, stage, progress, message):
    progress_bar.progress(progress)
    st.text(message)
    st.empty()

def plot_sma(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='SMA 20', line=dict(color='orange', dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], mode='lines', name='SMA 50', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_200'], mode='lines', name='SMA 200', line=dict(color='green', dash='dash')))
    return fig

# Function to plot Bollinger Bands
def plot_bbands(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['upper_band'], mode='lines', name='Upper Band', line=dict(color='cyan', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['middle_band'], mode='lines', name='Middle Band', line=dict(color='magenta', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['lower_band'], mode='lines', name='Lower Band', line=dict(color='cyan', dash='dot')))
    return fig

# Function to plot RSI
def plot_rsi(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')))
    fig.add_hline(y=70, line=dict(color='red', dash='dash'))
    fig.add_hline(y=30, line=dict(color='green', dash='dash'))
    return fig

# Function to plot MACD
def plot_macd(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], mode='lines', name='MACD Signal', line=dict(color='red')))
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_hist'], name='MACD Histogram', marker_color='gray', opacity=0.5))
    return fig

# Function to plot OBV
def plot_obv(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['OBV'], mode='lines', name='OBV', line=dict(color='brown')))
    return fig

# Function to plot ADX
def plot_adx(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['ADX'], mode='lines', name='ADX', line=dict(color='orange')))
    return fig


if __name__ == "__main__":
    stock_page()