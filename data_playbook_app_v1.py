# Required libraries: streamlit, pandas, plotly, Pillow (PIL), numpy, openpyxl, json
# Potentially required for full export features: python-pptx, reportlab (or fpdf2)
# Potentially required for database persistence: sqlalchemy, psycopg2-binary, etc.
# Potentially required for AI Integration: requests, or specific SDK
# Potentially required for Advanced Profiling: ydata-profiling
# Install them if you haven't:
# pip install streamlit pandas plotly Pillow numpy openpyxl python-pptx reportlab requests sqlalchemy psycopg2-binary ydata-profiling

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from PIL import Image
import io
import time  # For simulating processes
import datetime # For timestamps and date calculations
import json # For saving/loading state simulation
import os # For checking state file existence
import re # For validation
# import requests # Uncomment if using requests for AI API calls
# from sqlalchemy import create_engine # Example for DB persistence
# from ydata_profiling import ProfileReport # Example for advanced profiling

# --- App Configuration ---
st.set_page_config(
    page_title="Data Strategy Playbook", # Simplified title
    page_icon="🧭", # Updated icon
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help', # Placeholder
        'Report a bug': "https://www.example.com/bug", # Placeholder
        'About': "# Data Strategy Playbook v2.4\nAssess capabilities, build roadmaps, and integrate insights."
    }
)

# --- Theming Example (Create .streamlit/config.toml) ---
# [theme]
# primaryColor="#0072C6" # Example: Arcadis Blue
# backgroundColor="#f4f4f4" # Light grey background
# secondaryBackgroundColor="#ffffff" # White for containers
# textColor="#333333"
# font="sans serif"
# --- End Theming Example ---

# --- Constants & Configuration ---
APP_VERSION = "2.4 (Advanced Placeholders)"
STATE_FILE = "playbook_state.json" # File for persistence simulation
# --- [Database Placeholder] ---
# Example DB Connection String (use Streamlit secrets)
# DB_CONN_STRING = st.secrets.get("database_url", "sqlite:///playbook_data.db") # Default to SQLite file
# --- [End Database Placeholder] ---
DEFAULT_TIMEZONE = 'Europe/London'
DEFAULT_LOCATION = "London, England, UK"
# --- [AI Placeholder] ---
# AI_API_ENDPOINT = st.secrets.get("arcadis_gpt_endpoint", "YOUR_API_ENDPOINT_HERE") # Example using secrets
# AI_API_KEY = st.secrets.get("arcadis_gpt_key", "YOUR_API_KEY_HERE") # Example using secrets
# --- [End AI Placeholder] ---

# --- Set Timezone & Location ---
# Attempt to set timezone, fallback gracefully
try:
    APP_TIMEZONE = DEFAULT_TIMEZONE
    pd.Timestamp.now(tz=APP_TIMEZONE)
except Exception:
    st.warning(f"Could not set timezone to '{DEFAULT_TIMEZONE}'. Using system default or UTC.")
    APP_TIMEZONE = None # Fallback
APP_LOCATION = DEFAULT_LOCATION

# --- Mock Data (Can be moved to a separate config file or loaded) ---
mock_sectors = ["Mobility", "Resilience", "Utilities", "Healthcare", "Finance", "Retail", "Technology"]
mock_personas = ["Chief Data Officer (CDO)", "Head of Operations", "Lead Data Architect", "Marketing Manager", "Data Scientist", "Compliance Officer"]
mock_compliance_standards = ["GDPR", "CCPA", "HIPAA", "SOX", "ISO 27001", "Internal Policy v2.0"]
mock_maturity_levels = ["1 - Initial", "2 - Managed", "3 - Defined", "4 - Quantitatively Managed", "5 - Optimizing"]
mock_maturity_dimensions = ["Strategy & Vision", "Data Governance", "Data Quality", "Technology & Architecture", "People & Skills", "Data Usage & Analytics", "Innovation & Value"]
mock_roadmap_categories = ["Quick Wins (0-3 Months)", "Mid-Term (3-12 Months)", "Long-Term (12+ Months)"]
mock_effort_levels = ["Low", "Medium", "High", "Very High"]
mock_cost_levels = ["$", "$$", "$$$", "$$$$", "$$$$$"]
mock_status_levels = ["Not Started", "Planning", "In Progress", "On Hold", "Completed", "Blocked"]

# Default Interview Questions (Now part of initial state)
default_interview_questions = {
    "Chief Data Officer (CDO)": [
        "What are the top 3 strategic goals data should support?", "How is data literacy perceived?", "Biggest roadblocks to being data-driven?",
        "How is data value measured?", "Current state of data governance maturity?", "Using data for competitive advantage?",
        "Needed investments in platforms/tools?", "Impact of privacy/security concerns?", "Role of AI/ML in future strategy?",
        "Satisfaction with reporting capabilities?"
    ],
    "Head of Operations": [
        "Reliability of operational reporting data?", "Biggest data quality issues impacting ops?", "Are dashboards timely and actionable?",
        "Manual effort in data collection/prep?", "Do front-line staff have needed data?", "Impact of data inconsistencies?",
        "Processes most improved with better data?", "Sufficient training on data tools?", "How is data used for operational KPIs?",
        "Challenges accessing cross-departmental data?"
    ],
    "Lead Data Architect": [
        "Current state of data architecture (scalability, flexibility)?", "Main data integration challenges?", "Documentation state of sources/pipelines?",
        "Is data storage optimized (cost/performance)?", "Process for introducing new data tech?", "Robustness of data security framework?",
        "Effectiveness of MDM/reference data management?", "Technical limitations hindering advanced analytics?", "How is data lineage tracked?",
        "Improvements needed in data modeling?"
    ],
     "Marketing Manager": [
        "Effectiveness of customer segmentation?", "Accuracy/timeliness of campaign tracking?", "Challenges accessing customer journey data?",
        "Confidence in personalization data?", "Ability to calculate marketing ROI accurately?", "Missing data sources for complete customer view?",
        "Ease of A/B testing and analysis?", "Right tools for marketing analytics?", "How does data inform content strategy?",
        "Data privacy constraints limiting activities?"
    ],
    "Data Scientist": [ # Added Persona
        "Accessibility of data for model building?", "Quality of data available for analysis?", "Availability of tools/platforms for ML?",
        "Collaboration process with domain experts?", "Process for deploying models into production?", "Monitoring model performance and drift?",
        "Challenges in feature engineering?", "Ethical considerations in model development?", "Availability of compute resources?",
        "Integration of external datasets?"
    ],
    "Compliance Officer": [ # Added Persona
        "Effectiveness of current data privacy controls?", "Process for handling data subject requests (DSRs)?", "Data retention policy adherence?",
        "Audit trails for sensitive data access?", "Training level on data compliance requirements?", "Challenges in monitoring regulatory changes?",
        "Data classification accuracy?", "Incident response plan for data breaches?", "Third-party data sharing risk management?",
        "Alignment with specific regulations (GDPR, CCPA etc.)?"
    ]
}

# Default RACI Data (Now part of initial state)
default_raci_data = {
    'Activity': ['Define Data Quality Rules', 'Approve Master Data Changes', 'Monitor Data Pipeline Health', 'Ensure GDPR Compliance', 'Develop Analytics Models', 'Manage Data Dictionary', 'Set Data Access Policy'],
    'CDO': ['A', 'A', 'R', 'A', 'S', 'A', 'A'],
    'Head of Operations': ['C', 'R', 'A', 'C', 'I', 'C', 'C'],
    'Lead Data Architect': ['S', 'I', 'R', 'I', 'R', 'R', 'S'],
    'Data Steward (Sales)': ['R', 'C', 'I', 'R', 'C', 'R', 'I'],
    'IT Security': ['I', 'I', 'C', 'R', 'I', 'I', 'R'],
    'Compliance Officer': ['C', 'I', 'I', 'A', 'C', 'C', 'A'], # Added Role
    'Data Scientist': ['I', 'I', 'C', 'I', 'A', 'C', 'I'] # Added Role
}
default_raci_legend = "R: Responsible, A: Accountable, C: Consulted, I: Informed, S: Support"

# Default Roadmap Items (Now part of initial state)
default_roadmap_items = {
    "Quick Wins (0-3 Months)": [
        {'ID': 'QW1', 'Task': 'Implement Basic Data Quality Dashboard', 'Owner': 'Data Steward (Sales)', 'Effort': 'Medium', 'Cost': '$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': ''},
        {'ID': 'QW2', 'Task': 'Document Top 5 Critical Data Elements', 'Owner': 'Lead Data Architect', 'Effort': 'Low', 'Cost': '$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': ''},
        {'ID': 'QW3', 'Task': 'Conduct Data Literacy Survey', 'Owner': 'CDO', 'Effort': 'Low', 'Cost': '$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': ''},
    ],
    "Mid-Term (3-12 Months)": [
        {'ID': 'MT1', 'Task': 'Establish Data Governance Council', 'Owner': 'CDO', 'Effort': 'High', 'Cost': '$$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': 'QW3'},
        {'ID': 'MT2', 'Task': 'Implement Master Data Management (MDM) for Customer Domain', 'Owner': 'Lead Data Architect', 'Effort': 'High', 'Cost': '$$$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': 'QW2,MT1'},
        {'ID': 'MT3', 'Task': 'Roll out Self-Service BI Tool Training', 'Owner': 'Head of Operations', 'Effort': 'Medium', 'Cost': '$$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': 'MT1'},
    ],
    "Long-Term (12+ Months)": [
        {'ID': 'LT1', 'Task': 'Migrate to Cloud Data Warehouse', 'Owner': 'Lead Data Architect', 'Effort': 'Very High', 'Cost': '$$$$$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': 'MT2'},
        {'ID': 'LT2', 'Task': 'Develop Predictive Maintenance Model', 'Owner': 'Data Scientist', 'Effort': 'High', 'Cost': '$$$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': 'LT1'},
        {'ID': 'LT3', 'Task': 'Integrate AI for Customer Personalization', 'Owner': 'Marketing Manager', 'Effort': 'High', 'Cost': '$$$$', 'Status': 'Not Started', 'Progress (%)': 0, 'Dependencies (IDs)': 'MT2,LT1'},
    ]
}

# Default Maturity Level Criteria (Example - needs detailed content)
default_maturity_criteria = {
    "Strategy & Vision": {
        1: "Data strategy undefined or ad-hoc.",
        2: "Basic awareness of data's potential; strategy documented but not integrated.",
        3: "Defined data strategy aligned with some business units; roadmap exists.",
        4: "Enterprise-wide data strategy actively managed, measured, and linked to business outcomes.",
        5: "Data strategy drives business innovation; predictive and adaptive."
    },
    "Data Governance": {
        1: "No formal governance; data managed locally.",
        2: "Basic policies emerging; some roles defined (e.g., DBAs).",
        3: "Formal governance program established; stewards assigned; core policies defined.",
        4: "Governance framework consistently enforced; metrics tracked; policies cover most data.",
        5: "Proactive governance integrated into lifecycle; automated policy enforcement; continuous improvement."
    },
     "Data Quality": {
        1: "Data quality unknown or poor; reactive fixes.",
        2: "Basic DQ checks implemented in some systems; awareness growing.",
        3: "Defined DQ processes and rules; monitoring in place for critical data.",
        4: "DQ metrics actively managed and reported; root cause analysis performed.",
        5: "Proactive DQ management embedded; automated remediation; DQ culture established."
    },
    "Technology & Architecture": {
        1: "Siloed systems; limited integration; basic reporting tools.",
        2: "Some data consolidation (e.g., basic data mart); standard reporting tools used.",
        3: "Defined architecture (e.g., data warehouse); integration patterns established; BI tools available.",
        4: "Modern, scalable platform (e.g., cloud DWH/Lakehouse); self-service analytics enabled; metadata management tools.",
        5: "Flexible, integrated architecture supporting advanced analytics/AI; automated data pipelines; data fabric concepts."
    },
    "People & Skills": {
        1: "Limited data skills; reliance on IT.",
        2: "Some analysts present; basic data literacy in pockets.",
        3: "Defined data roles; formal training programs initiated; growing data literacy.",
        4: "Data skills mapped and developed strategically; data literacy widespread; collaboration between IT/business.",
        5: "Data-centric culture; specialized skills available (AI/ML); continuous learning environment."
    },
    "Data Usage & Analytics": {
        1: "Basic historical reporting (spreadsheets, static reports).",
        2: "Standardized operational reporting; some ad-hoc querying.",
        3: "Interactive dashboards and BI; descriptive analytics common.",
        4: "Predictive analytics used in key areas; self-service analytics widely adopted.",
        5: "Prescriptive analytics and AI drive decisions; data monetization explored; embedded analytics."
    },
     "Innovation & Value": {
        1: "Data seen as an operational byproduct.",
        2: "Data used for basic cost savings or efficiency.",
        3: "Data recognized as an asset; used to improve specific processes or products.",
        4: "Data actively used for competitive advantage, new revenue streams, or strategic insights.",
        5: "Data is central to innovation; drives new business models; ecosystem data sharing."
    }
    # Add criteria for other dimensions...
}

# --- Helper Functions ---

def get_current_time():
    """Gets the current time, applying the app's timezone if possible."""
    try:
        # Ensure APP_TIMEZONE is valid before using
        if APP_TIMEZONE and isinstance(APP_TIMEZONE, str):
             # Test timezone validity silently
            pd.Timestamp.now(tz=APP_TIMEZONE)
            return pd.Timestamp.now(tz=APP_TIMEZONE)
        else:
            return pd.Timestamp.now() # Use local time if APP_TIMEZONE invalid/None
    except Exception: # Fallback if timezone string is invalid or not supported
        return pd.Timestamp.now() # Use local time

# --- [Database Placeholder Functions] ---
# def connect_db():
#     """Connects to the database using SQLAlchemy."""
#     try:
#         engine = create_engine(DB_CONN_STRING)
#         return engine
#     except Exception as e:
#         st.error(f"Database connection failed: {e}")
#         return None

# def load_state_from_db(engine, user_id="default"): # Example user ID
#     """Loads state for a user from the database."""
#     if engine is None: return False
#     st.info("DB Load: Not Implemented")
#     # Implement logic to query DB tables and populate session state
#     # Example: st.session_state.maturity_scores = pd.read_sql(...)
#     return False # Return True on success

# def save_state_to_db(engine, user_id="default"):
#     """Saves session state for a user to the database."""
#     if engine is None: return False
#     st.info("DB Save: Not Implemented")
#     # Implement logic to collect session state and write to DB tables
#     # Example: pd.DataFrame(st.session_state.maturity_scores).to_sql(...)
#     return False # Return True on success
# --- [End Database Placeholder Functions] ---

def save_app_state_json():
    """Saves relevant parts of the session state to a JSON file."""
    state_to_save = {}
    keys_to_persist = [
        'project_metadata', 'selected_sector', 'uploaded_logo_bytes', # Landing Page
        'editable_exec_summary', 'show_summary_edit', # Executive Summary
        'interview_confidence', 'interview_notes', 'interview_questions', 'uploaded_interview_files', # Interviews
        'dq_rules_config', # Data Analysis Config
        'governance_scores', 'raci_df_json', 'selected_compliance', 'business_glossary', # Governance
        'maturity_scores', 'maturity_evidence', 'maturity_assessments_history', # Maturity
        'roadmap_data', # Roadmap (store as dict of lists)
        'export_options', # Export Config
    ]
    for key in keys_to_persist:
        if key in st.session_state:
            value = st.session_state[key]
            # Handle specific types for JSON serialization
            if isinstance(value, pd.DataFrame):
                # Special handling for RACI index
                if key == 'raci_df_json':
                     state_to_save[key] = value.reset_index().to_json(orient='split')
                else:
                     state_to_save[key] = value.to_json(orient='split')
            elif key == 'roadmap_data' and isinstance(value, dict):
                state_to_save[key] = {cat: df.to_dict(orient='records')
                                      for cat, df in value.items() if isinstance(df, pd.DataFrame)}
            elif key == 'maturity_assessments_history' and isinstance(value, dict):
                state_to_save[key] = {ts.isoformat() if isinstance(ts, pd.Timestamp) else str(ts): scores
                                      for ts, scores in value.items()}
            elif isinstance(value, (dict, list, str, int, float, bool, type(None))):
                state_to_save[key] = value
            elif isinstance(value, np.integer): state_to_save[key] = int(value)
            elif isinstance(value, np.floating): state_to_save[key] = float(value)
            elif isinstance(value, np.ndarray): state_to_save[key] = value.tolist()

    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state_to_save, f, indent=4)
        return True
    except Exception as e:
        st.sidebar.error(f"Error saving state to JSON: {e}")
        return False

