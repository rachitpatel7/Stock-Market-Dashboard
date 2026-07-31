# 📈 Real-Time Stock Dashboard

An interactive web-based stock market dashboard built with **Streamlit**, **Plotly**, and **yfinance**. Track live prices, visualize historical trends, and apply technical indicators — all from your browser.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🔍 **Ticker lookup** — search any publicly traded stock symbol
- ⏱️ **Flexible time ranges** — 1 day, 1 week, 1 month, 1 year, or max
- 📊 **Multiple chart types** — Candlestick or Line
- 📌 **Live watchlist** — track additional symbols in the sidebar, fully customizable
- 📉 **Key metrics at a glance** — last price, change, % change, high, low, volume

### Technical Indicators
- Simple Moving Average (SMA 20)
- Exponential Moving Average (EMA 20)
- Relative Strength Index (RSI 14)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands

### Visualization
- Price chart with indicator overlays
- Volume subplot, color-coded by bullish/bearish sessions
- Dedicated momentum tab for RSI/MACD
- Tabbed layout: **Price & Volume | Momentum | Historical Data | Indicator Values**

### Extras
- ⬇️ CSV export of historical data
- 🕒 Last-updated timestamp
- ⚡ Caching for faster reloads
- 🛡️ Error handling for invalid tickers or missing data

---

## 🖥️ Demo

*(Add a screenshot or GIF of the app here)*

```
![Dashboard Screenshot](assets/screenshot.png)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run stock_dashboard.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📦 Requirements

```
streamlit
plotly
pandas
yfinance
ta
```

Save this as `requirements.txt` in your repo root.

---

## 🛠️ Tech Stack

| Layer            | Tool         |
|-------------------|--------------|
| UI / App Framework | Streamlit   |
| Charting           | Plotly      |
| Data Source        | yfinance (Yahoo Finance API) |
| Technical Analysis | `ta` library |
| Data Handling      | pandas       |

---

## 📁 Project Structure

```
├── stock_dashboard.py    # Main Streamlit application
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🎯 Use Cases

- Retail investors doing quick technical analysis
- Students learning about stock market indicators
- A lightweight, self-hosted alternative to commercial charting tools

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for bug fixes, new indicators, or UI improvements.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a PR

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This dashboard is for educational and informational purposes only. It is **not financial advice**. Always do your own research before making investment decisions.
