# IQRA Competition - Data Analysis & Recommendation Engine

A comprehensive Flask-based web application with 7 core features for intelligent data analysis, filtering, recommendations, and visualization.

## 🎯 Features Implemented

### 1. **Data Sanitizer (Pandas Cleaning)** ✅
- Automatically removes duplicate records
- Handles missing values (fills numeric with mean, strings with 'Unknown')
- Auto-detects and converts data types
- Cleans and validates data on load

### 2. **Dynamic Filtering via Flask UI** ✅
- **Sales Tool**: Filter by Category and Date Range
- **Health Tool**: Filter by Age Group (0-18, 19-35, 36-60, 60+) and Condition
- Real-time filter application
- Reset functionality

### 3. **AI Recommendation Engine** ✅
- Sales recommendations:
  - Top-selling category identification
  - Revenue analysis
  - Pricing strategy suggestions
- Health recommendations:
  - Most common condition detection
  - Health alerts (cholesterol, etc.)
  - Population demographic insights

### 4. **Automated Statistical Summary** ✅
- Quick Stats Dashboard showing:
  - Total records and columns
  - Sales metrics (total, average, min, max)
  - Health metrics (patient count, average age, conditions)
- Updated dynamically with filters

### 5. **File Export Capability** ✅
- Export filtered data as CSV
- Export filtered data as JSON
- Maintains all applied filters in export

### 6. **Search Functionality** ✅
- Full-text search across all columns
- Case-insensitive matching
- Returns matching records preview
- Search result count

### 7. **Interactive Visualizations** ✅
- **Bar Charts**: Category/Condition distribution
- **Line Charts**: Trend analysis over time
- **Pie Charts**: Distribution percentages
- Built with Plotly for interactivity
- Displays directly in Flask app

---

## 📋 Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open in Browser
Navigate to: `http://localhost:5000`

---

## 🚀 Usage Guide

### Starting with Sales Tool:
1. Click **"📊 Sales Tool"** button
2. Statistics load automatically
3. Use filters to refine data:
   - Select Category (Electronics, Clothing, Food, Home)
   - Set Date Range
4. View recommendations and charts
5. Export filtered results

### Starting with Health Tool:
1. Click **"⚕️ Health Tool"** button
2. Statistics load automatically
3. Use filters to refine data:
   - Select Age Group
   - Select Medical Condition
4. View recommendations and charts
5. Export filtered results

### Using Features:

**📊 Apply Filters**
- Select filter criteria
- Click "Apply Filters"
- Data updates in real-time

**🔎 Search Data**
- Enter search term
- Click "Search"
- View matching records

**📈 Interactive Charts**
- Click "Bar Chart", "Line Chart", or "Pie Chart"
- Hover over data points for details
- Charts respond to current filters

**📥 Export Data**
- Click "Export as CSV" or "Export as JSON"
- File downloads automatically

**💡 AI Recommendations**
- Auto-generated based on data analysis
- Shows action items and insights

---

## 📊 Sample Data

### Sales Data Includes:
- Date (2024-01-01 to 2024-07-20)
- Category (Electronics, Clothing, Food, Home)
- Sales (amount in dollars)
- Quantity (units sold)
- Region (North, South, East, West)

### Health Data Includes:
- Age (18-80 years)
- Cholesterol (150-300 mg/dL)
- Blood Pressure (Normal, Pre-High, High)
- Condition (Diabetes, Heart Disease, Hypertension, Normal)
- Gender (Male, Female)

---

## 📁 Project Structure

```
competition_iqra/
├── app.py                  # Flask backend with all functions
├── tamplates.html         # Interactive UI dashboard
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🔧 Key Functions

### Backend (`app.py`)

**Data Processing:**
- `sanitize_data(df)` - Cleans and validates data
- `dynamic_filter(df, tool_type, filters)` - Applies dynamic filters
- `search_data(df, search_term)` - Full-text search

**Analysis:**
- `get_recommendations(df, tool_type)` - AI recommendations
- `get_statistics(df, tool_type)` - Statistical summary

**Export:**
- `export_to_csv(df, filename)` - CSV export
- `export_to_excel(df, filename)` - Excel export

**Visualization:**
- `create_sales_chart(df, chart_type)` - Sales charts
- `create_health_chart(df, chart_type)` - Health charts

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main dashboard |
| `/api/tool_select` | POST | Select tool & load initial data |
| `/api/filter` | POST | Apply filters |
| `/api/search` | POST | Search functionality |
| `/api/chart` | POST | Generate charts |
| `/api/export` | POST | Export data |
| `/api/statistics` | POST | Get statistics |

---

## 💡 Tips

- All filters are optional - leave empty to view all data
- Charts update based on current filtered view
- Search is case-insensitive
- Exports include all applied filters
- Recommendations update based on filtered data

---

## 🎓 Competition Features

This tool demonstrates:
✅ Data cleaning & preprocessing (Pandas)
✅ Dynamic filtering & search
✅ AI-powered recommendations
✅ Statistical analysis
✅ Data export capabilities
✅ Interactive visualizations (Plotly)
✅ Full-stack web application (Flask)
✅ Responsive UI design

---

## ⚙️ System Requirements

- Python 3.8+
- Flask 2.3.3
- Pandas 2.0.3
- Plotly 5.17.0
- Modern web browser

---

## 📝 Notes

- Sample data is randomly generated each run
- Filters are case-sensitive
- All visualizations are interactive
- Export maintains filter context

Happy analyzing! 🎉