def load_app_state_json():
    """Loads app state from the JSON file into session state."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                loaded_state = json.load(f)

            for key, value in loaded_state.items():
                 # Handle special cases during loading
                if key == 'raci_df_json' and isinstance(value, str):
                    try:
                         df = pd.read_json(io.StringIO(value), orient='split')
                         # Check if 'Activity' column exists before setting index
                         if 'Activity' in df.columns:
                              st.session_state[key] = df.set_index('Activity')
                         else: # Handle older state format if necessary or warn
                              st.warning(f"Loaded RACI data for key '{key}' missing 'Activity' column. Using default.")
                              st.session_state[key] = pd.DataFrame(default_raci_data).set_index('Activity')
                    except Exception as e:
                         st.warning(f"Could not load RACI DataFrame state for key '{key}': {e}. Using default.")
                         st.session_state[key] = pd.DataFrame(default_raci_data).set_index('Activity')
                elif key == 'roadmap_data' and isinstance(value, dict):
                     try:
                          st.session_state[key] = {cat: pd.DataFrame(items) for cat, items in value.items()}
                     except Exception as e:
                          st.warning(f"Could not load Roadmap state for key '{key}': {e}. Using default.")
                          st.session_state[key] = {category: pd.DataFrame(items) for category, items in default_roadmap_items.items()}
                elif key == 'maturity_assessments_history' and isinstance(value, dict):
                     try:
                          history_data = {}
                          for ts_str, scores in value.items():
                               try: history_data[pd.Timestamp(ts_str)] = scores
                               except ValueError: st.warning(f"Could not parse timestamp '{ts_str}' in maturity history. Skipping.")
                          st.session_state[key] = history_data
                     except Exception as e:
                          st.warning(f"Could not load Maturity History state for key '{key}': {e}. Using default.")
                          st.session_state[key] = {}
                elif key.endswith('_df_json') and isinstance(value, str): # General convention
                     try: st.session_state[key] = pd.read_json(io.StringIO(value), orient='split')
                     except Exception as e: st.warning(f"Could not load DataFrame state for key '{key}': {e}. Skipping.")
                else:
                     st.session_state[key] = value
            return True
        except Exception as e:
            st.sidebar.error(f"Error loading state file: {e}")
            init_session_state(force_defaults=True)
            return False
    else:
        init_session_state(force_defaults=True)
        return False


# --- Session State Initialization ---
def init_session_state(force_defaults=False):
    """Initializes session state with default values."""
    if 'state_initialized' in st.session_state and not force_defaults:
        return

    defaults = {
        # General
        'app_version': APP_VERSION,
        'state_initialized': True,
        'current_tab': "🏠 Landing Page", # Track current tab

        # Landing Page
        'project_metadata': {
            'Project Name': 'Enterprise Data Strategy Initiative',
            'Project Lead': 'TBD',
            'Client Name': 'Internal',
            'Generated Date': get_current_time().strftime('%Y-%m-%d'),
            'Generated Time': get_current_time().strftime('%H:%M:%S %Z') if get_current_time().tzinfo else get_current_time().strftime('%H:%M:%S'),
            'Generated From': APP_LOCATION,
        },
        'selected_sector': mock_sectors[0],
        'uploaded_logo_bytes': None, # Store logo bytes

        # Executive Summary
        'exec_summary_text': "*(Auto-generated summary - requires analysis)*",
        'editable_exec_summary': "", # User editable version
        'show_summary_edit': False, # Control visibility of edit area
        'data_trust_score': 0, # Overall trust score from analysis
        'avg_stakeholder_confidence': "N/A", # Average confidence from interviews

        # Stakeholder Interviews
        'interview_confidence': {}, # {persona: {q_index: score}}
        'interview_notes': {}, # {persona: {q_index: note}}
        'interview_questions': default_interview_questions.copy(), # Editable questions
        'uploaded_interview_files': {}, # {persona: [{'name': filename, 'size': ..., 'type': ...}, ...]}

        # Data Upload & Analysis
        'current_data': None, # Holds the DataFrame (uploaded or mock)
        'current_data_filename': None,
        'data_analysis_done': False,
        'dama_results': {},
        'mock_sql': "-- Analysis not run --",
        'profiling_results': None, # Store profiling output
        'data_analysis_issues': {}, # Store DQ issues summary
        'dq_rules_config': { # Example configurable rules
             'completeness_cols': ['CustomerID', 'TransactionAmount', 'SatisfactionScore'],
             'uniqueness_col': 'CustomerID',
             'timeliness_col': 'PurchaseDate',
             'timeliness_days': 90,
             'validity_col': 'TransactionAmount',
             'validity_condition': '>= 0', # Simple condition example
             'consistency_col': 'SatisfactionScore',
             'consistency_range': (1, 5)
        },

        # Data Governance
        'governance_scores': {
            "Policy & Standards": 50, "Data Stewardship": 40, "Data Quality Framework": 60,
            "Metadata Management": 30, "Security & Privacy": 70, "Compliance Adherence": 65
        },
        # Store RACI as DF, but save/load via JSON key 'raci_df_json'
        'raci_df_json': pd.DataFrame(default_raci_data).set_index('Activity'),
        'selected_compliance': mock_compliance_standards[:2],
        'business_glossary': { # Example glossary
             'Data Maturity': 'The extent to which an organization utilizes its data resources...',
             'Data Governance': 'The exercise of authority and control over data assets...',
             'MDM': 'Master Data Management disciplines...'
        },

        # Maturity Assessment
        'maturity_scores': {dim: 2 for dim in mock_maturity_dimensions}, # Current scores
        'maturity_evidence': {dim: "" for dim in mock_maturity_dimensions}, # Evidence text
        'maturity_criteria': default_maturity_criteria, # Descriptions
        'maturity_persona': mock_personas[0],
        'overall_maturity': 0.0,
        'maturity_assessments_history': {}, # {timestamp: {'scores': {...}, 'evidence': {...}}}
        'compare_assessment_ts1': None, # Timestamp for comparison view 1
        'compare_assessment_ts2': None, # Timestamp for comparison view 2


        # Roadmap Builder
        'roadmap_data': {category: pd.DataFrame(items) for category, items in default_roadmap_items.items()}, # Store DFs
        'full_roadmap_for_export': pd.DataFrame(), # Combined roadmap for export tab

        # Export
        'export_options': {
             'include_branding': False, 'include_glossary': True, 'include_raw_data': False,
             'selected_sections': list(TABS.keys()) # Default to all sections
        },
        'simulated_reports': {}, # Store simulated report content per persona
    }

    # Apply defaults only if the key doesn't exist or if forcing defaults
    for key, value in defaults.items():
        if key not in st.session_state or force_defaults:
            # Deep copy for mutable defaults like dicts/lists to avoid shared references
            if isinstance(value, (dict, list)):
                import copy
                st.session_state[key] = copy.deepcopy(value)
            elif isinstance(value, pd.DataFrame):
                 st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value

    # Ensure nested dictionaries are initialized correctly if needed after potential load/default mix
    if 'interview_questions' not in st.session_state or not isinstance(st.session_state['interview_questions'], dict) or force_defaults:
         st.session_state['interview_questions'] = default_interview_questions.copy()
    if 'maturity_evidence' not in st.session_state or not isinstance(st.session_state['maturity_evidence'], dict) or force_defaults:
         st.session_state['maturity_evidence'] = {dim: "" for dim in mock_maturity_dimensions}
    if 'maturity_assessments_history' not in st.session_state or not isinstance(st.session_state['maturity_assessments_history'], dict) or force_defaults:
        st.session_state['maturity_assessments_history'] = {}
    if 'dq_rules_config' not in st.session_state or not isinstance(st.session_state['dq_rules_config'], dict) or force_defaults:
         st.session_state['dq_rules_config'] = defaults['dq_rules_config'].copy() # Ensure it's initialized

    # Mark state as initialized
    st.session_state.state_initialized = True


# --- Plotting Functions ---

def create_radar_chart(data_dict, title, range_max=100):
    """Creates a Plotly radar chart."""
    if not data_dict or not isinstance(data_dict, dict):
        st.warning(f"Cannot create radar chart '{title}': Invalid data.")
        return go.Figure().update_layout(title=f"{title} (No data)")

    categories = list(data_dict.keys())
    values = [v if isinstance(v, (int, float)) else 0 for v in data_dict.values()]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Score'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, range_max])),
        showlegend=False,
        title=dict(text=title, x=0.5),
        height=400,
        margin=dict(l=40, r=40, t=80, b=40), # Increased top margin for title
        # Example theme consistency:
        # paper_bgcolor='rgba(0,0,0,0)',
        # plot_bgcolor='rgba(0,0,0,0)',
        # font=dict(color=st.get_option("theme.textColor"))
    )
    return fig

def create_maturity_radar(data_dict, title):
    """Creates a Plotly radar chart for maturity assessment (scale 1-5)."""
    if not data_dict or not isinstance(data_dict, dict):
        st.warning(f"Cannot create maturity radar chart '{title}': Invalid data.")
        return go.Figure().update_layout(title=f"{title} (No data)")

    # Ensure categories come from the canonical list for consistent ordering
    categories = mock_maturity_dimensions
    values = []
    for dim in categories: # Iterate through expected dimensions
        val = data_dict.get(dim, 1) # Default to 1 if dimension missing in data_dict
        if isinstance(val, (int, float)) and 1 <= val <= 5:
            values.append(val)
        else:
            values.append(1) # Default to 1 if value invalid

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Maturity Level',
        hovertemplate='<b>%{theta}</b><br>Level: %{r}<extra></extra>' # Custom hover
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5.5], # Extend range slightly for labels
                tickvals=[1, 2, 3, 4, 5],
                ticktext=mock_maturity_levels, # Show level names
                angle=90, # Start axis at top
                tickangle = 0 # Horizontal tick labels
            ),
            angularaxis=dict(direction="clockwise")
        ),
        showlegend=False,
        title=dict(text=title, x=0.5),
        height=450, # Slightly taller
        margin=dict(l=60, r=60, t=80, b=60), # Adjust margins for labels
    )
    return fig

def create_quadrant_chart(x_values, y_values, labels, title, x_axis_label="Trust", y_axis_label="Value", color_values=None, color_label="Category"):
    """Creates a Plotly quadrant chart with optional coloring."""
    if not all(isinstance(lst, list) for lst in [x_values, y_values, labels]):
        st.warning(f"Cannot create quadrant chart '{title}': Input data must be lists.")
        return go.Figure().update_layout(title=f"{title} (Invalid Input)")
    if not (len(x_values) == len(y_values) == len(labels)):
        st.warning(f"Cannot create quadrant chart '{title}': Input lists must have the same length.")
        return go.Figure().update_layout(title=f"{title} (Mismatched Lengths)")
    if color_values and len(color_values) != len(x_values):
         st.warning(f"Cannot create quadrant chart '{title}': Color list length mismatch.")
         color_values = None # Disable coloring if lengths mismatch

    if not x_values:
        return go.Figure().update_layout(title=f"{title} (No data)")

    # Prepare DataFrame
    data = {'x': x_values, 'y': y_values, 'label': labels}
    if color_values:
        data[color_label] = color_values
    df = pd.DataFrame(data)

    # Ensure numeric and drop NaNs for calculations and plotting
    df['x'] = pd.to_numeric(df['x'], errors='coerce')
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df_numeric = df.dropna(subset=['x', 'y']).copy()

    if df_numeric.empty:
        return go.Figure().update_layout(title=f"{title} (No numeric data points)")

    avg_x = df_numeric['x'].mean()
    avg_y = df_numeric['y'].mean()

    # Create scatter plot
    scatter_args = {'data_frame': df_numeric, 'x': 'x', 'y': 'y', 'text': 'label', 'title': title}
    if color_values:
        scatter_args['color'] = color_label
        scatter_args['color_discrete_sequence'] = px.colors.qualitative.Pastel # Example color sequence

    fig = px.scatter(**scatter_args)
    fig.update_traces(textposition='top center', hovertemplate='<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>')

    # Add quadrant lines
    fig.add_vline(x=avg_x, line_dash="dash", line_color="grey", annotation_text="Avg X")
    fig.add_hline(y=avg_y, line_dash="dash", line_color="grey", annotation_text="Avg Y")

    # Add quadrant annotations (adjust positioning based on data range)
    x_range = df_numeric['x'].max() - df_numeric['x'].min() if len(df_numeric['x']) > 1 else 10
    y_range = df_numeric['y'].max() - df_numeric['y'].min() if len(df_numeric['y']) > 1 else 10
    x_pad = x_range * 0.05 + 1 # Add padding
    y_pad = y_range * 0.05 + 1

    x_axis_min = df_numeric['x'].min() - x_pad
    x_axis_max = df_numeric['x'].max() + x_pad
    y_axis_min = df_numeric['y'].min() - y_pad
    y_axis_max = df_numeric['y'].max() + y_pad

    # Quadrant labels (adjust text and position as needed)
    annotations = [
        dict(x=avg_x + x_pad, y=avg_y + y_pad, text="High Value / High Trust", showarrow=False, xanchor='left', yanchor='bottom', bgcolor="rgba(200,255,200,0.7)"),
        dict(x=avg_x - x_pad, y=avg_y + y_pad, text="High Value / Low Trust", showarrow=False, xanchor='right', yanchor='bottom', bgcolor="rgba(255,255,200,0.7)"),
        dict(x=avg_x - x_pad, y=avg_y - y_pad, text="Low Value / Low Trust", showarrow=False, xanchor='right', yanchor='top', bgcolor="rgba(255,200,200,0.7)"),
        dict(x=avg_x + x_pad, y=avg_y - y_pad, text="Low Value / High Trust", showarrow=False, xanchor='left', yanchor='top', bgcolor="rgba(200,200,255,0.7)")
    ]
    for ann in annotations:
         fig.add_annotation(**ann)

    fig.update_layout(
        xaxis_title=x_axis_label,
        yaxis_title=y_axis_label,
        height=500,
        xaxis=dict(range=[x_axis_min, x_axis_max]),
        yaxis=dict(range=[y_axis_min, y_axis_max]),
        margin=dict(l=40, r=40, t=80, b=40),
        legend_title_text=color_label if color_values else None
    )
    return fig

def create_gantt_chart(roadmap_df):
    """Creates an interactive Gantt chart from roadmap data."""
    if roadmap_df is None or roadmap_df.empty:
        st.info("No roadmap data available to generate Gantt chart.")
        return None # Return None if no data

    gantt_data = []
    start_date = get_current_time().normalize() # Base date for calculations

    # Define start offsets and approximate durations for categories
    category_timing = {
        "Quick Wins (0-3 Months)": {"start_offset": pd.DateOffset(days=0), "base_duration_days": 60, "variability_days": 30},
        "Mid-Term (3-12 Months)": {"start_offset": pd.DateOffset(months=3), "base_duration_days": 180, "variability_days": 90},
        "Long-Term (12+ Months)": {"start_offset": pd.DateOffset(years=1), "base_duration_days": 270, "variability_days": 90}
    }
    effort_duration_factor = {"Low": 0.5, "Medium": 1.0, "High": 1.5, "Very High": 2.0}

    # Assign mock dates row by row
    for index, row in roadmap_df.iterrows():
        try:
            category = row.get('Category', mock_roadmap_categories[0])
            timing = category_timing.get(category, category_timing[mock_roadmap_categories[0]])

            cat_start = start_date + timing["start_offset"]
            task_start_offset_days = np.random.randint(0, max(1, int(timing["variability_days"] / 2)))
            task_start = cat_start + pd.Timedelta(days=task_start_offset_days)

            task_effort = row.get('Effort', 'Medium')
            duration_multiplier = effort_duration_factor.get(task_effort, 1.0)
            task_duration_days = timing["base_duration_days"] * duration_multiplier * (0.8 + np.random.rand() * 0.4)
            task_finish = task_start + pd.Timedelta(days=max(1, task_duration_days))

            task_id = row.get('ID', f'Task-{index}')
            task_desc = row.get('Task', 'Unnamed Task')
            task_owner = row.get('Owner', 'TBD')
            task_status = row.get('Status', 'Not Started')
            task_progress = row.get('Progress (%)', 0)
            task_deps = row.get('Dependencies (IDs)', '') # Get dependencies
            # Ensure progress is numeric and within range
            try:
                task_progress = max(0, min(100, int(task_progress)))
            except (ValueError, TypeError):
                task_progress = 0


            display_task = f"{task_id}: {task_desc}"
            display_task = display_task[:60] + "..." if len(display_task) > 60 else display_task

            gantt_data.append(dict(
                Task=display_task,
                Start=task_start,
                Finish=task_finish,
                Owner=task_owner,
                Category=category,
                Status=task_status,
                Progress=task_progress, # Use numeric progress
                Dependencies=task_deps, # Include dependencies
                FullTaskDesc=f"{task_id}: {task_desc} (Status: {task_status}, Progress: {task_progress}%, Depends on: {task_deps or 'None'})" # Add more info
            ))
        except Exception as e:
            st.warning(f"Could not process roadmap item {row.get('ID', index)} for Gantt: {e}")
            continue # Skip problematic rows

    if not gantt_data:
        st.warning("No valid data points generated for Gantt chart.")
        return None

    gantt_df = pd.DataFrame(gantt_data)
    gantt_df['Start'] = pd.to_datetime(gantt_df['Start'])
    gantt_df['Finish'] = pd.to_datetime(gantt_df['Finish'])

    # Filter out invalid dates
    gantt_df_valid = gantt_df.dropna(subset=['Start', 'Finish'])
    gantt_df_valid = gantt_df_valid[gantt_df_valid['Finish'] >= gantt_df_valid['Start']].copy()

    if gantt_df_valid.empty:
        st.warning("No valid roadmap items with start/finish dates found after processing.")
        return None

    try:
        # Sort tasks for better visualization (e.g., by start date, reversed for Plotly y-axis)
        gantt_df_valid = gantt_df_valid.sort_values(by='Start', ascending=False)

        # Map Status to colors (example)
        status_colors = {
            "Not Started": "lightgrey", "Planning": "lightblue", "In Progress": "orange",
            "On Hold": "lightyellow", "Completed": "lightgreen", "Blocked": "lightcoral"
        }

        fig_gantt = px.timeline(
            gantt_df_valid,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Owner", # Color bars by owner
            title="Roadmap Timeline (Simulated Dates)",
            labels={"Owner": "Task Owner"},
            hover_data=["Category", "Status", "Progress", "Dependencies", "FullTaskDesc"], # Show more info on hover
            custom_data=["Progress", "Status", "Dependencies"] # Pass extra data
        )

        # --- Add Progress Simulation within bars ---
        shapes = []
        for i, row in gantt_df_valid.iterrows():
            progress = row['Progress'] / 100.0
            if progress > 0 and progress < 1: # Only draw for partial progress
                 progress_end_date = row['Start'] + (row['Finish'] - row['Start']) * progress
                 shapes.append(dict(
                     type="line", x0=row['Start'], y0=row['Task'], x1=progress_end_date, y1=row['Task'],
                     line=dict(color="rgba(0, 100, 0, 0.7)", width=10), layer="above"
                 ))
        # --- [Placeholder] Dependency Visualization ---
        # Actual dependency lines are complex in Plotly timeline.
        # Could potentially add annotations or try network graph libraries.
        # Example: Add annotation for dependency text
        # for i, row in gantt_df_valid.iterrows():
        #     if row['Dependencies']:
        #         fig_gantt.add_annotation(x=row['Start'], y=row['Task'], text=f"🔗{row['Dependencies']}", showarrow=False, xanchor='right', xshift=-5)
        # --- [End Placeholder] ---

        fig_gantt.update_layout(shapes=shapes)

        fig_gantt.update_layout(
            height=max(400, len(gantt_df_valid) * 35 + 100), # Dynamic height
            xaxis_title="Timeline", yaxis_title="Roadmap Initiatives",
            legend_title_text='Owner / Status',
            xaxis_range=[gantt_df_valid['Start'].min() - pd.Timedelta(days=14), # Add padding
                         gantt_df_valid['Finish'].max() + pd.Timedelta(days=14)]
        )
        # Customize hover template
        fig_gantt.update_traces(hovertemplate='<b>%{y}</b><br>Owner: %{customdata[1]}<br>Start: %{base|%Y-%m-%d}<br>Finish: %{x|%Y-%m-%d}<br>Progress: %{customdata[0]}%<br>Depends on: %{customdata[2]}<extra></extra>')

        return fig_gantt

    except Exception as e:
        st.error(f"Could not generate Gantt chart: {e}")
        st.dataframe(gantt_df_valid) # Show valid data if chart fails
        return None


# --- Data Analysis Functions ---

def run_mock_dama_checks(df, config):
    """Simulates DAMA data quality checks based on config."""
    results = {}
    if df is None or df.empty:
        results['Overall Status'] = "Error: No data provided."
        return results, {} # Return empty issues dict

    num_rows = len(df)
    issues_summary = {} # Store details about failures

    def calculate_percentage(numerator, denominator):
        if denominator == 0: return 100.0
        return round((numerator / denominator) * 100, 1)

    # 1. Completeness
    completeness_cols = config.get('completeness_cols', [])
    present_cols = [col for col in completeness_cols if col in df.columns]
    if present_cols:
        try:
            total_cells = len(present_cols) * num_rows
            nan_cells = df[present_cols].isnull().sum().sum()
            completeness_score = calculate_percentage(total_cells - nan_cells, total_cells)
            results['Completeness'] = completeness_score
            if nan_cells > 0:
                issues_summary['Completeness'] = f"{nan_cells} missing values found in columns: {', '.join(present_cols)}"
        except Exception as e:
            results['Completeness'] = f"Error ({e})"
    else: results['Completeness'] = "N/A (Cols missing)"

    # 2. Uniqueness
    unique_col = config.get('uniqueness_col')
    if unique_col and unique_col in df.columns:
        try:
            non_na_rows = df[unique_col].dropna()
            num_non_na = len(non_na_rows)
            unique_ids = non_na_rows.nunique()
            uniqueness_score = calculate_percentage(unique_ids, num_non_na) if num_non_na > 0 else 100.0
            results['Uniqueness'] = uniqueness_score
            duplicates = num_non_na - unique_ids
            if duplicates > 0:
                 issues_summary['Uniqueness'] = f"{duplicates} duplicate values found in '{unique_col}' (excluding nulls)."
        except Exception as e: results['Uniqueness'] = f"Error ({e})"
    else: results['Uniqueness'] = "N/A (Col missing)"

    # 3. Timeliness
    time_col = config.get('timeliness_col')
    days_limit = config.get('timeliness_days', 90)
    if time_col and time_col in df.columns:
        try:
            dates = pd.to_datetime(df[time_col], errors='coerce')
            valid_dates = dates.dropna()
            if not valid_dates.empty:
                now = get_current_time()
                if valid_dates.dt.tz is None and now.tz is not None: now_compare = now.tz_localize(None)
                elif valid_dates.dt.tz is not None and now.tz is None: now_compare = now.tz_localize(APP_TIMEZONE).tz_convert(valid_dates.dt.tz) if APP_TIMEZONE else now
                elif valid_dates.dt.tz is not None and now.tz is not None: now_compare = now.tz_convert(valid_dates.dt.tz)
                else: now_compare = now

                limit_date = now_compare - pd.Timedelta(days=days_limit)
                timely_records = valid_dates[valid_dates > limit_date].shape[0]
                timeliness_score = calculate_percentage(timely_records, num_rows)
                results['Timeliness'] = timeliness_score
                outdated_records = len(valid_dates) - timely_records
                if outdated_records > 0:
                    issues_summary['Timeliness'] = f"{outdated_records} records older than {days_limit} days in '{time_col}'."
            else: results['Timeliness'] = "N/A (No valid dates)"
        except Exception as e: results['Timeliness'] = f"Error ({e})"
    else: results['Timeliness'] = f"N/A (Col missing or invalid limit: {days_limit})"

    # 4. Validity (Simple example: Amount >= 0)
    validity_col = config.get('validity_col')
    if validity_col and validity_col in df.columns:
        try:
            numeric_vals = pd.to_numeric(df[validity_col], errors='coerce').dropna()
            if config.get('validity_condition') == '>= 0':
                valid_vals = numeric_vals[numeric_vals >= 0].shape[0]
            else: valid_vals = len(numeric_vals)

            validity_score = calculate_percentage(valid_vals, num_rows)
            results['Validity'] = validity_score
            invalid_count = len(numeric_vals) - valid_vals
            if invalid_count > 0:
                 issues_summary['Validity'] = f"{invalid_count} values in '{validity_col}' failed condition '{config.get('validity_condition', 'N/A')}'."
        except Exception as e: results['Validity'] = f"Error ({e})"
    else: results['Validity'] = "N/A (Col missing)"

    # 5. Consistency (Example: Score 1-5 or Null)
    consistency_col = config.get('consistency_col')
    consistency_range = config.get('consistency_range', (1, 5))
    if consistency_col and consistency_col in df.columns and isinstance(consistency_range, tuple) and len(consistency_range) == 2:
        min_val, max_val = consistency_range
        try:
            scores = pd.to_numeric(df[consistency_col], errors='coerce')
            consistent_scores = scores[((scores >= min_val) & (scores <= max_val)) | scores.isna()].shape[0]
            consistency_score = calculate_percentage(consistent_scores, num_rows)
            results['Consistency'] = consistency_score
            inconsistent_count = num_rows - consistent_scores
            if inconsistent_count > 0:
                 issues_summary['Consistency'] = f"{inconsistent_count} values in '{consistency_col}' outside range {min_val}-{max_val} (or non-numeric)."
        except Exception as e: results['Consistency'] = f"Error ({e})"
    else: results['Consistency'] = "N/A (Col/Range missing)"

    return results, issues_summary

def simulate_sql_analysis(df, config):
    """Simulates running SQL-like analysis and generating a trust score."""
    if df is None or df.empty:
        return "-- No data for analysis --", 0, {}, {}

    dama_results, issues_summary = run_mock_dama_checks(df, config)
    valid_scores = [v for v in dama_results.values() if isinstance(v, (int, float))]
    trust_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0

    # Mock SQL query representation
    cols = df.columns
    select_cols = [c for c in ['Region', 'ProductCategory'] if c in cols]
    group_by_cols = ', '.join(select_cols) if select_cols else '1'
    avg_trans = f"AVG({config.get('validity_col', 'Amount')})" if config.get('validity_col') in cols else "'N/A'"
    unique_cust = f"COUNT(DISTINCT {config.get('uniqueness_col', 'ID')})" if config.get('uniqueness_col') in cols else "COUNT(*)"
    low_sat_col = config.get('consistency_col', 'Score')
    low_sat_cond = f"WHEN {low_sat_col} < 3 THEN 1 ELSE 0" if low_sat_col in cols else "'N/A'" # Example condition

    # --- [AI Integration Placeholder] ---
    ai_prompt = f"""
    Analyze the following data quality results and provide a brief insight:
    DAMA Scores: {dama_results}
    Issues Found: {issues_summary}
    Trust Score: {trust_score}%
    Focus on the lowest scoring DAMA dimension and suggest a potential root cause or next step.
    """
    # ai_insight = call_arcadis_gpt(ai_prompt) # Replace mock response
    ai_insight = f"AI Insight Placeholder: Data quality checks reveal potential issues (see DAMA results). Average trust score reflects these checks. Issues found in: {', '.join(issues_summary.keys()) if issues_summary else 'None'}. Recommend investigating '{min(dama_results, key=lambda k: dama_results.get(k, 101)) if valid_scores else 'N/A'}'." # Mock response
    # --- [End AI Integration Placeholder] ---

    mock_sql = f"""
