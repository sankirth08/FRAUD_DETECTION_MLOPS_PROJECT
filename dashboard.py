
import streamlit as st
import requests

st.set_page_config(
    page_title="FraudGuard | Fraud Detection",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}
.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #14213d;
}
.subtitle {
    color: #64748b;
    font-size: 16px;
}
div.stButton > button {
    background-color: #2457d6;
    color: white;
    border-radius: 8px;
    height: 46px;
    width: 100%;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #173ea5;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🛡️ FraudGuard</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Machine Learning Transaction Risk Monitoring</div>',
    unsafe_allow_html=True
)

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader("Transaction Details")

    with st.form("transaction_form"):
        step = st.number_input("Transaction Step", min_value=1, value=1)

        transaction_type = st.selectbox(
            "Transaction Type",
            ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
        )

        amount = st.number_input(
            "Transaction Amount", min_value=0.0, value=181.0
        )

        st.markdown("#### Origin Account")
        oldbalanceOrg = st.number_input(
            "Previous Balance", min_value=0.0, value=181.0
        )
        newbalanceOrig = st.number_input(
            "New Balance", min_value=0.0, value=0.0
        )

        st.markdown("#### Destination Account")
        oldbalanceDest = st.number_input(
            "Previous Destination Balance", min_value=0.0, value=0.0
        )
        newbalanceDest = st.number_input(
            "New Destination Balance", min_value=0.0, value=0.0
        )

        submitted = st.form_submit_button("Analyze Transaction")

with right:
    st.subheader("Risk Analysis")

    if submitted:
        data = {
            "step": step,
            "type": transaction_type,
            "amount": amount,
            "oldbalanceOrg": oldbalanceOrg,
            "newbalanceOrig": newbalanceOrig,
            "oldbalanceDest": oldbalanceDest,
            "newbalanceDest": newbalanceDest
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                probability = result["fraud_probability"]

                st.metric("Estimated Fraud Probability", f"{probability:.2%}")
                st.progress(min(max(probability, 0.0), 1.0))

                if result["fraud_prediction"] == 1:
                    st.error("⚠️ Transaction flagged as potential fraud")
                else:
                    st.success("✅ Transaction not flagged at the current threshold")

                st.caption(
                    "The prediction is a model estimate, not a guarantee "
                    "that the transaction is safe."
                )

            else:
                st.error(f"API returned error {response.status_code}")
                st.code(response.text)

        except requests.exceptions.RequestException:
            st.error(
                "Cannot connect to FastAPI. Make sure the backend "
                "is running at http://127.0.0.1:8000."
            )

    else:
        st.info("Enter transaction details and click Analyze Transaction.")
        st.markdown("**Model threshold:** 80%")
        st.caption(
            "Transactions with estimated fraud probability at or above "
            "80% are flagged."
        )

st.divider()
st.caption("FraudGuard | Educational ML project | Logistic Regression")