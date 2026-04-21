# 📦 APL Logistics Dashboard

A comprehensive, interactive analytics dashboard for logistics and supply chain performance monitoring, built with Python and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Overview

The APL Logistics Dashboard is a powerful data analytics application designed to provide real-time insights into logistics operations, delivery performance, financial metrics, and supply chain optimization. Built with Streamlit, this dashboard offers an intuitive interface for monitoring KPIs, analyzing trends, and making data-driven decisions.

### Key Features

- **📊 Real-time Performance Monitoring**: Track delivery performance, SLA compliance, and operational metrics
- **💰 Financial Analysis**: Monitor revenue, profit margins, and cost efficiency across different dimensions
- **🚚 Shipping Analytics**: Analyze delivery modes, on-time performance, and delay patterns
- **🌍 Geographic Insights**: Interactive maps and regional performance breakdowns
- **🔮 Predictive Analytics**: Risk assessment and delivery performance predictions
- **📈 Multi-dimensional Analysis**: Customer segments, markets, regions, and shipping modes
- **📥 Exportable Reports**: Download detailed reports in CSV format
- **🎨 Modern UI**: Clean, gradient-based interface with interactive visualizations

## 🚀 Live Demo

[(https://ffdhr6abvccshxb8sxxciq.streamlit.app/)]

## 🛠️ Tech Stack

- **Frontend Framework**: [Streamlit](https://streamlit.io/) - Interactive web applications
- **Data Processing**: [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- **Visualizations**: [Plotly](https://plotly.com/) - Interactive charts and graphs
- **Numerical Computing**: [NumPy](https://numpy.org/) - Numerical operations
- **File Handling**: [openpyxl](https://openpyxl.readthedocs.io/) - Excel file support

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/danem47531-byte/-APL-Logistics
cd apl-logistics-dashboard
```

### 2. Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎯 Setup & Configuration

### Data Setup

The dashboard automatically loads data from a GitHub repository. Follow these steps:

1. **Prepare Your Data**:
   - Ensure your logistics data is in CSV format
   - Compress it into a ZIP file named `APL_Logistics.zip`
   - Upload the ZIP file to your GitHub repository

2. **Update the Data URL**:
   - Open `app.py`
   - Locate line 98 and update the URL:
   ```python
   GITHUB_ZIP_URL = "https://github.com/danem47531-byte/-APL-Logistics/raw/main/APL_Logistics.zip"
   ```

### Required Data Columns

Your CSV file should include the following columns:
- `Days for shipping (real)` - Actual shipping duration
- `Days for shipment (scheduled)` - Scheduled shipping duration
- `Delivery Status` - Status of delivery
- `Late_delivery_risk` - Risk indicator for late delivery
- `Order Region` - Geographic region
- `Market` - Market segment
- `Shipping Mode` - Method of shipping
- `Customer Segment` - Customer category
- `Sales` - Sales amount
- `Order Profit Per Order` - Profit per order

[See full column list in documentation]

## 🚀 Running the Application

### Local Development

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Production Deployment

#### Streamlit Community Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy directly from your repository
4. Add any secrets in the Streamlit Cloud dashboard

#### Alternative Deployment Options
- **Heroku**: Use `Procfile` for deployment
- **AWS EC2**: Deploy on cloud server
- **Docker**: Containerize the application

## 📊 Dashboard Features

### 1. Executive Overview
- Total orders, revenue, and profit metrics
- Overall on-time delivery rate
- Late delivery risk indicators
- Delivery status distribution
- Trend analysis and sparklines

### 2. Shipping Performance Analysis
- Shipping mode comparison
- Delay analysis and distribution
- Average shipping times
- SLA compliance tracking
- Performance trends over time

### 3. Financial Analysis
- Revenue and profit breakdowns
- Profit margin analysis
- Regional financial performance
- Market-wise revenue distribution
- Customer segment profitability

### 4. Predictive Insights
- Late delivery risk prediction
- Delay probability analysis
- Performance forecasting
- Risk factor identification
- Trend predictions

### 5. Geographic Analysis
- Interactive world map
- Regional performance metrics
- Country-level analytics
- Heat maps and geographic distributions

### 6. Detailed Reports
- Customizable data tables
- Shipping mode reports
- Regional performance reports
- Market analysis reports
- Customer segment analysis
- SLA breach details
- Top/bottom performers
- Downloadable CSV exports

## 🎨 Customization

### Styling

The dashboard uses custom CSS for styling. Modify the CSS section in `app.py` (lines 29-87) to customize:
- Color schemes
- Typography
- Card designs
- Hover effects
- Tab styles

### Metrics

Add or modify metrics in the `calculate_metrics()` function (lines 167-201).

### Visualizations

Create new charts using Plotly in the respective tab sections.

## 📁 Project Structure

```
apl-logistics-dashboard/
│
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── python-version         # Python version specification
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
└── APL_Logistics.zip     # Data file (not in repo)
```

## 🔐 Security Notes

- Never commit sensitive data (CSV/Excel files) to the repository
- Use `.gitignore` to exclude data files
- Store credentials in Streamlit secrets for production
- Use environment variables for sensitive configuration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [danem47531-byte](https://github.com/danem47531-byte)
- LinkedIn:  [Your LinkedIn]([https://linkedin.com/in/YOUR-PROFILE](https://www.linkedin.com/in/tridev-pal-74575a379/))

## 🙏 Acknowledgments

- Streamlit for the amazing framework
- Plotly for powerful visualizations
- The open-source community

## 📧 Contact

For questions or feedback, please open an issue or contact [tridevpal2@gmail.com](mailto:tridevpal2@gmail.com)

⭐ **If you find this project useful, please consider giving it a star!** ⭐