-- Mock Analysis Summary --
SELECT
    {group_by_cols if select_cols else "'Overall' AS Grouping"},
    COUNT(*) AS total_records,
    {avg_trans} AS avg_transaction,
    {unique_cust} AS unique_identifiers,
    SUM(CASE {low_sat_cond} END) AS low_satisfaction_count -- Example aggregation
FROM your_data_table -- Represents the uploaded/simulated data
{"GROUP BY " + group_by_cols if select_cols else ""};

-- MOCK TRUST SCORE: {trust_score}% --
-- Based on DAMA Checks: {', '.join([f'{k}: {v}%' for k, v in dama_results.items() if isinstance(v, (int, float))])}
-- AI Insight: {ai_insight}
    """
    return mock_sql, trust_score, dama_results, issues_summary

def run_basic_profiling(df):
    """Performs basic data profiling."""
    if df is None or df.empty:
        return "No data to profile."

    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    profile = {
        "Basic Info": info_str,
        "Shape": df.shape,
        "Missing Values (%)": (df.isnull().sum() / len(df) * 100).round(1).to_dict(),
        "Unique Values": df.nunique().to_dict(),
        "Numeric Stats": df.describe(include=np.number).to_json(orient="split"), # Use JSON for display
        "Categorical Stats": df.describe(include='object').to_json(orient="split") # Use JSON for display
    }
    return profile

# --- [Advanced Profiling Placeholder] ---
# def generate_profiling_report(df, title="Data Profile Report"):
#     """Generates an advanced profiling report using ydata-profiling."""
#     if df is None or df.empty:
#         st.warning("No data available to generate profiling report.")
#         return None
#     try:
#         profile = ProfileReport(df, title=title, explorative=True)
#         # Save to HTML or display directly in Streamlit using components
#         # profile.to_file("profiling_report.html")
#         # st_profile_report(profile) # Requires streamlit-pandas-profiling component
#         st.info("Advanced Profiling (ydata-profiling) placeholder: Report generation logic goes here.")
#         return profile # Or path to report file
#     except Exception as e:
#         st.error(f"Failed to generate profiling report: {e}")
#         return None
# --- [End Advanced Profiling Placeholder] ---

# --- [Data Cleaning Placeholder] ---
# def perform_data_cleaning(df, action, column=None, value=None):
#     """Performs a specified data cleaning action."""
#     df_cleaned = df.copy()
#     st.info(f"Data Cleaning Action '{action}' placeholder: Logic to modify DataFrame goes here.")
#     # Example actions:
#     # if action == "remove_duplicates":
#     #     df_cleaned = df.drop_duplicates()
#     # elif action == "impute_mean" and column:
#     #     if column in df_cleaned.columns and pd.api.types.is_numeric_dtype(df_cleaned[column]):
#     #         mean_val = df_cleaned[column].mean()
#     #         df_cleaned[column].fillna(mean_val, inplace=True)
#     # ... other actions ...
#     return df_cleaned
# --- [End Data Cleaning Placeholder] ---


# --- [AI Integration Placeholder] ---
# def call_arcadis_gpt(prompt, max_tokens=150):
#     """Sends a prompt to the Arcadis GPT API and returns the response."""
#     api_key = st.secrets.get("arcadis_gpt_key")
#     api_endpoint = st.secrets.get("arcadis_gpt_endpoint")
#     if not api_key or not api_endpoint:
#          st.error("Arcadis GPT API Key or Endpoint not found in Streamlit Secrets.")
#          return "Error: API credentials missing."
#
#     headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" }
#     payload = { "prompt": prompt, "max_tokens": max_tokens }
#     try:
#         response = requests.post(api_endpoint, headers=headers, json=payload, timeout=30)
#         response.raise_for_status()
#         result = response.json()
#         # --- IMPORTANT: Adapt the line below based on Arcadis GPT's actual response structure ---
#         ai_text = result.get("choices", [{}])[0].get("text", "Error: Could not extract text.").strip()
#         return ai_text
#     except requests.exceptions.RequestException as e:
#         st.error(f"AI API request failed: {e}")
#         return f"Error: AI API request failed ({e})"
#     except Exception as e:
#         st.error(f"An error occurred during AI processing: {e}")
#         return f"Error: AI processing failed ({e})"
# --- [End AI Integration Placeholder] ---


# --- Tab Functions ---

def tab_landing_page():
    st.markdown("## 🏠 Welcome to the Data Strategy Playbook")
    st.markdown("Follow the steps outlined below and navigate through the tabs to assess your current state, identify gaps, and build an actionable data strategy roadmap.")
    st.markdown("---")

    # Load/Save State Buttons
    col_state1, col_state2 = st.sidebar.columns(2)
    with col_state1:
        if st.button("💾 Save State", key="save_state_sidebar", help="Save current inputs and scores to state file"):
            if save_app_state_json(): # Use JSON save
                 st.toast("✅ State saved!", icon="💾")
                 time.sleep(1)
            else:
                 st.error("Failed to save state.")
    with col_state2:
        if st.button("🔄 Load State", key="load_state_sidebar", help="Load inputs and scores from state file"):
            if load_app_state_json(): # Use JSON load
                 st.toast("✅ State loaded!", icon="🔄")
                 time.sleep(1)
                 st.rerun()
            else:
                 st.error("Failed to load state or no state file found.")
    st.sidebar.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Your Strategic Intelligence Engine for Data Leadership (v{st.session_state.get('app_version', 'N/A')}).**")
        st.write("") # Add vertical space

        # Sector Selection
        st.session_state.selected_sector = st.selectbox(
            "Select Your Primary Sector:",
            options=mock_sectors,
            index=mock_sectors.index(st.session_state.get('selected_sector', mock_sectors[0])),
            key="landing_sector_select"
        )
        st.caption(f"Sector selection ('{st.session_state.selected_sector}') may influence benchmarks or suggestions (feature placeholder).")

        st.markdown("---")
        st.markdown("#### 📝 Project Metadata")
        with st.container(border=True):
            meta = st.session_state.get('project_metadata', {})
            # Allow editing metadata
            meta['Project Name'] = st.text_input("Project Name", value=meta.get('Project Name', ''))
            meta['Project Lead'] = st.text_input("Project Lead", value=meta.get('Project Lead', ''))
            meta['Client Name'] = st.text_input("Client Name", value=meta.get('Client Name', ''))
            st.write("") # Spacer
            # Display generated info
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.caption(f"Date Generated: {meta.get('Generated Date', 'N/A')}")
                st.caption(f"Time Generated: {meta.get('Generated Time', 'N/A')}")
            with meta_col2:
                st.caption(f"Generated from: {meta.get('Generated From', 'N/A')}")
                st.caption(f"App Version: {st.session_state.get('app_version', 'N/A')}")
            # Update state
            st.session_state.project_metadata = meta


    with col2:
        st.markdown("#### 🖼️ Organization Logo")
        with st.container(border=True):
            uploaded_file = st.file_uploader("Upload your logo (PNG, JPG)", type=["png", "jpg", "jpeg"], key="logo_uploader")

            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                try:
                    img = Image.open(io.BytesIO(bytes_data))
                    st.session_state.uploaded_logo_bytes = bytes_data # Store bytes
                    st.image(img, caption=f"Uploaded: {uploaded_file.name}", width=150)
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    st.session_state.uploaded_logo_bytes = None
            elif st.session_state.get('uploaded_logo_bytes'):
                try:
                    img = Image.open(io.BytesIO(st.session_state.uploaded_logo_bytes))
                    st.image(img, caption="Stored Logo", width=150)
                except Exception as e:
                    st.error(f"Error displaying stored logo: {e}")
                    st.session_state.uploaded_logo_bytes = None # Clear if invalid
            else:
                st.info("Upload a logo to personalize the report.")

            if st.session_state.get('uploaded_logo_bytes'):
                st.write("") # Spacer
                if st.button("Remove Logo", key="remove_logo_btn"):
                    st.session_state.uploaded_logo_bytes = None
                    st.rerun()
        st.write("") # Vertical space

    st.markdown("---")
    st.markdown("#### 🚀 Playbook Steps (Storyline)")
    steps = [
        ("1️⃣ Setup", "Input Project Metadata & Logo.", "🏠 Landing Page"),
        ("2️⃣ Discover", "Capture Stakeholder Insights.", "🎙️ Stakeholder Interviews"),
        ("3️⃣ Assess", "Evaluate Maturity & Governance.", "📈 Maturity Assessment"), # Link to first assessment tab
        ("4️⃣ Analyze", "Check Sample Data Quality.", "🔍 Data Upload & Analysis"),
        ("5️⃣ Plan", "Build Your Strategic Roadmap.", "🗺️ Roadmap Builder"),
        ("6️⃣ Summarize", "Review Executive Summary.", "📄 Executive Summary"),
        ("7️⃣ Export", "Generate Tailored Reports.", "📤 Export")
    ]
    # Display steps more prominently
    cols = st.columns(len(steps))
    tab_keys = list(TABS.keys())
    for i, (step_num, step_desc, target_tab_title) in enumerate(steps):
         with cols[i]:
             with st.container(border=True):
                 st.markdown(f"**{step_num}**")
                 st.caption(f"{step_desc}")
                 # Simple navigation hint - real navigation requires more complex callback/state handling
                 # st.button(f"Go to {target_tab_title}", key=f"nav_{i}") # Buttons might work better than links


def tab_executive_summary():
    st.markdown("## 📄 Executive Summary")
    st.markdown("This section provides a high-level overview based on your inputs across the playbook. Review the generated narrative and key metrics.")
    st.markdown("---")

    # --- Calculate values needed for summary ---
    governance_scores = st.session_state.get('governance_scores', {})
    maturity_scores = st.session_state.get('maturity_scores', {})
    avg_stakeholder_conf_val = st.session_state.get('avg_stakeholder_confidence', "N/A")
    data_trust_val = st.session_state.get('data_trust_score', "N/A")

    valid_gov_scores = [v for v in governance_scores.values() if isinstance(v, (int, float))]
    avg_gov_score = sum(valid_gov_scores) / len(valid_gov_scores) if valid_gov_scores else 0

    valid_maturity_scores = [s for s in maturity_scores.values() if isinstance(s, (int, float))]
    avg_maturity = sum(valid_maturity_scores) / len(valid_maturity_scores) if valid_maturity_scores else 0
    maturity_level_index = round(avg_maturity) - 1
    maturity_level_text = mock_maturity_levels[maturity_level_index] if 0 <= maturity_level_index < len(mock_maturity_levels) else "N/A"

    avg_stakeholder_conf_str = f"{avg_stakeholder_conf_val}/10" if isinstance(avg_stakeholder_conf_val, (int, float)) else "N/A"
    data_trust_str = f"{data_trust_val}%" if isinstance(data_trust_val, (int, float)) else "N/A"

    lowest_gov_area = min(governance_scores, key=lambda k: governance_scores.get(k, 101)) if valid_gov_scores else "N/A"
    lowest_gov_score = governance_scores.get(lowest_gov_area, "N/A")
    lowest_gov_score_str = f"{lowest_gov_score}%" if isinstance(lowest_gov_score, (int, float)) else "N/A"

    lowest_maturity_area = min(maturity_scores, key=lambda k: maturity_scores.get(k, 6)) if valid_maturity_scores else "N/A"
    highest_maturity_area = max(maturity_scores, key=lambda k: maturity_scores.get(k, 0)) if valid_maturity_scores else "N/A"


    # --- Generate Summary Text ---
    # --- [AI Integration Placeholder] ---
    ai_summary_prompt = f"""
    Generate an executive summary for a data strategy playbook based on the following key metrics:
    - Selected Sector: {st.session_state.get('selected_sector', 'N/A')}
    - Overall Maturity Level: {avg_maturity:.1f} ({maturity_level_text})
    - Highest Maturity Dimension: {highest_maturity_area}
    - Lowest Maturity Dimension: {lowest_maturity_area}
    - Average Stakeholder Confidence: {avg_stakeholder_conf_str}
    - Data Trust Score (from sample analysis): {data_trust_str}
    - Average Governance Score: {avg_gov_score:.1f}%
    - Lowest Governance Area: {lowest_gov_area}
    - Key Roadmap Themes (Placeholder): [e.g., MDM Implementation, Cloud Migration, Improve DQ Reporting]

    Structure the summary with clear bullet points covering Maturity, Governance, Trust/Quality, and Priority Areas. Keep it concise and action-oriented.
    """
    # generated_summary = call_arcadis_gpt(ai_summary_prompt, max_tokens=250) # Replace mock text below
    generated_summary = f"""
