# 📦 APL Logistics Dashboard

An interactive Streamlit dashboard for analyzing APL logistics data with advanced analytics and visualizations.

## 🚀 Live Demo

**Deploy this app to Streamlit Cloud:** [Follow instructions below](#how-to-deploy-to-streamlit-cloud)

## ✨ Features

- 📊 **Interactive KPI Dashboard** - Real-time metrics and performance indicators
- 💰 **Financial Analysis** - Revenue, profit, and margin tracking
- 🚚 **Shipping Performance** - Delivery efficiency and SLA monitoring
- 🔮 **Predictive Insights** - Statistical analysis and anomaly detection
- 📋 **Detailed Reports** - Exportable data tables and visualizations
- 🎨 **Beautiful UI** - Modern gradient styling and responsive design

## 📋 Requirements

- Python 3.8+
- Required packages are in `requirements.txt`

## 🔧 Local Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. **Upload your CSV file** when the app opens in your browser

## ☁️ How to Deploy to Streamlit Cloud

### Step 1: Upload to GitHub

1. Create a new repository on GitHub
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Main file path: `app.py`
6. Click **"Deploy"**

### Step 3: Use the App

1. Wait for deployment (1-2 minutes)
2. Upload your CSV file when the app loads
3. The app will process your data and show the dashboard!

## 📊 Data Requirements

Your CSV file should include these columns:

- `Days for shipping (real)`
- `Days for shipment (scheduled)`
- `Delivery Status`
- `Late_delivery_risk`
- `Sales`
- `Order Profit Per Order`
- `Order Item Profit Ratio`
- `Shipping Mode`
- `Order Region`
- `Market`
- `Customer Segment`
- `Customer City`
- `Customer Country`
- `Latitude`
- `Longitude`

## 📁 About the Large CSV File

**The CSV file is NOT included in this repository** because:
- It's 57.4MB (too large for GitHub's 50MB limit)
- Data files should be uploaded directly to the app
- Keeps the repository clean and fast

**To use the app:**
1. Keep your CSV file on your local computer
2. Upload it through the app interface
3. The app processes it in real-time

## 🎯 Usage

1. **Upload Data**: Click "Browse files" and select your APL Logistics CSV
2. **Apply Filters**: Use the sidebar to filter by shipping mode, region, market, etc.
3. **Explore Tabs**: Navigate through different analysis sections
4. **Export Reports**: Download filtered data and reports as CSV files

## 🛠️ Technologies Used

- **Streamlit** - Web framework
- **Pandas** - Data processing
- **Plotly** - Interactive visualizations
- **NumPy** - Numerical computations

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

**Made with ❤️ using Streamlit**
