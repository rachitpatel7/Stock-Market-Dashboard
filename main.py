import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta

##########################################################################################
## PART 1: Data fetching, processing, metrics, and technical indicators                 ##
##########################################################################################

INTERVAL_MAPPING = {
    '1d': '1m',
    '1wk': '30m',
    '1mo': '1d',
    '1y': '1wk',
    'max': '1wk',
}


@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data(ticker, period, interval):
    """Download data from yfinance. Always returns a DataFrame (empty on failure)."""
    try:
        end_date = datetime.now()
        if period == '1wk':
            start_date = end_date - timedelta(days=7)
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
        else:
            data = yf.download(ticker, period=period, interval=interval, progress=False)
    except Exception:
        return pd.DataFrame()

    # Newer yfinance versions return MultiIndex columns even for a single ticker.
    # Flatten them so downstream code always gets plain scalars/Series.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


def process_data(data):
    """Make the index timezone-aware (US/Eastern) and turn it into a normal column."""
    if data is None or data.empty:
        return pd.DataFrame()
    data = data.copy()
    if data.index.tz is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('US/Eastern')
    data.reset_index(inplace=True)
    data.rename(columns={data.columns[0]: 'Datetime'}, inplace=True)
    return data


def calculate_metrics(data):
    last_close = float(data['Close'].iloc[-1])
    prev_close = float(data['Close'].iloc[0])
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100 if prev_close else 0.0
    high = float(data['High'].max())
    low = float(data['Low'].min())
    volume = int(data['Volume'].sum())
    return last_close, change, pct_change, high, low, volume


def add_technical_indicators(data, sma=False, ema=False, rsi=False, macd=False, bbands=False):
    data = data.copy()
    if sma:
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
    if ema:
        data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
    if rsi:
        data['RSI_14'] = ta.momentum.rsi(data['Close'], window=14)
    if macd:
        macd_ind = ta.trend.MACD(data['Close'])
        data['MACD'] = macd_ind.macd()
        data['MACD_signal'] = macd_ind.macd_signal()
        data['MACD_diff'] = macd_ind.macd_diff()
    if bbands:
        bb = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
        data['BB_upper'] = bb.bollinger_hband()
        data['BB_lower'] = bb.bollinger_lband()
    return data


###############################################
## PART 2: Dashboard layout                   ##
###############################################

st.set_page_config(page_title="Real-Time Stock Dashboard", page_icon="📈", layout="wide")
st.title('📈 Real-Time Stock Dashboard')

# 2A: SIDEBAR PARAMETERS ############

st.sidebar.header('Chart Parameters')
ticker = st.sidebar.text_input('Ticker', 'ADBE').strip().upper()
time_period = st.sidebar.selectbox('Time Period', list(INTERVAL_MAPPING.keys()), index=2)
chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])
indicators = st.sidebar.multiselect(
    'Technical Indicators',
    ['SMA 20', 'EMA 20', 'RSI 14', 'MACD', 'Bollinger Bands'],
    default=['SMA 20'],
)
update_clicked = st.sidebar.button('🔄 Update', use_container_width=True)

# 2B: MAIN CONTENT AREA ############

# Fetch fresh data only when the button is clicked, but keep it in session_state so
# the chart/tables don't vanish on the next rerun (e.g. when you tweak the indicators).
if update_clicked:
    raw = fetch_stock_data(ticker, time_period, INTERVAL_MAPPING[time_period])
    raw = process_data(raw)
    if raw.empty:
        st.error(f"No data found for '{ticker}'. Check the symbol and try again.")
        st.session_state['raw_data'] = None
    else:
        st.session_state['raw_data'] = raw
        st.session_state['ticker'] = ticker
        st.session_state['time_period'] = time_period