* **Overall Maturity:** Assessed at **Level {avg_maturity:.1f} ({maturity_level_text})**. Strengths observed in **'{highest_maturity_area}'**, while **'{lowest_maturity_area}'** requires development.
* **Governance:** Average score is **{avg_gov_score:.1f}%**. The area needing most attention is **'{lowest_gov_area}'** (Score: {lowest_gov_score_str}), suggesting a need for clearer policies or stewardship.
* **Data Trust & Quality:** Stakeholder confidence averages **{avg_stakeholder_conf_str}**. Sample data analysis yielded a Trust Score of **{data_trust_str}**. Addressing quality issues identified is crucial.
* **Strategic Alignment:** [Placeholder: Moderate/High/Low] alignment noted. Opportunities exist to better leverage data for strategic goals like [Placeholder Goal].
* **Priority Areas:** Recommend focus on improving **'{lowest_gov_area}'** governance, addressing data quality concerns highlighted during analysis, and advancing maturity in **'{lowest_maturity_area}'**. Key roadmap themes include [Placeholder].
"""
    # --- End AI Integration Placeholder ---

    # Use generated summary as default for editable area if not already edited by user
    if not st.session_state.get('editable_exec_summary'):
        st.session_state.editable_exec_summary = generated_summary

    # --- Layout ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💬 Narrative Summary & KPIs")
        with st.container(border=True):
            # Display using Markdown first
            st.markdown(st.session_state.editable_exec_summary)
            st.write("---") # Separator

            # Display KPIs alongside summary points (Example)
            kpi_sum_col1, kpi_sum_col2, kpi_sum_col3 = st.columns(3)
            with kpi_sum_col1:
                st.metric("Avg. Maturity", f"{avg_maturity:.1f}", f"{maturity_level_text}")
            with kpi_sum_col2:
                st.metric("Avg. Governance", f"{avg_gov_score:.1f}%", f"Low: {lowest_gov_area}")
            with kpi_sum_col3:
                 delta_col = "off"
                 if isinstance(data_trust_val, (int, float)):
                     if data_trust_val < 60: delta_col = "inverse"
                     elif data_trust_val < 85: delta_col = "normal"
                 st.metric("Data Trust", data_trust_str, delta_color=delta_col)

            st.write("---") # Separator

            # Button to toggle edit mode
            if st.button("✏️ Edit Summary Text", key="toggle_summary_edit"):
                 st.session_state.show_summary_edit = not st.session_state.get('show_summary_edit', False)

            # Show text area only if edit mode is active
            if st.session_state.get('show_summary_edit', False):
                edited_summary = st.text_area(
                    "Edit Summary Text:",
                    value=st.session_state.editable_exec_summary,
                    height=250,
                    key="exec_summary_text_area",
                    label_visibility="collapsed"
                )
                if edited_summary != st.session_state.editable_exec_summary:
                    st.session_state.editable_exec_summary = edited_summary
                    st.toast("Summary edits captured in session.", icon="📝")

            st.write("") # Spacer
            # Export Summary Button
            if st.button("⬇️ Download Summary Text", key="download_summary_txt"):
                 st.download_button(
                     label="Click Here to Download Summary",
                     data=st.session_state.editable_exec_summary.encode('utf-8'),
                     file_name=f"Executive_Summary_{get_current_time().strftime('%Y%m%d')}.txt",
                     mime="text/plain",
                     key="exec_summary_download_action"
                 )


    with col2:
        st.markdown("#### 🧭 Overall Capability Radar")
        with st.container(border=True):
            summary_maturity_data = {
                dim: st.session_state.maturity_scores.get(dim, 1) * 20 # Scale 1-5 to 0-100
                for dim in mock_maturity_dimensions
            }
            summary_maturity_data["Data Governance"] = avg_gov_score # Use calculated avg gov score
            fig_radar = create_radar_chart(summary_maturity_data, "Overall Capability Scores (Approx. 0-100 Scale)", range_max=100)
            st.plotly_chart(fig_radar, use_container_width=True)

        st.write("") # Vertical space
        st.markdown("#### 🎯 Data Asset Trust vs. Value (Mock)")
        with st.container(border=True):
            calculated_trust = data_trust_val if isinstance(data_trust_val, (int, float)) else 70
            mock_quadrant_data = {
                'labels': ['Customer DB', 'Sales Transactions', 'Web Analytics', 'Sensor Data', 'Marketing Leads', 'Inventory Logs'],
                'x_values': [85, calculated_trust, 60, 40, 55, 75], # Trust (X-axis)
                'y_values': [90, 85, 70, 60, 50, 65], # Value (Y-axis) - Mock Value
                'category': ['Core', 'Core', 'Web', 'IoT', 'Marketing', 'Operations'] # Example category
            }
            fig_quadrant = create_quadrant_chart(
                mock_quadrant_data['x_values'], mock_quadrant_data['y_values'], mock_quadrant_data['labels'],
                "Key Data Assets: Trust vs. Value (Illustrative)",
                x_axis_label="Data Trust % (Simulated)", y_axis_label="Business Value (Subjective)",
                color_values=mock_quadrant_data['category'], color_label="Asset Type"
            )
            st.plotly_chart(fig_quadrant, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📈 Scorecard Download")
    # Allow customization placeholder
    st.info("Future Enhancement: Allow selecting metrics for the scorecard.")
    # Generate scorecard data
    current_time = get_current_time()
    current_date_str = current_time.strftime('%Y-%m-%d')
    scorecard_data = {
        "Metric": ["Overall Maturity Level", "Avg. Stakeholder Confidence", "Simulated Data Trust Score", "Avg. Governance Maturity Score", "Lowest Governance Area", "Strategic Value Score (Mock)"],
        "Score": [f"{avg_maturity:.1f} ({maturity_level_text})", avg_stakeholder_conf_str, data_trust_str, f"{avg_gov_score:.1f}%", lowest_gov_area, "70%"],
        "Comment": ["Requires standardization.", "Based on interviews.", "Based on sample data analysis.", f"Lowest score: {lowest_gov_score_str}.", "Area needing most attention.", "Opportunities for proactive use."]
    }
    scorecard_df = pd.DataFrame(scorecard_data)
    csv_data = scorecard_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇️ Download Mock Scorecard (CSV)",
        data=csv_data,
        file_name=f"Data_Strategy_Scorecard_{st.session_state.get('selected_sector', 'All')}_{current_date_str.replace('-','')}.csv",
        mime="text/csv",
        key="download_scorecard_csv"
    )


def tab_stakeholder_interviews():
    st.markdown("## 🎙️ Stakeholder Interviews")
    st.markdown("Capture insights by selecting a persona, managing questions, recording notes, and analyzing confidence levels.")
    st.markdown("---")

    col1, col2 = st.columns([1, 2]) # Left column for setup, right for input/display

    with col1:
        st.markdown("#### Configuration")
        with st.container(border=True):
            st.markdown("**Select Persona**")
            selected_persona = st.selectbox("Select Persona for Interview Input:", options=mock_personas, key="interview_persona_select", label_visibility="collapsed")

            st.markdown("**Manage Questions**")
            with st.expander("Edit / Add Interview Questions", expanded=False): # Keep closed by default
                # Ensure the persona exists in the questions dict
                if selected_persona not in st.session_state.interview_questions:
                    st.session_state.interview_questions[selected_persona] = []

                st.markdown("**Edit Existing Questions:**")
                current_questions = st.session_state.interview_questions.get(selected_persona, [])
                new_questions_str = st.text_area(
                    f"Questions for {selected_persona} (one per line):",
                    value="\n".join(current_questions),
                    height=150, # Adjusted height
                    key=f"edit_questions_{selected_persona}"
                )
                new_questions_list = [q.strip() for q in new_questions_str.splitlines() if q.strip()]

                # Update state only if text area content changed
                if new_questions_list != current_questions:
                     st.session_state.interview_questions[selected_persona] = new_questions_list
                     st.success("Questions list updated in text area. Changes applied.")
                     st.rerun()

                st.markdown("**Add New Question:**")
                new_q_text = st.text_input("Enter new question:", key=f"add_question_text_{selected_persona}")
                if st.button("➕ Add Question", key=f"add_question_button_{selected_persona}"):
                     if new_q_text:
                          if selected_persona not in st.session_state.interview_questions:
                               st.session_state.interview_questions[selected_persona] = []
                          st.session_state.interview_questions[selected_persona].append(new_q_text)
                          st.success(f"Question added for {selected_persona}.")
                          st.rerun()
                     else:
                          st.warning("Please enter a question to add.")

            st.markdown("**Upload Documents**")
            # Ensure the persona exists in the files dict
            if selected_persona not in st.session_state.uploaded_interview_files:
                st.session_state.uploaded_interview_files[selected_persona] = []

            uploaded_docs = st.file_uploader(
                f"Upload relevant documents for {selected_persona}",
                accept_multiple_files=True,
                key=f"upload_docs_{selected_persona}",
                label_visibility="collapsed"
            )
            if uploaded_docs:
                current_files_set = {f['name'] for f in st.session_state.uploaded_interview_files[selected_persona]}
                new_files_count = 0
                for f in uploaded_docs:
                     if f.name not in current_files_set:
                         file_details = {'name': f.name, 'size': f.size, 'type': f.type}
                         st.session_state.uploaded_interview_files[selected_persona].append(file_details)
                         current_files_set.add(f.name)
                         new_files_count += 1
                if new_files_count > 0:
                     st.success(f"{new_files_count} new document(s) recorded for {selected_persona}.")
                     st.rerun()

            # Display and manage uploaded files
            if st.session_state.uploaded_interview_files[selected_persona]:
                st.write("**Recorded Documents:**")
                files_to_keep = []
                needs_rerun_files = False
                for i, file_info in enumerate(st.session_state.uploaded_interview_files[selected_persona]):
                     doc_col1, doc_col2 = st.columns([4, 1])
                     doc_col1.caption(f"📄 {file_info['name']} ({file_info['type']}, {file_info['size']} bytes)")
                     if doc_col2.button("❌", key=f"remove_doc_{selected_persona}_{i}", help=f"Remove {file_info['name']}"):
                         st.toast(f"'{file_info['name']}' removed.", icon="🗑️")
                         needs_rerun_files = True # Mark that state needs update
                     else:
                         files_to_keep.append(file_info)

                if needs_rerun_files:
                     st.session_state.uploaded_interview_files[selected_persona] = files_to_keep
                     st.rerun() # Rerun to reflect removal

                if st.button(f"Clear All Documents for {selected_persona}", key=f"clear_files_{selected_persona}"):
                    st.session_state.uploaded_interview_files[selected_persona] = []
                    st.info(f"Document list cleared for {selected_persona}.")
                    st.rerun()


    with col2:
        st.markdown(f"#### 💬 Interview Input for: **{selected_persona}**")

        # Ensure sub-dictionaries exist for the selected persona
        if selected_persona not in st.session_state.interview_confidence: st.session_state.interview_confidence[selected_persona] = {}
        if selected_persona not in st.session_state.interview_notes: st.session_state.interview_notes[selected_persona] = {}

        questions = st.session_state.interview_questions.get(selected_persona, [])

        if not questions:
            st.warning(f"No interview questions defined for {selected_persona}. Add some in the 'Manage Questions' section.")
        else:
            search_notes = st.text_input("Search notes for this persona:", key=f"search_notes_{selected_persona}")
            notes_found_count = 0

            with st.container(height=600): # Make the question area scrollable
                for i, question in enumerate(questions):
                    q_key_base = f"{selected_persona}_{i}"
                    # Get current note, default to empty string if index doesn't exist
                    current_note = st.session_state.interview_notes[selected_persona].get(str(i), "") # Use string index for notes key

                    # Filter visibility based on search term
                    display_question = True
                    if search_notes and search_notes.lower() not in current_note.lower() and search_notes.lower() not in question.lower():
                        display_question = False
                    else:
                         notes_found_count +=1

                    if display_question:
                        with st.container(border=True): # Border around each question block
                            st.markdown(f"**Q{i+1}: {question}**")
                            col_q1, col_q2 = st.columns([1, 3]) # Slider left, notes right

                            with col_q1:
                                # Get current confidence, default to 5 if index doesn't exist
                                current_conf = st.session_state.interview_confidence[selected_persona].get(str(i), 5) # Use string index
                                confidence = st.slider(
                                    f"Confidence / Clarity", 0, 10, int(current_conf),
                                    key=f"conf_{q_key_base}", help="Rate stakeholder confidence/clarity on this topic (0=Low, 10=High)"
                                )
                                st.session_state.interview_confidence[selected_persona][str(i)] = confidence # Save with string index

                            with col_q2:
                                note = st.text_area(
                                    f"Notes for Q{i+1}", value=current_note, key=f"notes_{q_key_base}",
                                    height=75, placeholder="Enter interview notes, key points, action items..."
                                )
                                st.session_state.interview_notes[selected_persona][str(i)] = note # Save with string index
                        st.write("") # Add space between question blocks

                if search_notes and notes_found_count == 0:
                     st.caption("No notes match your search term for this persona.")


    st.markdown("---")
    st.markdown("#### 📊 Interview Summary & Analysis")

    analysis_col1, analysis_col2 = st.columns(2)

    with analysis_col1:
        st.markdown("##### Confidence Overview")
        with st.container(border=True):
            # Calculate overall average confidence
            total_scores, num_scores = 0, 0
            confidence_by_persona = {}
            for persona_key, scores_dict in st.session_state.interview_confidence.items():
                persona_scores = [v for v in scores_dict.values() if isinstance(v, (int, float))]
                if persona_scores:
                    avg_score = round(sum(persona_scores) / len(persona_scores), 1)
                    confidence_by_persona[persona_key] = avg_score
                    total_scores += sum(persona_scores)
                    num_scores += len(persona_scores)

            overall_avg_confidence = round(total_scores / num_scores, 1) if num_scores > 0 else "N/A"
            st.session_state['avg_stakeholder_confidence'] = overall_avg_confidence # Update global state

            st.metric("Overall Average Confidence (All Input)", f"{overall_avg_confidence} / 10")

            if confidence_by_persona:
                with st.expander("Show Average Confidence per Persona", expanded=False):
                    st.bar_chart(pd.DataFrame.from_dict(confidence_by_persona, orient='index', columns=['Average Score']))

        st.write("") # Spacer
        # Placeholder for AI analysis
        st.markdown("##### 💡 AI Analysis (Placeholders)")
        with st.container(border=True):
            st.info("🧠 **Future AI Features:**\n- **Thematic Analysis:** Identify recurring themes in notes.\n- **Sentiment Scoring:** Gauge overall sentiment per persona.\n- **Action Item Extraction:** Automatically list potential action items.")
            # --- [AI Integration Placeholder] ---
            if st.button("Run Mock AI Analysis", key="mock_ai_interview"):
                 # 1. Consolidate notes for analysis
                 all_notes = ""
                 for persona, notes_dict in st.session_state.interview_notes.items():
                      all_notes += f"\n--- Notes from {persona} ---\n"
                      for idx, note in notes_dict.items():
                           all_notes += f"Q{int(idx)+1}: {note}\n" # Assumes idx is string '0', '1' etc.

                 if not all_notes.strip():
                     st.warning("No interview notes entered to analyze.")
                 else:
                     # 2. Create prompt for the AI
                     ai_notes_prompt = f"""
                     Analyze the following stakeholder interview notes. Identify the top 3-5 recurring themes,
                     assess the overall sentiment (Positive, Negative, Neutral, Mixed),
                     and extract potential action items mentioned.

                     Notes:
                     {all_notes}
                     """
                     # 3. Call the AI function (replace mock call)
                     with st.spinner("Simulating AI analysis of notes..."):
                         # ai_analysis_result = call_arcadis_gpt(ai_notes_prompt, max_tokens=300)
                         # Mock Response:
                         ai_analysis_result = """
                         **Themes:** Data Quality Concerns, Tooling Gaps, Training Needs, Integration Challenges, Reporting Delays.
                         **Sentiment:** Mixed (Concerns about quality/tools, but optimism about potential).
                         **Action Items:** Investigate CRM data accuracy, Schedule BI tool training, Define data lineage process, Review data security policies.
                         """
                         st.markdown("**Mock AI Analysis Results:**")
                         st.markdown(ai_analysis_result)
            # --- End AI Integration Placeholder ---

    with analysis_col2:
        st.markdown("##### Confidence Heatmap")
        with st.container(border=True):
            # Generate Heatmap Data more robustly
            heatmap_data = {}
            # Use all personas who have *any* confidence score recorded
            personas_for_heatmap = [p for p in mock_personas if p in st.session_state.interview_confidence and st.session_state.interview_confidence[p]]
            max_questions_per_persona = {p: len(qs) for p, qs in st.session_state.interview_questions.items()}


            if personas_for_heatmap:
                # Determine max questions across included personas for consistent columns
                max_q_count = 0
                if max_questions_per_persona:
                     # Filter max_questions_per_persona to only include those in personas_for_heatmap before calculating max
                     relevant_max_q = {p: count for p, count in max_questions_per_persona.items() if p in personas_for_heatmap}
                     if relevant_max_q:
                          max_q_count = max(relevant_max_q.values())


                if max_q_count > 0:
                    q_labels = [f"Q{i+1}" for i in range(max_q_count)]
                    heatmap_scores = []
                    valid_personas_in_heatmap = [] # Keep track of personas actually added
                    for p in personas_for_heatmap:
                        # Only add persona if they actually have questions defined
                        if max_questions_per_persona.get(p, 0) > 0:
                             scores = st.session_state.interview_confidence.get(p, {})
                             # Pad scores with NaN up to max_q_count
                             # Use string index '0', '1', ... for lookup consistent with saving
                             padded_scores = [scores.get(str(i), np.nan) for i in range(max_q_count)]
                             heatmap_scores.append(padded_scores)
                             valid_personas_in_heatmap.append(p)


                    if heatmap_scores: # Check if any scores were added
                        heatmap_df = pd.DataFrame(heatmap_scores, index=valid_personas_in_heatmap, columns=q_labels)
                        heatmap_df.index.name = "Persona"

                        st.write("Confidence Scores (0-10, '-' = No Data):")
                        st.dataframe(
                            heatmap_df.style
                            .format("{:.0f}", na_rep='-')
                            .background_gradient(cmap='RdYlGn', axis=None, vmin=0, vmax=10, low=0.1, high=0.1) # Subtle gradient
                            .set_properties(**{'width': '50px', 'text-align': 'center'})
                            .set_caption("Hover over cells for scores.")
                        )
                    else:
                        st.info("No questions defined for the personas with recorded confidence scores.")
                else:
                    st.info("No questions found for the personas with recorded confidence scores.")
            else:
                st.info("Enter interview confidence scores via the input section to generate the heatmap.")

    st.markdown("---")
    st.markdown("#### Export Interview Data")
    with st.container(border=True):
        exp_col1, exp_col2 = st.columns(2)
        # Combine all notes and scores for export
        all_interview_data = []
        for persona, notes_dict in st.session_state.interview_notes.items():
             questions = st.session_state.interview_questions.get(persona, [])
             scores_dict = st.session_state.interview_confidence.get(persona, {})
             for i_str, note in notes_dict.items(): # Iterate using string index '0', '1', ...
                 try:
                      i = int(i_str) # Convert string index back to integer
                      if i < len(questions): # Ensure question index is valid
                          all_interview_data.append({
                              "Persona": persona,
                              "Question_Index": i + 1,
                              "Question": questions[i],
                              "Confidence": scores_dict.get(i_str, np.nan), # Use string index for lookup
                              "Notes": note
                          })
                 except ValueError:
                      continue # Skip if index is not a valid integer string

        if all_interview_data:
             export_df = pd.DataFrame(all_interview_data)
             csv_export = export_df.to_csv(index=False).encode('utf-8')
             json_export = export_df.to_json(orient='records', indent=4).encode('utf-8')

             with exp_col1:
                 st.download_button(
                     label="⬇️ Export All Notes & Scores (CSV)",
                     data=csv_export,
                     file_name=f"Interview_Data_{get_current_time().strftime('%Y%m%d')}.csv",
                     mime="text/csv",
                     key="export_interviews_csv",
                     use_container_width=True
                 )
             with exp_col2:
                  st.download_button(
                     label="⬇️ Export All Notes & Scores (JSON)",
                     data=json_export,
                     file_name=f"Interview_Data_{get_current_time().strftime('%Y%m%d')}.json",
                     mime="application/json",
                     key="export_interviews_json",
                     use_container_width=True
                 )
        else:
             st.info("No interview notes or scores entered yet to export.")


def tab_data_upload_analysis():
    st.markdown("## 🔍 Data Upload & Analysis")
    st.markdown("Upload sample datasets, configure checks, run analysis, and review quality/profiling results.")
    st.markdown("---")

    col1, col2 = st.columns([1, 2]) # Input on left, preview/results on right

    with col1:
        st.markdown("#### 1. Load Data")
        with st.container(border=True):
            data_source = st.radio(
                "Choose data source:",
                ("Upload CSV/Excel", "Use Mock Dataset", "Connect to Database (Placeholder)"),
                key="data_source_radio",
                index=1 if st.session_state.get('current_data') is None else 0,
                horizontal=True
            )

            df = None # Initialize df variable
            uploaded_file = None
            selected_sheet = None

            if data_source == "Upload CSV/Excel":
                uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"], key="data_uploader")
                if uploaded_file:
                    # Check if it's a different file before reloading
                    if uploaded_file.name != st.session_state.get('current_data_filename'):
                        st.session_state.current_data_filename = uploaded_file.name
                        try:
                            if uploaded_file.name.endswith('.csv'):
                                df = pd.read_csv(uploaded_file)
                            elif uploaded_file.name.endswith('.xlsx'):
                                excel_file = pd.ExcelFile(uploaded_file)
                                sheet_names = excel_file.sheet_names
                                selected_sheet = st.selectbox("Select Excel Sheet:", sheet_names, key="excel_sheet_select")
                                if selected_sheet:
                                    df = pd.read_excel(excel_file, sheet_name=selected_sheet, engine='openpyxl')
                            else:
                                st.error("Unsupported file type.")
                        except Exception as e:
                            st.error(f"Error reading file: {e}")
                            df = None
                    else:
                         # Same file uploaded, maybe just sheet changed? Check sheet selection again
                         if uploaded_file.name.endswith('.xlsx'):
                             excel_file = pd.ExcelFile(uploaded_file)
                             sheet_names = excel_file.sheet_names
                             current_selection = st.session_state.get("excel_sheet_select")
                             selected_sheet = st.selectbox("Select Excel Sheet:", sheet_names, index=sheet_names.index(current_selection) if current_selection in sheet_names else 0, key="excel_sheet_select")
                             if selected_sheet != current_selection:
                                 try:
                                     df = pd.read_excel(excel_file, sheet_name=selected_sheet, engine='openpyxl')
                                 except Exception as e:
                                     st.error(f"Error reading sheet '{selected_sheet}': {e}")
                                     df = None


            elif data_source == "Use Mock Dataset":
                if st.button("Load Mock Sales Data", key="load_mock_data_button", use_container_width=True):
                    np.random.seed(42)
                    mock_data_dict = { # Regenerate mock data
                        'CustomerID': [f'CUST-{i:04d}' for i in range(1, 101)],
                        'PurchaseDate': pd.to_datetime(np.random.choice(pd.date_range('2024-01-15', '2025-04-14'), 100)),
                        'ProductCategory': np.random.choice(['Electronics', 'Clothing', 'Home Goods', 'Groceries', 'Books'], 100),
                        'TransactionAmount': np.random.uniform(10, 500, 100).round(2),
                        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                        'SatisfactionScore': np.random.randint(1, 6, 100).astype(float),
                    }
                    mock_df = pd.DataFrame(mock_data_dict)
                    mock_df.loc[np.random.choice(mock_df.index, 5, replace=False), 'TransactionAmount'] = -np.random.uniform(5, 50, 5).round(2)
                    mock_df.loc[np.random.choice(mock_df.index, 10, replace=False), 'SatisfactionScore'] = np.nan
                    indices_to_duplicate = np.random.choice(mock_df.index, 3, replace=False)
                    mock_df.loc[indices_to_duplicate[1:], 'CustomerID'] = mock_df.loc[indices_to_duplicate[0], 'CustomerID']
                    df = mock_df.copy()
                    st.session_state.current_data_filename = "Mock Sales Data"
                    st.success("Mock data loaded.")

            elif data_source == "Connect to Database (Placeholder)":
                st.info("Database connection feature placeholder.")
                # --- [Database Placeholder] ---
                # with st.expander("Database Connection Details"):
                #     db_type = st.selectbox("DB Type", ["PostgreSQL", "MySQL", "SQLite"])
                #     db_host = st.text_input("Host")
                #     db_port = st.number_input("Port", value=5432)
                #     db_name = st.text_input("Database Name")
                #     db_user = st.text_input("User")
                #     db_pass = st.text_input("Password", type="password")
                #     db_query = st.text_area("SQL Query", height=150)
                #     if st.button("Connect & Load"):
                #         st.warning("DB Connection not implemented.")
                #         # conn_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}" # Example
                #         # engine = connect_db(conn_string)
                #         # if engine: df = pd.read_sql(db_query, engine)
                # --- [End Database Placeholder] ---
                pass

            # Update session state only if a *new* DataFrame was successfully loaded
            if df is not None:
                st.session_state.current_data = df
                st.session_state.data_analysis_done = False # Reset analysis flags
                st.session_state.dama_results = {}
                st.session_state.mock_sql = "-- Analysis not run --"
                st.session_state.data_trust_score = 0
                st.session_state.profiling_results = None
                st.session_state.data_analysis_issues = {}
                st.success(f"Data '{st.session_state.current_data_filename}' loaded successfully!")
                st.rerun() # Rerun to update options in config section immediately

        st.write("") # Spacer
        st.markdown("#### 2. Configure Analysis")
        with st.expander("Configure DQ Rules & Profiling", expanded=False): # Keep closed by default
             st.caption("Define columns and parameters for DAMA checks:")
             dq_config = st.session_state.get('dq_rules_config', {})
             current_columns = list(st.session_state.current_data.columns) if st.session_state.current_data is not None else []

             # --- FIX for Completeness Columns ---
             saved_completeness_cols = dq_config.get('completeness_cols', [])
             filtered_completeness_default = [col for col in saved_completeness_cols if col in current_columns]
             dq_config['completeness_cols'] = st.multiselect(
                 "Completeness Check Columns:", options=current_columns,
                 default=filtered_completeness_default, key="dq_completeness_cols"
             )
             # --- End FIX ---

             # --- FIX for Uniqueness Column ---
             saved_uniqueness_col = dq_config.get('uniqueness_col')
             uniqueness_options = [None] + current_columns
             uniqueness_index = 0
             if saved_uniqueness_col in current_columns:
                  uniqueness_index = uniqueness_options.index(saved_uniqueness_col)
             dq_config['uniqueness_col'] = st.selectbox(
                 "Uniqueness Check Column:", options=uniqueness_options,
                 index=uniqueness_index, key="dq_uniqueness_col"
             )
             # --- End FIX ---

             # Add more config options... (Timeliness, Validity, Consistency)

             st.session_state.dq_rules_config = dq_config
             st.caption("Profiling Options:")
             # Add profiling options if needed

        st.write("") # Spacer
        st.markdown("#### 3. Run Analysis")
        run_analysis_disabled = st.session_state.get('current_data') is None
        if st.button("📊 Run Analysis", key="run_analysis_button", disabled=run_analysis_disabled, type="primary", use_container_width=True):
            if st.session_state.current_data is not None:
                with st.spinner("Profiling data and running DAMA checks..."):
                    time.sleep(1.0) # Simulate work
                    try:
                        st.session_state.profiling_results = run_basic_profiling(st.session_state.current_data)
                        config = st.session_state.get('dq_rules_config', {})
                        mock_sql_result, trust_score_result, dama_results_dict, issues_summary = simulate_sql_analysis(st.session_state.current_data, config)
                        st.session_state.dama_results = dama_results_dict
                        st.session_state.mock_sql = mock_sql_result
                        st.session_state.data_trust_score = trust_score_result
                        st.session_state.data_analysis_issues = issues_summary
                        st.session_state.data_analysis_done = True
                        st.success("Analysis complete!")
                    except Exception as e:
                         st.error(f"Analysis failed: {e}")
                         st.session_state.data_analysis_done = False
            else:
                st.warning("No data loaded to analyze.")


    with col2:
        st.markdown("#### Data Preview & Results")
        if st.session_state.get('current_data') is not None:
            df_display = st.session_state.current_data
            sheet_info = f"(Sheet: {st.session_state.get('excel_sheet_select', 'N/A')})" if st.session_state.get('current_data_filename', '').endswith('.xlsx') else ''
            st.markdown(f"**Previewing:** `{st.session_state.get('current_data_filename', 'Loaded Data')}` {sheet_info}")
            with st.container(border=True):
                st.dataframe(df_display.head(), use_container_width=True)
                st.caption(f"Shape: {df_display.shape[0]} rows, {df_display.shape[1]} columns")

            if st.session_state.get('data_analysis_done'):
                st.write("") # Spacer
                results_tabs = st.tabs(["📊 DAMA Quality Checks", "📝 Profiling Summary", "💡 Simulated SQL & Insights", "⚠️ Quality Issues", "🧹 Cleaning Actions"])

                with results_tabs[0]: # DAMA Checks
                    st.markdown("##### DAMA Quality Checks")
                    dama_results = st.session_state.get('dama_results', {})
                    if dama_results:
                        num_checks = len(dama_results)
                        cols_per_row = 3 # Adjust as needed
                        num_rows = (num_checks + cols_per_row - 1) // cols_per_row

                        check_items = list(dama_results.items())
                        idx = 0
                        for r in range(num_rows):
                             cols = st.columns(cols_per_row)
                             for c in range(cols_per_row):
                                  if idx < num_checks:
                                       check, score = check_items[idx]
                                       with cols[c]:
                                            if isinstance(score, (int, float)):
                                                 delta_color = "off"
                                                 if score < 60: delta_color = "inverse"
                                                 elif score < 85: delta_color = "normal"
                                                 st.metric(label=check, value=f"{score}%", delta_color=delta_color)
                                                 st.progress(int(score))
                                            else:
                                                 st.metric(label=check, value=str(score))
                                       idx += 1
                    else:
                        st.warning("No DAMA results available.")

                with results_tabs[1]: # Profiling
                    st.markdown("##### Basic Data Profiling")
                    profile_res = st.session_state.get('profiling_results')
                    if isinstance(profile_res, dict):
                         st.text(f"Shape: {profile_res.get('Shape')}")
                         with st.expander("Column Info & Types", expanded=False):
                             st.text(profile_res.get("Basic Info", "N/A"))
                         with st.expander("Missing Values (%)", expanded=False):
                             st.dataframe(pd.DataFrame.from_dict(profile_res.get("Missing Values (%)", {}), orient='index', columns=['Missing %']).sort_values(by='Missing %', ascending=False))
                         with st.expander("Unique Value Counts", expanded=False):
                             st.dataframe(pd.DataFrame.from_dict(profile_res.get("Unique Values", {}), orient='index', columns=['Unique Count']))
                         with st.expander("Numeric Statistics", expanded=False):
                              try:
                                   num_stats_json = profile_res.get("Numeric Stats", "{}")
                                   if num_stats_json and num_stats_json != '{}':
                                        st.dataframe(pd.read_json(io.StringIO(num_stats_json), orient="split"))
                                   else: st.write("No numeric data found.")
                              except Exception as e: st.warning(f"Could not display numeric stats: {e}")
                         with st.expander("Categorical Statistics", expanded=False):
                             try:
                                  cat_stats_json = profile_res.get("Categorical Stats", "{}")
                                  if cat_stats_json and cat_stats_json != '{}':
                                       st.dataframe(pd.read_json(io.StringIO(cat_stats_json), orient="split"))
                                  else: st.write("No categorical data found.")
                             except Exception as e: st.warning(f"Could not display categorical stats: {e}")
                         # Add visualizations
                         with st.expander("Visual Profiling (Sample)", expanded=False):
                              num_cols_prof = df_display.select_dtypes(include=np.number).columns
                              cat_cols_prof = df_display.select_dtypes(include='object').columns
                              if len(num_cols_prof) > 0:
                                   col_to_plot_num = st.selectbox("Select numeric column for histogram:", num_cols_prof, key="prof_hist_select")
                                   if col_to_plot_num:
                                        try:
                                             fig_hist = px.histogram(df_display, x=col_to_plot_num, title=f"Distribution of {col_to_plot_num}")
                                             st.plotly_chart(fig_hist, use_container_width=True)
                                        except Exception as e:
                                             st.warning(f"Could not plot histogram for {col_to_plot_num}: {e}")
                              else:
                                   st.caption("No numeric columns found for histogram.")

                              if len(cat_cols_prof) > 0:
                                   col_to_plot_cat = st.selectbox("Select categorical column for bar chart:", cat_cols_prof, key="prof_bar_select")
                                   if col_to_plot_cat:
                                        try:
                                             top_n = 15
                                             counts = df_display[col_to_plot_cat].value_counts().nlargest(top_n)
                                             fig_bar = px.bar(counts, x=counts.index, y=counts.values, title=f"Top {top_n} Frequencies for {col_to_plot_cat}", labels={'x': col_to_plot_cat, 'y': 'Count'})
                                             st.plotly_chart(fig_bar, use_container_width=True)
                                        except Exception as e:
                                             st.warning(f"Could not plot bar chart for {col_to_plot_cat}: {e}")
                              else:
                                   st.caption("No categorical columns found for bar chart.")
                         # --- [Advanced Profiling Placeholder] ---
                         # if st.button("Generate Advanced Profile Report", key="adv_profile_btn"):
                         #      generate_profiling_report(df_display)
                         # --- [End Advanced Profiling Placeholder] ---
                    else:
                         st.info("Profiling results not available. Run analysis.")

                with results_tabs[2]: # SQL & Trust
                    st.markdown("##### Simulated SQL & Trust Score")
                    mock_sql = st.session_state.get('mock_sql', "-- Analysis not run --")
                    trust_score = st.session_state.get('data_trust_score', 0)

                    st.code(mock_sql, language='sql')
                    if isinstance(trust_score, (int, float)):
                        st.progress(int(trust_score), text=f"Overall Trust Score: {trust_score}%")
                        st.caption("Trust score calculated as the average of numeric DAMA check results.")
                    else:
                        st.warning("Trust score not calculated or is invalid.")

                with results_tabs[3]: # Issues Summary
                    st.markdown("##### Data Quality Issues Summary")
                    issues = st.session_state.get('data_analysis_issues', {})
                    if issues:
                         for check, desc in issues.items():
                              st.warning(f"**{check}:** {desc}")
                    else:
                         st.success("✅ No major quality issues detected by configured checks.")

                with results_tabs[4]: # Cleaning Actions
                     st.markdown("##### Data Cleaning Actions (Placeholders)")
                     issues = st.session_state.get('data_analysis_issues', {})
                     if not issues:
                          st.info("No issues found, no cleaning actions needed based on current checks.")
                     else:
                          st.info("💡 **Select actions to apply to the dataset (Not Implemented):**")
                          # --- [Data Cleaning Placeholder] ---
                          action_applied = False
                          if 'Uniqueness' in issues:
                               if st.button("Action: Remove Duplicates", key="clean_dupes"):
                                    # st.session_state.current_data = perform_data_cleaning(st.session_state.current_data, "remove_duplicates")
                                    st.warning("Remove Duplicates action not implemented.")
                                    action_applied = True
                          if 'Completeness' in issues:
                               impute_method = st.selectbox("Action: Impute Missing Values With:", ["None", "Mean", "Median", "Mode"], key="clean_impute")
                               if impute_method != "None":
                                    # Find columns with issues from issues_summary['Completeness']
                                    # st.session_state.current_data = perform_data_cleaning(st.session_state.current_data, f"impute_{impute_method.lower()}", column=affected_column)
                                    st.warning(f"Impute with {impute_method} action not implemented.")
                                    action_applied = True # Set flag even if not implemented
                          if 'Validity' in issues:
                               if st.button("Action: Flag/Correct Invalid Values", key="clean_validity"):
                                    # st.session_state.current_data = perform_data_cleaning(st.session_state.current_data, "correct_validity")
                                    st.warning("Correct Validity action not implemented.")
                                    action_applied = True

                          if action_applied:
                               st.info("If actions were implemented, re-run analysis to see updated results.")
                               # Consider adding a button to explicitly apply selected actions
                          # --- [End Data Cleaning Placeholder] ---

            elif run_analysis_disabled:
                st.info("Load data first using the options on the left to enable analysis.")
            else:
                st.info("Click '📊 Run Analysis' on the left to see results.")

        else:
            st.info("Upload a file, load mock data, or connect to a database to begin.")


def tab_data_governance():
    st.markdown("## 🏛️ Data Governance Assessment")
    st.markdown("Evaluate governance maturity, define roles (RACI), track compliance, and manage glossary terms.")
    st.markdown("---")

    gov_tabs = st.tabs(["📊 Maturity Scoring", "👥 RACI Matrix", "📜 Compliance & Glossary", "💡 AI Suggestions"])

    with gov_tabs[0]: # Maturity Scoring
        st.markdown("#### Governance Maturity Scoring")
        st.markdown("Rate your current maturity (0=Low, 100=High) in these key governance areas:")
        st.write("") # Spacer

        gov_scores = st.session_state.get('governance_scores', {})
        score_data = {} # For bar chart

        score_cols = st.columns(2)
        i = 0
        # Ensure all expected dimensions are present in the scores dict
        expected_gov_dims = ["Policy & Standards", "Data Stewardship", "Data Quality Framework", "Metadata Management", "Security & Privacy", "Compliance Adherence"]
        for area in expected_gov_dims:
             if area not in gov_scores:
                  gov_scores[area] = 50 # Default if missing

        for area, score in gov_scores.items():
            # Only display sliders for expected dimensions
            if area in expected_gov_dims:
                with score_cols[i % 2]:
                    with st.container(border=True): # Group each slider
                        current_score = int(score) if isinstance(score, (int, float)) else 50
                        current_score = max(0, min(100, current_score))
                        simple_key_part = area.lower().replace('&', 'and').replace(' ', '_').replace('/', '_')
                        slider_key = f"gov_score_{simple_key_part}"

                        new_score = st.slider(
                            area, 0, 100, current_score, key=slider_key,
                            help=f"Assess maturity for '{area}' (0=Low, 100=High)"
                        )
                        st.session_state.governance_scores[area] = new_score
                        score_data[area] = new_score
                i += 1

        # Recalculate average score
        valid_scores = [s for s in st.session_state.governance_scores.values() if isinstance(s, (int, float))]
        avg_gov_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        st.session_state.avg_gov_score = avg_gov_score # Store for summary

        st.markdown("---")
        st.metric("Average Governance Score", f"{avg_gov_score:.1f}%")
        st.progress(int(avg_gov_score))

        # Bar chart visualization
        st.markdown("##### Scores Overview")
        score_df = pd.DataFrame.from_dict(score_data, orient='index', columns=['Score'])
        st.bar_chart(score_df)


    with gov_tabs[1]: # RACI Matrix
        st.markdown("#### Roles & Responsibilities (RACI)")
        st.markdown(f"**Legend:** {default_raci_legend}")
        st.write("") # Spacer

        # Load RACI DataFrame from state (previously stored under 'raci_df_json')
        raci_df = st.session_state.get('raci_df_json') # This should be a DataFrame now due to load_app_state logic

        if raci_df is None or not isinstance(raci_df, pd.DataFrame):
             st.warning("RACI data not found or invalid in state. Initializing with defaults.")
             raci_df = pd.DataFrame(default_raci_data).set_index('Activity')
             st.session_state.raci_df_json = raci_df # Store the DataFrame back

        try:
            # Use data editor for RACI
            edited_raci_df = st.data_editor(
                raci_df.reset_index(), # Edit with Activity as column
                key="raci_editor",
                num_rows="dynamic",
                column_config={
                     "Activity": st.column_config.TextColumn("Activity/Task", required=True, width="large"),
                     # Dynamically configure columns based on the DataFrame's columns
                     **{role: st.column_config.SelectboxColumn(
                         role, options=["R", "A", "C", "I", "S", ""], default="", help=default_raci_legend
                         ) for role in raci_df.columns}
                },
                use_container_width=True,
                hide_index=True
            )
            # Validate and save back to state
            if 'Activity' in edited_raci_df.columns and not edited_raci_df['Activity'].isnull().any() and not edited_raci_df['Activity'].duplicated().any():
                 edited_raci_df.set_index('Activity', inplace=True)
                 # Check if the edited DF is different before updating state to prevent unnecessary reruns
                 if not raci_df.equals(edited_raci_df):
                      st.session_state.raci_df_json = edited_raci_df
                      st.toast("RACI Matrix updated.", icon="👥")
            else:
                 st.warning("RACI Matrix editing failed - 'Activity' column must be present, unique, and non-empty.")

        except Exception as e:
            st.error(f"Error displaying RACI editor: {e}")
            st.dataframe(raci_df) # Show non-editable on error


    with gov_tabs[2]: # Compliance & Glossary
        st.markdown("#### Compliance & Standards")
        with st.container(border=True):
            selected_compliance = st.multiselect(
                "Select applicable compliance standards:",
                options=mock_compliance_standards,
                default=st.session_state.get('selected_compliance', mock_compliance_standards[:2]),
                key="compliance_multiselect"
            )
            st.session_state.selected_compliance = selected_compliance
            st.caption("Selected Standards: " + (", ".join(selected_compliance) if selected_compliance else "None"))

        st.write("") # Spacer
        st.markdown("#### 📖 Business Glossary / Data Dictionary")
        with st.container(border=True):
            glossary = st.session_state.get('business_glossary', {})

            # Display existing terms with Edit/Delete options
            st.markdown("##### Existing Terms")
            terms_to_delete = []
            edited_terms = {}

            if not glossary:
                st.info("Glossary is empty. Add terms below.")
            else:
                for term, definition in sorted(glossary.items()):
                     with st.expander(term, expanded=False): # Keep closed by default
                          edited_def = st.text_area(f"Definition for {term}", value=definition, key=f"edit_def_{term}")
                          if edited_def != definition:
                               edited_terms[term] = edited_def # Store edited definition

                          if st.button(f"❌ Delete '{term}'", key=f"delete_term_{term}"):
                               terms_to_delete.append(term)

            # Apply edits and deletions outside the loop
            needs_rerun = False
            if edited_terms:
                for term, new_def in edited_terms.items():
                     glossary[term] = new_def
                st.session_state.business_glossary = glossary
                st.success(f"{len(edited_terms)} term(s) updated.")
                needs_rerun = True

            if terms_to_delete:
                for term in terms_to_delete:
                     del glossary[term]
                st.session_state.business_glossary = glossary
                st.success(f"{len(terms_to_delete)} term(s) deleted.")
                needs_rerun = True


            # Add new term section
            st.markdown("##### Add New Term")
            with st.form(key="add_term_form"):
                 new_term = st.text_input("New Term")
                 new_definition = st.text_area("Definition")
                 submitted = st.form_submit_button("➕ Add Term")
                 if submitted:
                     if new_term and new_definition and new_term not in glossary:
                         glossary[new_term] = new_definition
                         st.session_state.business_glossary = glossary
                         st.success(f"Term '{new_term}' added.")
                         needs_rerun = True
                     elif new_term in glossary:
                         st.warning(f"Term '{new_term}' already exists.")
                     else:
                         st.warning("Please provide both a term and a definition.")

            if needs_rerun:
                st.rerun()


    with gov_tabs[3]: # AI Suggestions
        st.markdown("#### 💡 AI-Powered Suggestions (Placeholder)")
        st.info("🧠 **Future AI Features:** Leverage AI to provide tailored recommendations.")
        st.write("")

        lowest_gov_area = "N/A"
        valid_scores = [s for s in st.session_state.get('governance_scores', {}).values() if isinstance(s, (int, float))]
        if valid_scores:
            lowest_gov_area = min(st.session_state.governance_scores, key=lambda k: st.session_state.governance_scores.get(k, 101))

        selected_sector = st.session_state.get('selected_sector', 'the selected')
        compliance_str = ', '.join(st.session_state.get('selected_compliance', [])) if st.session_state.get('selected_compliance') else 'selected'

        with st.container(border=True):
            st.markdown("**Potential AI Use Cases:**")
            suggestion_text = f"""
