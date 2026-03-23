📊 Strategic Finance Engine (3-Statement Model)
A robust, Python-powered financial modeling engine designed to automate the transition from raw ERP data to high-level strategic insights. This tool bridges the gap between traditional accounting and Finance 4.0 by integrating automated forecasting, interactive scenario modeling, and dynamic headcount planning.

🚀 Key Features
Automated 3-Statement Integration: Fully linked Income Statement, Balance Sheet, and Indirect Cash Flow Statement.

Strategic Operational Drivers: Interactive sidebar in Streamlit to stress-test Revenue Growth, COGS efficiency, and OpEx scaling.

Liquidity & Efficiency Analytics: Built-in logic for Cash Runway (in months) and the Rule of 40 (Growth + EBITDA Margin) to assess SaaS/Scale-up health.

Headcount Planner: Personnel cost and FTE count projections dynamically linked to revenue scale.

Smart Formatting: Custom row-aware formatting engine that intelligently distinguishes between Currency (€) and Percentages (%).

🛠️ Technical Stack
Language: Python 3.14+

Data Processing: Pandas, NumPy

Web Interface: Streamlit

DevOps: Structured directory logic (core/, data/raw/) for clean deployment.

📂 Project Structure
Plaintext
3-statement-engine/
├── app.py                # Streamlit UI & Data Formatting Logic
├── generate_test_data.py # Mock ERP Ledger Generator
├── core/
│   └── engine.py         # Financial Logic & Forecasting Engine
└── data/
    └── raw/              # Source for erp_export_pro.csv
🚦 Getting Started
1. Prerequisites
Ensure you have the required libraries installed:

Bash
pip install pandas numpy streamlit
2. Generate the Ledger
Run the data script to create a synthetic 5-year historical ERP export:

Bash
python generate_test_data.py
3. Launch the Model
Fire up the interactive dashboard:

Bash
streamlit run app.py
📈 Strategic Context
This model was developed to support financial leadership in high-growth environments (specifically targeting the Berlin scale-up ecosystem). It focuses on Revenue Assurance and Burn Management, providing a clear "Ops Center" view for CFOs and Finance Controllers to make data-driven relocation and scaling decisions.