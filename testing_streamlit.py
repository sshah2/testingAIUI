import streamlit as st

# Define custom CSS to apply card styling
def card_layout():
    st.markdown("""
    <style>
    .card {
        margin: 10px;
        padding: 10px;  /* Reduced padding */
        border: none;
        border-radius: 10px;
        box-shadow: 0px 0px 5px 0px grey;
        transition: 0.3s;
        width: 95%;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: start; /* Align items to the start of the card */
        align-items: center; /* Center align the items horizontally */
        min-height: 250px; /* Minimum height to standardize card size */
    }
    .card:hover {
        box-shadow: 0px 0px 11px 0px rgba(0,0,0,0.2);
    }
    .card img {
        margin-top: 10px; /* Adjusted margin */
        margin-bottom: 10px; /* Adjusted margin */
        width: 50px; /* Adjust the size of the images */
        margin-left: auto;
        margin-right: auto;
    }
    .card h3 {
        margin-top: 5px; /* Adjusted spacing */
        margin-bottom: 5px; /* Added bottom margin */
        font-weight: bold;
        font-size: 18px; /* Adjusted font size */
    }
    .card p {
        margin: 0;
        padding: 0; /* Adjusted padding */
        color: grey;
        font-size: 12px; /* Reduced font size */
        line-height: 1.5; /* Adjusted line height for readability */
    }
    </style>
    """, unsafe_allow_html=True)

# Main function to layout the app
def main():
    # Apply the card layout styles
    card_layout()

    st.title("Explore Benefits")

    # You can use a loop to generate multiple cards if you have many
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="card">
                <img src="https://peak.my.site.com/peak/resource/1701925644000/landingPageAssets/LandingPage/FoodAssistance/Food.png" alt="SNAP">
                <h3>SNAP</h3>
                <p>The Supplemental Nutrition Assistance Program (SNAP) provides food assistance for households. It offers a monthly amount to purchase food via an EBT card.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="card">
                <img src="https://peak.my.site.com/peak/resource/1701925644000/landingPageAssets/LandingPage/MedicalAssistance/Medicalassistance.png" alt="Health Coverage">
                <h3>Medical</h3>
                <p>Medicaid and CHP+ offer low-cost health insurance for eligible children and adults in the State of Wellbeing.</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="card">
                <img src="https://peak.my.site.com/peak/resource/1701925644000/landingPageAssets/LandingPage/CashAssistance/Group.png" alt="Cash Assistance">
                <h3>Cash</h3>
                <p>TANF provides cash assistance to families, supporting employment and financial stability in the State of Wellbeing.</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