* **Control Recommendations:** Suggest specific governance controls relevant to the **{selected_sector}** sector and **{compliance_str} Compliance Standards**. _(Example: Based on GDPR selection, recommend implementing data minimization checks.)_
* **Role Gaps:** Recommend roles or responsibilities based on identified gaps (e.g., low score in '{lowest_gov_area}' might suggest needing a dedicated Data Quality Lead).
* **Policy Generation:** Generate draft policy statements or procedures for areas scoring below a certain threshold (e.g., < 50%). _(Example: Draft a basic Data Access Request procedure if Security score is low.)_
* **Glossary Enrichment:** Suggest definitions for common data terms or identify terms used in notes/roadmaps that are missing from the glossary.
            """
            st.markdown(suggestion_text)
            st.write("")

            # --- [AI Integration Placeholder] ---
            if st.button("Generate Mock AI Suggestions", key="mock_ai_gov"):
                 # 1. Prepare prompt context
                 context = f"""
                 Governance Assessment Scores: {st.session_state.get('governance_scores', {})}
                 Lowest Scoring Area: {lowest_gov_area}
                 Selected Sector: {selected_sector}
                 Applicable Compliance: {compliance_str}
                 RACI Matrix Summary: [Placeholder - Could include roles with many 'R's or 'A's]
                 Glossary Terms: {list(st.session_state.get('business_glossary', {}).keys())}
                 """
                 ai_gov_prompt = f"Based on the following Data Governance context, provide 2-3 actionable suggestions for improvement:\n{context}"

                 # 2. Call AI function
                 with st.spinner("Simulating AI analysis for governance suggestions..."):
                     # ai_gov_suggestions = call_arcadis_gpt(ai_gov_prompt, max_tokens=200)
                     # Mock Response:
                     ai_gov_suggestions = f"""
                     **Mock Suggestions:**
                     1.  **Focus on '{lowest_gov_area}':** Given the low score, consider establishing a dedicated working group to define clear metrics, processes, and responsibilities for this area. Review RACI assignments related to this.
                     2.  **Compliance Alignment ({compliance_str}):** Ensure data handling procedures, especially concerning [Placeholder: e.g., data subject rights or data transfers], explicitly address the requirements of selected standards. Update relevant policies.
                     3.  **Glossary Expansion:** Terms like '[Placeholder Term 1]' and '[Placeholder Term 2]' seem relevant but are missing from the glossary. Consider adding definitions.
                     """
                     st.markdown("**Mock AI Suggestions:**")
                     st.markdown(ai_gov_suggestions)
            # --- [End AI Integration Placeholder] ---


def tab_maturity_assessment():
    st.markdown("## 📈 Maturity Assessment")
    st.markdown("Assess data capabilities across key dimensions (Level 1-5), provide evidence, and track progress over time.")
    st.markdown("---")

    # --- Load/Save Specific Assessment ---
    history = st.session_state.get('maturity_assessments_history', {})
    assessment_timestamps = sorted(list(history.keys()), reverse=True)
    display_timestamps = ["Current Assessment"] + [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in assessment_timestamps]

    st.markdown("#### Assessment History Management")
    with st.container(border=True):
        col_hist1, col_hist2, col_hist3 = st.columns([3,1,1])
        with col_hist1:
             selected_ts_str = st.selectbox("Load Assessment / View History:", display_timestamps, key="maturity_history_select", label_visibility="collapsed")
        with col_hist2:
             if st.button("💾 Save Current", key="save_maturity_assessment", help="Save the current scores and evidence as a snapshot", use_container_width=True):
                  current_ts = get_current_time()
                  scores_to_save = st.session_state.maturity_scores.copy()
                  evidence_to_save = st.session_state.maturity_evidence.copy()
                  if 'maturity_assessments_history' not in st.session_state: st.session_state.maturity_assessments_history = {}
                  st.session_state.maturity_assessments_history[current_ts] = {'scores': scores_to_save, 'evidence': evidence_to_save}
                  st.success(f"Assessment saved for {current_ts.strftime('%Y-%m-%d %H:%M:%S')}")
                  time.sleep(1)
                  st.rerun()
        with col_hist3:
            if selected_ts_str != "Current Assessment":
                if st.button("🗑️ Delete Sel.", key="delete_maturity_hist", help=f"Delete assessment from {selected_ts_str}", use_container_width=True):
                    try:
                        selected_ts_to_delete = pd.Timestamp(selected_ts_str)
                        if selected_ts_to_delete in st.session_state.maturity_assessments_history:
                            del st.session_state.maturity_assessments_history[selected_ts_to_delete]
                            st.success(f"Deleted assessment from {selected_ts_str}")
                            time.sleep(1)
                            st.rerun()
                        else: st.warning("Could not find selected assessment to delete.")
                    except Exception as e: st.error(f"Error deleting assessment: {e}")
            else:
                 st.button("🗑️ Delete Sel.", disabled=True, key="delete_maturity_hist_disabled", help="Cannot delete the current assessment.", use_container_width=True)


    # --- Apply selected historical scores/evidence if not 'Current' ---
    viewing_current = (selected_ts_str == "Current Assessment")
    display_scores = st.session_state.maturity_scores # Default to current
    display_evidence = st.session_state.maturity_evidence # Default to current

    if not viewing_current:
         try:
              selected_ts = pd.Timestamp(selected_ts_str) # Convert back to timestamp
              if selected_ts in history:
                   loaded_data = history[selected_ts]
                   display_scores = loaded_data.get('scores', st.session_state.maturity_scores) # Fallback
                   display_evidence = loaded_data.get('evidence', st.session_state.maturity_evidence) # Fallback
                   st.info(f"ℹ️ Viewing historical assessment from: {selected_ts_str}")
              else:
                   st.warning("Selected historical assessment not found. Displaying current.")
                   viewing_current = True # Fallback to current
         except Exception as e:
              st.error(f"Error loading historical data: {e}. Displaying current.")
              viewing_current = True # Fallback to current

    st.markdown("---")
    # --- Layout ---
    col1, col2 = st.columns([2, 3]) # Inputs/Evidence on left, Charts/History on right

    with col1:
        st.markdown("#### Scoring Input & Evidence")
        st.caption(f"**Levels:** {', '.join(mock_maturity_levels)}")
        st.write("")

        # Ensure dictionaries exist
        if 'maturity_scores' not in st.session_state: st.session_state.maturity_scores = {dim: 2 for dim in mock_maturity_dimensions}
        if 'maturity_evidence' not in st.session_state: st.session_state.maturity_evidence = {dim: "" for dim in mock_maturity_dimensions}
        if 'maturity_criteria' not in st.session_state: st.session_state.maturity_criteria = default_maturity_criteria

        for dim in mock_maturity_dimensions:
            with st.expander(f"{dim}", expanded=False): # Keep closed by default
                score = display_scores.get(dim, 2)
                evidence = display_evidence.get(dim, "")
                try:
                    current_level = int(score); current_level = max(1, min(5, current_level))
                except (ValueError, TypeError): current_level = 2

                criteria = st.session_state.maturity_criteria.get(dim, {})
                st.markdown("**Level Descriptions:**")
                for lvl in range(1, 6): st.caption(f" L{lvl}: {criteria.get(lvl, 'N/A')}")
                st.write("")

                slider_key = f"maturity_slider_{dim.lower().replace(' & ','_and_').replace(' ','_').replace('/','_')}"
                new_level = st.slider("Select Level (1-5)", 1, 5, current_level, key=slider_key,
                    help=f"Assess maturity level for '{dim}'", disabled=not viewing_current)
                st.caption(f"Selected Level: **{mock_maturity_levels[new_level - 1]}**")

                if viewing_current: st.session_state.maturity_scores[dim] = new_level

                evidence_key = f"maturity_evidence_{dim.lower().replace(' & ','_and_').replace(' ','_').replace('/','_')}"
                new_evidence = st.text_area("Evidence / Comments", value=evidence, key=evidence_key, height=100,
                    placeholder=f"Enter justification or notes for the '{dim}' score...", disabled=not viewing_current)
                if viewing_current: st.session_state.maturity_evidence[dim] = new_evidence


        # Recalculate overall maturity based on *currently displayed* scores
        valid_scores_display = [s for s in display_scores.values() if isinstance(s, (int, float)) and 1 <= s <= 5]
        overall_maturity_display = sum(valid_scores_display) / len(valid_scores_display) if valid_scores_display else 0
        if viewing_current: st.session_state.overall_maturity = overall_maturity_display # Update global state only if viewing current

        maturity_level_index_display = round(overall_maturity_display) - 1
        maturity_level_text_display = mock_maturity_levels[maturity_level_index_display] if 0 <= maturity_level_index_display < len(mock_maturity_levels) else "N/A"

        st.markdown("---")
        st.metric("Overall Average Maturity (Displayed)", f"{overall_maturity_display:.1f}", f"~ {maturity_level_text_display}")


    with col2: # Charts and History column
        st.markdown("#### Maturity Visualization")
        with st.container(border=True):
            # Radar Chart using displayed scores
            fig_radar = create_maturity_radar(display_scores, f"Data Capability Maturity ({selected_ts_str})")
            st.plotly_chart(fig_radar, use_container_width=True)

        st.write("")
        st.markdown("#### ⚖️ Assessment Comparison")
        with st.container(border=True):
             history = st.session_state.get('maturity_assessments_history', {})
             compare_options = {ts.strftime('%Y-%m-%d %H:%M:%S'): ts for ts in sorted(history.keys())}
             compare_options_list = ["Current Assessment"] + list(compare_options.keys())

             sel_col1, sel_col2 = st.columns(2)
             with sel_col1:
                  selection1_str = st.selectbox("Select Baseline:", compare_options_list, key="compare_select1", index=len(compare_options_list)-1 if len(compare_options_list)>1 else 0) # Default to second last (older)
             with sel_col2:
                  selection2_str = st.selectbox("Select Comparison:", compare_options_list, key="compare_select2", index=0) # Default to Current

             scores1, scores2 = None, None
             ts1, ts2 = None, None

             if selection1_str == "Current Assessment": scores1 = st.session_state.maturity_scores; ts1="Current"
             elif selection1_str in compare_options: ts1 = compare_options[selection1_str]; scores1 = history.get(ts1, {}).get('scores')

             if selection2_str == "Current Assessment": scores2 = st.session_state.maturity_scores; ts2="Current"
             elif selection2_str in compare_options: ts2 = compare_options[selection2_str]; scores2 = history.get(ts2, {}).get('scores')

             if scores1 and scores2 and selection1_str != selection2_str:
                  st.markdown(f"Comparing **{selection1_str}** vs **{selection2_str}**")
                  comp_chart_col1, comp_chart_col2 = st.columns(2)
                  with comp_chart_col1:
                       fig_comp1 = create_maturity_radar(scores1, f"{selection1_str}")
                       st.plotly_chart(fig_comp1, use_container_width=True)
                  with comp_chart_col2:
                       fig_comp2 = create_maturity_radar(scores2, f"{selection2_str}")
                       st.plotly_chart(fig_comp2, use_container_width=True)
             elif selection1_str == selection2_str:
                  st.info("Please select two different assessments to compare.")
             else:
                  st.info("Select two assessments from the dropdowns above to compare.")


        st.write("")
        st.markdown("#### Assessment History Trend")
        with st.container(border=True):
            history = st.session_state.get('maturity_assessments_history', {}) # Get updated history
            if len(history) > 1:
                 history_df_data = {}
                 for ts, data in history.items():
                      scores = data.get('scores', {})
                      if isinstance(scores, dict): history_df_data[ts] = scores
                      else: st.warning(f"Skipping history entry for {ts} due to invalid scores format.")

                 if history_df_data:
                      history_df = pd.DataFrame.from_dict(history_df_data, orient='index')
                      history_df = history_df.sort_index()
                      valid_cols = [col for col in history_df.columns if col in mock_maturity_dimensions]
                      if valid_cols: history_df['Overall'] = history_df[valid_cols].mean(axis=1, skipna=True)
                      else: history_df['Overall'] = np.nan
                      st.line_chart(history_df)
                      st.caption("Trend of maturity scores over time based on saved assessments.")
                 else: st.info("No valid historical score data found to plot trend.")
            else: st.info("Save at least two assessments to see the historical trend chart.")


def tab_roadmap_builder():
    st.markdown("## 🗺️ Roadmap Builder")
    st.markdown("Define initiatives within different timeframes, assign owners, estimate effort/cost, and note dependencies.")
    st.markdown("---")

    # --- Filtering ---
    st.sidebar.markdown("## Roadmap Filters")
    combined_roadmap_df = pd.concat(st.session_state.roadmap_data.values(), ignore_index=True) if st.session_state.roadmap_data else pd.DataFrame()
    available_owners = sorted(combined_roadmap_df['Owner'].unique()) if 'Owner' in combined_roadmap_df.columns and not combined_roadmap_df.empty else mock_personas + ["Other", "TBD"]
    available_statuses = sorted(combined_roadmap_df['Status'].unique()) if 'Status' in combined_roadmap_df.columns and not combined_roadmap_df.empty else mock_status_levels

    filter_owner = st.sidebar.multiselect("Filter by Owner:", ["All"] + available_owners, default="All", key="roadmap_filter_owner")
    filter_status = st.sidebar.multiselect("Filter by Status:", ["All"] + available_statuses, default="All", key="roadmap_filter_status")

    # --- Roadmap Item Editing ---
    st.markdown("#### Roadmap Initiatives")
    st.caption("Use the tables below to add, edit, or remove roadmap items. Double-click cells to edit. Use '+' to add rows, select rows and press 'Delete' to remove.")
    st.write("")

    roadmap_tabs = st.tabs(mock_roadmap_categories)
    all_roadmap_tasks_list = [] # To collect DFs for combining later

    for i, category in enumerate(mock_roadmap_categories):
        with roadmap_tabs[i]:
            roadmap_key = f"roadmap_df_{category.replace(' ','_')}"

            # Initialize DF in state if needed
            if roadmap_key not in st.session_state or not isinstance(st.session_state[roadmap_key], pd.DataFrame):
                initial_items = default_roadmap_items.get(category, [])
                st.session_state[roadmap_key] = pd.DataFrame(initial_items)
                # Ensure Progress & Dependencies columns exist
                if 'Progress (%)' not in st.session_state[roadmap_key].columns: st.session_state[roadmap_key]['Progress (%)'] = 0
                if 'Dependencies (IDs)' not in st.session_state[roadmap_key].columns: st.session_state[roadmap_key]['Dependencies (IDs)'] = ''
                st.session_state[roadmap_key]['Progress (%)'] = pd.to_numeric(st.session_state[roadmap_key]['Progress (%)'], errors='coerce').fillna(0).astype(int)
                st.session_state[roadmap_key]['Dependencies (IDs)'] = st.session_state[roadmap_key]['Dependencies (IDs)'].fillna('').astype(str)


            current_df_for_category = st.session_state[roadmap_key].copy()

            # --- Apply Filters ---
            df_to_display = current_df_for_category.copy()
            filter_active = False
            if "All" not in filter_owner and 'Owner' in df_to_display.columns:
                 df_to_display = df_to_display[df_to_display['Owner'].isin(filter_owner)]; filter_active = True
            if "All" not in filter_status and 'Status' in df_to_display.columns:
                 df_to_display = df_to_display[df_to_display['Status'].isin(filter_status)]; filter_active = True

            if filter_active:
                 st.info(f"ℹ️ Displaying filtered view for {category}. Edits apply to the underlying full data.")


            # --- Define default ID ---
            id_prefix = category.split(" ")[0][:1].upper()
            next_id_num = 1
            if not current_df_for_category.empty and 'ID' in current_df_for_category.columns:
                 ids = current_df_for_category['ID'].astype(str)
                 numeric_suffixes = ids[ids.str.match(f'^{id_prefix}\\d+$')].str.extract(f'^{id_prefix}(\\d+)$')[0].dropna().astype(int)
                 if not numeric_suffixes.empty: next_id_num = numeric_suffixes.max() + 1
                 else: next_id_num = len(current_df_for_category) + 1
            default_id = f"{id_prefix}{next_id_num}"


            # --- Data Editor ---
            try:
                edited_df = st.data_editor(
                    df_to_display, # Display the filtered or full DF
                    num_rows="dynamic",
                    key=f"editor_{category.replace(' ','_')}",
                    column_config={
                        "ID": st.column_config.TextColumn("ID", help="Unique ID (e.g., QW1). Auto-suggested.", default=default_id, required=True, validate="^\\S+$"),
                        "Task": st.column_config.TextColumn("Task Description", width="large", required=True),
                        "Owner": st.column_config.SelectboxColumn("Owner", options=mock_personas + ["Other", "TBD"], default="TBD", required=True),
                        "Effort": st.column_config.SelectboxColumn("Effort", options=mock_effort_levels, default="Medium", required=True),
                        "Cost": st.column_config.SelectboxColumn("Cost Estimate", options=mock_cost_levels, default="$", required=True, help="Relative cost ($=Low)"),
                        "Status": st.column_config.SelectboxColumn("Status", options=mock_status_levels, default="Not Started", required=True),
                        "Progress (%)": st.column_config.NumberColumn("Progress (%)", min_value=0, max_value=100, step=5, default=0, required=True, format="%d%%"),
                        "Dependencies (IDs)": st.column_config.TextColumn("Dependencies (IDs)", help="Comma-separated IDs of prerequisite tasks", default="")
                    },
                    use_container_width=True,
                    hide_index=True,
                )

                # --- Update Original DataFrame in Session State ---
                if filter_active:
                     original_df = st.session_state[roadmap_key].copy()
                     edited_ids_in_view = set(edited_df['ID'])
                     original_ids_in_view = set(df_to_display['ID'])
                     for index, row in edited_df.iterrows(): original_df.loc[original_df['ID'] == row['ID']] = row.to_dict()
                     new_ids = edited_ids_in_view - original_ids_in_view
                     if new_ids:
                          new_rows = edited_df[edited_df['ID'].isin(new_ids)]
                          original_df = pd.concat([original_df, new_rows], ignore_index=True)
                     deleted_ids = original_ids_in_view - edited_ids_in_view
                     original_df = original_df[~original_df['ID'].isin(deleted_ids)]
                     st.session_state[roadmap_key] = original_df.reset_index(drop=True)
                else:
                     if not current_df_for_category.equals(edited_df):
                          st.session_state[roadmap_key] = edited_df.reset_index(drop=True)

            except Exception as e:
                 st.error(f"Error rendering roadmap editor for {category}: {e}")
                 st.dataframe(current_df_for_category) # Display non-editable on error

            df_with_cat = st.session_state[roadmap_key].copy()
            df_with_cat['Category'] = category
            all_roadmap_tasks_list.append(df_with_cat)


    # Combine all roadmap items into a single DataFrame for Gantt/Export
    if all_roadmap_tasks_list:
        full_roadmap_df = pd.concat(all_roadmap_tasks_list, ignore_index=True)
        # Ensure Progress & Dependencies columns are correct type after concat
        if 'Progress (%)' in full_roadmap_df.columns: full_roadmap_df['Progress (%)'] = pd.to_numeric(full_roadmap_df['Progress (%)'], errors='coerce').fillna(0).astype(int)
        else: full_roadmap_df['Progress (%)'] = 0
        if 'Dependencies (IDs)' in full_roadmap_df.columns: full_roadmap_df['Dependencies (IDs)'] = full_roadmap_df['Dependencies (IDs)'].fillna('').astype(str)
        else: full_roadmap_df['Dependencies (IDs)'] = ''
    else:
        full_roadmap_df = pd.DataFrame(columns=['ID', 'Task', 'Owner', 'Effort', 'Cost', 'Status', 'Progress (%)', 'Dependencies (IDs)', 'Category'])

    # --- Store combined DF in state for export tab ---
    st.session_state.full_roadmap_for_export = full_roadmap_df

    st.markdown("---")
    st.markdown("#### 📊 Roadmap Visualization (Gantt Chart)")
    st.caption("Conceptual Gantt representation. Dates are simulated based on category and effort. Filters applied.")
    st.write("")

    with st.container(border=True):
        # Apply filters to the full roadmap *before* generating Gantt
        gantt_df_filtered = full_roadmap_df.copy()
        if "All" not in filter_owner and 'Owner' in gantt_df_filtered.columns:
            gantt_df_filtered = gantt_df_filtered[gantt_df_filtered['Owner'].isin(filter_owner)]
        if "All" not in filter_status and 'Status' in gantt_df_filtered.columns:
            gantt_df_filtered = gantt_df_filtered[gantt_df_filtered['Status'].isin(filter_status)]

        if not gantt_df_filtered.empty:
            fig_gantt = create_gantt_chart(gantt_df_filtered)
            if fig_gantt:
                 st.plotly_chart(fig_gantt, use_container_width=True)
            else:
                 st.info("Could not generate Gantt chart based on current data or filters.")
        else:
            st.info("No roadmap items match the current filters, or no items added yet.")


def tab_export():
    st.markdown("## 📤 Export Center")
    st.markdown("Configure and generate simulated reports or download raw assessment data.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⚙️ Report Configuration")
        with st.container(border=True):
            st.markdown("**Select Content:**")
            all_sections = list(TABS.keys())
            options = st.session_state.get('export_options', {})
            selected_sections = st.multiselect(
                "Include Sections:", options=all_sections,
                default=options.get('selected_sections', all_sections), key="export_select_sections"
            )
            options['selected_sections'] = selected_sections

            st.markdown("**Formatting Options:**")
            logo_available = st.session_state.get('uploaded_logo_bytes') is not None
            options['include_branding'] = st.checkbox("Include Organization Logo",
                value=options.get('include_branding', False) and logo_available, key="export_branding", disabled=not logo_available)
            if options['include_branding'] and not logo_available: st.warning("Logo not uploaded on Landing Page.", icon="⚠️")

            options['include_glossary'] = st.checkbox("Include Data Strategy Glossary", value=options.get('include_glossary', True), key="export_glossary")
            options['include_raw_data'] = st.checkbox("Include Raw Assessment Data Tables", value=options.get('include_raw_data', False), key="export_raw_data")
            st.session_state.export_options = options
            st.caption("_(Save/Load configuration feature placeholder)_")


    with col2:
        st.markdown("#### 🚀 Generate Report (Simulated)")
        with st.container(border=True):
            target_persona = st.selectbox("Tailor Report For:", options=["General Audience"] + mock_personas, key="export_target_persona")

            st.markdown("**Select Format:**")
            fmt_col1, fmt_col2 = st.columns(2)
            with fmt_col1: pdf_button = st.button("📄 Generate Mock PDF", key="generate_mock_pdf", use_container_width=True)
            with fmt_col2: ppt_button = st.button("🖥️ Generate Mock PPT", key="generate_mock_ppt", use_container_width=True)

            # --- Simulation Logic ---
            if pdf_button or ppt_button:
                 file_type = "PDF" if pdf_button else "PPT"
                 with st.spinner(f"Simulating {file_type} generation for {target_persona}..."):
                     report_content = f"## Data Strategy Report ({file_type} Mock)\n\n"
                     report_content += f"**Target Audience:** {target_persona}\n"
                     current_time = get_current_time()
                     time_str = current_time.strftime('%Y-%m-%d %H:%M:%S %Z') if current_time.tzinfo else current_time.strftime('%Y-%m-%d %H:%M:%S')
                     report_content += f"**Generated:** {time_str} from {APP_LOCATION}\n"
                     report_content += f"**Sector Focus:** {st.session_state.get('selected_sector', 'N/A')}\n"
                     report_content += f"**Includes Logo:** {'Yes' if options.get('include_branding') and logo_available else 'No'}\n\n"

                     report_content += "**--- Selected Sections ---**\n"
                     included_sections = options.get('selected_sections', [])
                     for section in included_sections: report_content += f"- {section}\n"
                     report_content += "\n"

                     # Add placeholder content based on persona/sections
                     if "📄 Executive Summary" in included_sections:
                          report_content += "**--- Executive Summary Snippet ---**\n"
                          summary_text = st.session_state.get('editable_exec_summary') or st.session_state.get('exec_summary_text', "Summary not available.")
                          report_content += summary_text.split('\n\n')[0] + "...\n\n"
                     if "📈 Maturity Assessment" in included_sections: report_content += "**--- Maturity Highlights ---**\n[Placeholder: Radar Chart Image / Key Scores]\n\n"
                     if "🗺️ Roadmap Builder" in included_sections: report_content += "**--- Roadmap Overview ---**\n[Placeholder: Gantt Chart Image / Priority Items List]\n\n"
                     if options.get('include_glossary'):
                          report_content += "**--- Glossary ---**\n"
                          glossary_terms = st.session_state.get('business_glossary', {})
                          if glossary_terms:
                               for term, definition in glossary_terms.items(): report_content += f"- **{term}:** {definition}\n"
                          else: report_content += "[Glossary is empty]\n"
                          report_content += "\n"
                     if options.get('include_raw_data'): report_content += "**--- Raw Data Tables ---**\n[Placeholder: Maturity Scores Table, Governance Scores Table]\n\n"

                     report_content += f"-- End of Mock {file_type} --\n"
                     report_content += "\n*Note: Actual generation requires libraries like python-pptx or reportlab/fpdf2.*"
                     time.sleep(1.5)

                     sim_key = f'simulated_report_{target_persona}_{file_type}'
                     st.session_state[sim_key] = report_content
                     st.success(f"Mock {file_type} report for {target_persona} simulated!")

                     st.download_button(
                         label=f"⬇️ Download Simulated {file_type} (.txt)", data=report_content.encode('utf-8'),
                         file_name=f"Mock_Report_{target_persona.replace(' ','')}_{file_type}_{current_time.strftime('%Y%m%d')}.txt",
                         mime="text/plain", key=f"download_{sim_key}"
                     )


    st.markdown("---")
    st.markdown("#### 💾 Export Raw Data")
    with st.container(border=True):
         st.caption("Download specific data tables generated within the app.")
         data_exp_col1, data_exp_col2, data_exp_col3 = st.columns(3)

         # Export Maturity History
         with data_exp_col1:
             history = st.session_state.get('maturity_assessments_history', {})
             if history:
                  history_df_data = {}
                  for ts, data in history.items():
                       scores = data.get('scores', {}); evidence = data.get('evidence', {})
                       combined = {f"{dim}_Score": scores.get(dim) for dim in mock_maturity_dimensions}
                       combined.update({f"{dim}_Evidence": evidence.get(dim) for dim in mock_maturity_dimensions})
                       history_df_data[ts] = combined
                  history_df = pd.DataFrame.from_dict(history_df_data, orient='index')
                  history_df.index.name = "Assessment Timestamp"; history_df = history_df.sort_index()
                  csv_maturity = history_df.to_csv().encode('utf-8')
                  st.download_button("Maturity History (CSV)", csv_maturity, f"Maturity_History_{get_current_time().strftime('%Y%m%d')}.csv", "text/csv", key="exp_maturity", use_container_width=True)
             else: st.button("Maturity History (CSV)", disabled=True, help="No history saved yet.", use_container_width=True)

         # Export Full Roadmap
         with data_exp_col2:
             roadmap_df_exp = st.session_state.get('full_roadmap_for_export')
             if roadmap_df_exp is not None and not roadmap_df_exp.empty:
                  csv_roadmap = roadmap_df_exp.to_csv(index=False).encode('utf-8')
                  st.download_button("Full Roadmap (CSV)", csv_roadmap, f"Full_Roadmap_{get_current_time().strftime('%Y%m%d')}.csv", "text/csv", key="exp_roadmap", use_container_width=True)
             else: st.button("Full Roadmap (CSV)", disabled=True, help="Roadmap is empty.", use_container_width=True)

         # Export Interview Data
         with data_exp_col3:
             all_interview_data_exp = []
             for persona, notes_dict in st.session_state.get('interview_notes', {}).items():
                  questions = st.session_state.get('interview_questions', {}).get(persona, [])
                  scores_dict = st.session_state.get('interview_confidence', {}).get(persona, {})
                  for i_str, note in notes_dict.items():
                      try:
                          i = int(i_str)
                          if i < len(questions):
                              all_interview_data_exp.append({
                                  "Persona": persona, "Q_Index": i + 1, "Question": questions[i],
                                  "Confidence": scores_dict.get(i_str, np.nan), "Notes": note
                              })
                      except ValueError: continue
             if all_interview_data_exp:
                  export_df_int = pd.DataFrame(all_interview_data_exp)
                  csv_export_int = export_df_int.to_csv(index=False).encode('utf-8')
                  st.download_button("Interview Data (CSV)", csv_export_int, f"Interview_Data_{get_current_time().strftime('%Y%m%d')}.csv", "text/csv", key="exp_interviews_raw", use_container_width=True)
             else: st.button("Interview Data (CSV)", disabled=True, help="No interview data entered.", use_container_width=True)

# --- [Risk Assessment Placeholder Tab] ---
# def display_risk_module():
#      st.markdown("## ⚠️ Risk Assessment (Placeholder)")
#      st.markdown("Identify, assess, and link risks to strategy elements.")
#      st.markdown("---")
#      st.info("This section is a placeholder for a risk management module.")
#      # Add UI elements for adding risks (description, likelihood, impact, mitigation)
#      # Add UI elements for linking risks to maturity dimensions or roadmap items
#      # Display a risk matrix or register
# --- [End Risk Assessment Placeholder Tab] ---


# --- Main App Execution ---

# Define Tab Titles and Corresponding Functions
TABS = {
    "🏠 Landing Page": tab_landing_page,
    "📄 Executive Summary": tab_executive_summary,
    "🎙️ Stakeholder Interviews": tab_stakeholder_interviews,
    "🔍 Data Upload & Analysis": tab_data_upload_analysis,
    "🏛️ Data Governance": tab_data_governance,
    "📈 Maturity Assessment": tab_maturity_assessment,
    "🗺️ Roadmap Builder": tab_roadmap_builder,
    # "⚠️ Risk Assessment": display_risk_module, # Example of adding a new placeholder tab
    "📤 Export": tab_export,
}

# --- Load state at the beginning ---
if 'state_initialized' not in st.session_state:
     load_app_state_json() # Use JSON load

# --- Sidebar Info ---
st.sidebar.markdown("---")
st.sidebar.header("App Info")
st.sidebar.info(f"""
**Version:** {st.session_state.get('app_version', 'N/A')}
**Sector:** {st.session_state.get('selected_sector', 'N/A')}
**Data Loaded:** {st.session_state.get('current_data_filename', 'None')}
**Last Saved:** {datetime.datetime.fromtimestamp(os.path.getmtime(STATE_FILE)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(STATE_FILE) else 'Never'}
""")
st.sidebar.markdown("---")
# --- [Sidebar Guidance Placeholder] ---
# current_tab_title = st.session_state.get('current_tab', list(TABS.keys())[0])
# current_index = list(TABS.keys()).index(current_tab_title)
# next_index = (current_index + 1) % len(TABS)
# next_tab_title = list(TABS.keys())[next_index]
# st.sidebar.markdown("---")
# st.sidebar.markdown(f"**Next Step Suggestion:**\n➡️ Proceed to **{next_tab_title}**")
# st.sidebar.markdown("---")
# --- [End Sidebar Guidance Placeholder] ---


# Create Tabs
tab_titles = list(TABS.keys())
streamlit_tabs = st.tabs(tab_titles)

# Populate Tabs
for i, title in enumerate(tab_titles):
    with streamlit_tabs[i]:
        tab_func = TABS.get(title)
        if tab_func:
            try:
                # Track current tab (useful if needed elsewhere)
                st.session_state.current_tab = title
                tab_func()
            except Exception as e:
                st.error(f"An error occurred in the '{title}' tab:")
                st.exception(e) # Show detailed traceback
        else:
            st.error(f"Error: No function found for tab '{title}'")

# --- Auto-save option (optional) ---
# if st.sidebar.checkbox("Auto-save state on change", key="autosave_toggle", value=False):
#     save_app_state_json() # Be careful with performance on complex state changes
