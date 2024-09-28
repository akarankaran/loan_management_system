import streamlit as st
from pymongo import MongoClient
import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client['loan_management']  # Database name
customers_collection = db['customers']  # Collection for customer data
documents_collection = db['documents']  # Collection for document data
loans_collection = db['loans']  # Collection for loan applications

# Function to insert customer data into MongoDB
def save_customer_data(customer_data):
    customer_id = customers_collection.insert_one(customer_data).inserted_id
    return customer_id

# Function to insert document data into MongoDB
def save_document(customer_id, document_type, file):
    document_data = {
        "customer_id": customer_id,
        "document_type": document_type,
        "document_path": file.name,
        "uploaded_at": datetime.datetime.now()
    }
    documents_collection.insert_one(document_data)

# Function to insert loan data into MongoDB
def save_loan_data(loan_data):
    loan_id = loans_collection.insert_one(loan_data).inserted_id
    return loan_id

# Streamlit interface
st.title("MSME Loan Onboarding System")

# Step 1: Personal & Business Information
st.header("Step 1: Personal & Business Information")

with st.form(key='business_info'):
    person_name = st.text_input("Name of Person Applying")
    business_name = st.text_input("Business Name")
    vintage = st.number_input("Vintage (Age of Business in years)", min_value=0, max_value=100, step=1)
    is_registered = st.selectbox("Is the Business Registered?", ["Yes", "No"])
    gst_status = st.selectbox("Does the Business Have GST?", ["Yes", "No"])
    industry = st.selectbox("Industry", ["Retail", "Wholesale", "Manufacturing", "Service", "Others"])
    phone_number = st.text_input("Phone Number")
    
    submit_button = st.form_submit_button(label="Next")

# If customer submits the form, save data to MongoDB
if submit_button:
    customer_data = {
        "person_name": person_name,
        "business_name": business_name,
        "vintage": vintage,
        "is_registered": is_registered == "Yes",
        "gst_status": gst_status == "Yes",
        "industry": industry,
        "phone_number": phone_number,
        "created_at": datetime.datetime.now()
    }
    
    customer_id = save_customer_data(customer_data)
    st.session_state['customer_data'] = customer_data
    st.session_state['customer_id'] = customer_id
    st.success("Customer information saved. Proceed to document upload.")

# Step 2: Document Collection
if 'customer_id' in st.session_state:
    st.header("Step 2: Document Upload")
    
    with st.form(key='document_upload'):
        business_registration_proof = st.file_uploader("Upload Business Registration Proof", type=['pdf', 'jpg', 'png'])
        bank_statements = st.file_uploader("Upload Bank Statements (6 months)", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)
        itr_documents = st.file_uploader("Upload Income Tax Returns (2 years)", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)
        
        gst_documents = st.file_uploader("Upload GST Returns (2 years)", type=['pdf', 'jpg', 'png'], accept_multiple_files=True) if st.session_state['customer_data']['gst_status'] else None
        
        submit_documents_button = st.form_submit_button(label="Submit Documents")

    if submit_documents_button:
        if business_registration_proof:
            save_document(st.session_state['customer_id'], "Business Registration", business_registration_proof)
        if bank_statements:
            for statement in bank_statements:
                save_document(st.session_state['customer_id'], "Bank Statement", statement)
        if itr_documents:
            for itr in itr_documents:
                save_document(st.session_state['customer_id'], "Income Tax Return", itr)
        if gst_documents:
            for gst in gst_documents:
                save_document(st.session_state['customer_id'], "GST Return", gst)
        st.success("Documents uploaded successfully. Proceed to loan application.")

# Step 3: Loan Application
if 'customer_id' in st.session_state:
    st.header("Step 3: Loan Application")
    
    with st.form(key='loan_application'):
        loan_amount = st.number_input("Loan Amount Requested", min_value=1000, step=500)
        loan_purpose = st.selectbox("Purpose of Loan", ["Working Capital", "Expansion", "Inventory", "Other"])
        
        submit_loan_button = st.form_submit_button(label="Submit Loan Application")

    if submit_loan_button:
        loan_data = {
            "customer_id": st.session_state['customer_id'],
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "application_date": datetime.datetime.now(),
            "status": "Submitted"
        }
        save_loan_data(loan_data)
        st.success("Loan application submitted successfully.")
