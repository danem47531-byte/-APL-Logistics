📦 APL Logistics Dashboard - Auto-Loading Version
An interactive Streamlit dashboard for analyzing APL logistics data with automatic data loading from GitHub - no manual CSV upload needed!
✨ What's New
✅ Automatic Data Loading - CSV loads automatically from GitHub zip file
✅ Geography Section Added - Interactive maps with location-based analytics
✅ No File Upload Needed - Data loads on app startup
✅ Fast Performance - Data cached for quick reloads
🚀 Features
📊 Interactive KPI Dashboard - Real-time metrics and performance indicators
💰 Financial Analysis - Revenue, profit, and margin tracking
🚚 Shipping Performance - Delivery efficiency and SLA monitoring
🔮 Predictive Insights - Statistical analysis and anomaly detection
🗺️ Geographic Distribution - Interactive maps with customer locations
📋 Detailed Reports - Exportable data tables and visualizations
🎨 Beautiful UI - Modern gradient styling and responsive design
📋 Requirements
Python 3.11 (recommended for Streamlit Cloud)
Required packages are in `requirements.txt`
☁️ How to Deploy to Streamlit Cloud
Step 1: Prepare Your GitHub Repository
Create a new repository on GitHub
Upload these files to your repository:
`app.py` (the main application)
`requirements.txt`
`README.md`
`.gitignore`
`.python-version`
`APL_Logistics.zip` (your 57MB CSV file, zipped)
Step 2: Update the GitHub URL in app.py
IMPORTANT: Before deploying, you need to update line 97 in `app.py`:
```python
# REPLACE THIS URL with your actual GitHub raw file URL
GITHUB_ZIP_URL = "https://github.com/YOUR-USERNAME/YOUR-REPO-NAME/raw/main/APL_Logistics.zip"
```
How to get your GitHub raw file URL:
Go to your GitHub repository
Click on `APL_Logistics.zip`
Click the "Download" or "Raw" button
Copy the URL from the browser address bar
It should look like: `https://github.com/username/repo-name/raw/main/APL_Logistics.zip`
Example:
```python
GITHUB_ZIP_URL = "https://github.com/johndoe/apl-dashboard/raw/main/APL_Logistics.zip"
```
Step 3: Deploy on Streamlit Cloud
Go to share.streamlit.io
Sign in with GitHub
Click "New app"
Select your repository
Branch: `main`
Main file path: `app.py`
Click "Deploy"
Step 4: Wait and Enjoy!
Deployment takes 2-3 minutes
The app will automatically download and load the CSV from GitHub
No manual file upload needed - the dashboard is ready to use!
🔧 Local Installation (Optional)
If you want to run it locally:
Clone this repository:
```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```
Install dependencies:
```bash
   pip install -r requirements.txt
   ```
Update the GitHub URL in app.py (line 97)
Run the app:
```bash
   streamlit run app.py
   ```
📊 Data Requirements
Your CSV file should include these columns:
`Days for shipping (real)`
`Days for shipment (scheduled)`
`Delivery Status`
`Late_delivery_risk`
`Sales`
`Order Profit Per Order`
`Order Item Profit Ratio`
`Shipping Mode`
`Order Region`
`Market`
`Customer Segment`
`Customer City`
`Customer Country`
`Latitude`
`Longitude`
📁 Why Use a Zip File?
The CSV file is 57.4MB, which is too large for GitHub's 50MB limit for direct file uploads. By zipping it:
✅ File size reduces to ~15-20MB (easily under GitHub's limit)
✅ Faster downloads from GitHub
✅ App automatically extracts it on load
🎯 New Geography Features
The geography tab includes:
🗺️ Interactive Maps - Scatter map with customer locations
🎨 Multiple Color Options - Color by delivery status, SLA, sales, profit, or delay
🌍 Top Cities Analysis - See which cities have the most orders
🌐 Country Performance - Compare metrics across countries
📊 Regional Charts - Visualize regional distribution of any metric
🔧 Troubleshooting
Error: "404 Not Found" when loading data
Solution:
Make sure `APL_Logistics.zip` is in your GitHub repository
Check that the URL in app.py (line 97) is correct
The URL should be the raw file URL, not the GitHub page URL
Error: "Failed to download and build packages"
Solution:
Make sure you have `.python-version` file with:
```
3.11
```
Map not showing data
Solution:
Check that your CSV has valid `Latitude` and `Longitude` columns
Some filters might exclude all geographic data - try resetting filters
🛠️ Technologies Used
Streamlit - Web framework
Pandas - Data processing
Plotly - Interactive visualizations (including maps)
NumPy - Numerical computations
Requests - Download zip file from GitHub
Zipfile - Extract CSV from zip
📝 License
MIT License - Feel free to use and modify!
🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first.
---
Made with ❤️ using Streamlit
📧 Need Help?
If you encounter any issues:
Check that all files are uploaded to GitHub
Verify the GitHub URL in app.py is correct
Make sure `.python-version` file exists
Check Streamlit Cloud deployment logs for errors