if st.session_state.get('raw_data') is not None:
    data = add_technical_indicators(
        st.session_state['raw_data'],
        sma='SMA 20' in indicators,
        ema='EMA 20' in indicators,
        rsi='RSI 14' in indicators,
        macd='MACD' in indicators,
        bbands='Bollinger Bands' in indicators,
    )
    used_ticker = st.session_state['ticker']
    used_period = st.session_state['time_period']

    last_close, change, pct_change, high, low, volume = calculate_metrics(data)

    st.metric(
        label=f"{used_ticker} Last Price",
        value=f"{last_close:.2f} USD",
        delta=f"{change:.2f} ({pct_change:.2f}%)",
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("High", f"{high:.2f} USD")
    col2.metric("Low", f"{low:.2f} USD")
    col3.metric("Volume", f"{volume:,}")

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Price & Volume", "📊 Momentum", "🧾 Historical Data", "🧮 Indicator Values"])

    with tab1:
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.03, row_heights=[0.7, 0.3],
        )

        if chart_type == 'Candlestick':
            fig.add_trace(
                go.Candlestick(
                    x=data['Datetime'], open=data['Open'], high=data['High'],
                    low=data['Low'], close=data['Close'], name=used_ticker,
                ),
                row=1, col=1,
            )
        else:
            fig.add_trace(
                go.Scatter(x=data['Datetime'], y=data['Close'], mode='lines', name=used_ticker),
                row=1, col=1,
            )

        if 'SMA_20' in data:
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['SMA_20'], name='SMA 20', line=dict(width=1.5)), row=1, col=1)
        if 'EMA_20' in data:
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['EMA_20'], name='EMA 20', line=dict(width=1.5)), row=1, col=1)
        if 'BB_upper' in data:
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['BB_upper'], name='BB Upper', line=dict(width=1, dash='dot')), row=1, col=1)
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['BB_lower'], name='BB Lower', line=dict(width=1, dash='dot'), fill='tonexty'), row=1, col=1)

        volume_colors = ['#26a69a' if c >= o else '#ef5350' for o, c in zip(data['Open'], data['Close'])]
        fig.add_trace(go.Bar(x=data['Datetime'], y=data['Volume'], name='Volume', marker_color=volume_colors), row=2, col=1)

        fig.update_layout(
            title=f'{used_ticker} {used_period.upper()} Chart',
            height=650,
            xaxis_rangeslider_visible=False,
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
        )
        fig.update_yaxes(title_text='Price (USD)', row=1, col=1)
        fig.update_yaxes(title_text='Volume', row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        has_rsi = 'RSI_14' in data
        has_macd = 'MACD' in data
        if not has_rsi and not has_macd:
            st.info("Select **RSI 14** or **MACD** from the sidebar to see momentum charts here.")
        if has_rsi:
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(x=data['Datetime'], y=data['RSI_14'], name='RSI 14'))
            rsi_fig.add_hline(y=70, line_dash='dash', line_color='red')
            rsi_fig.add_hline(y=30, line_dash='dash', line_color='green')
            rsi_fig.update_layout(title='RSI (14)', height=300, yaxis_range=[0, 100])
            st.plotly_chart(rsi_fig, use_container_width=True)
        if has_macd:
            macd_fig = go.Figure()
            macd_fig.add_trace(go.Scatter(x=data['Datetime'], y=data['MACD'], name='MACD'))
            macd_fig.add_trace(go.Scatter(x=data['Datetime'], y=data['MACD_signal'], name='Signal'))
            macd_fig.add_trace(go.Bar(x=data['Datetime'], y=data['MACD_diff'], name='Histogram'))
            macd_fig.update_layout(title='MACD', height=300)
            st.plotly_chart(macd_fig, use_container_width=True)

    with tab3:
        st.dataframe(data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']], use_container_width=True)
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download CSV", data=csv,
            file_name=f"{used_ticker}_{used_period}.csv", mime='text/csv',
        )

    with tab4:
        indicator_cols = ['Datetime'] + [
            c for c in ['SMA_20', 'EMA_20', 'RSI_14', 'MACD', 'MACD_signal', 'MACD_diff', 'BB_upper', 'BB_lower']
            if c in data.columns
        ]
        if len(indicator_cols) > 1:
            st.dataframe(data[indicator_cols], use_container_width=True)
        else:
            st.info("No technical indicators selected.")
else:
    st.info("👈 Enter a ticker in the sidebar and click **Update** to load data.")


# 2C: SIDEBAR WATCHLIST ############

st.sidebar.header('📌 Watchlist')
watchlist_input = st.sidebar.text_input("Symbols (comma-separated)", "AAPL,GOOGL,AMZN,MSFT")
watchlist = [s.strip().upper() for s in watchlist_input.split(',') if s.strip()]

for symbol in watchlist:
    wdata = process_data(fetch_stock_data(symbol, '1d', '1m'))
    if wdata.empty:
        st.sidebar.warning(f"{symbol}: no data available")
        continue
    last_price = float(wdata['Close'].iloc[-1])
    open_price = float(wdata['Open'].iloc[0])
    w_change = last_price - open_price
    w_pct_change = (w_change / open_price) * 100 if open_price else 0.0
    st.sidebar.metric(symbol, f"{last_price:.2f} USD", f"{w_change:.2f} ({w_pct_change:.2f}%)")

st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

st.sidebar.subheader('About')
st.sidebar.info('This dashboard provides stock data and technical indicators for various time periods. Use the sidebar to customize your view.')