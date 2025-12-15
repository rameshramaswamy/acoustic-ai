import streamlit as st

st.header("🧠 ML Label Validation (Human-in-the-Loop)")

st.info("Listen to the audio clip and verify if the 'NewCNNLeaf' model classified it correctly.")

# Mock Iteration
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Clip: #UUID-9823")
    st.audio("https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav", format="audio/wav")
    
    st.markdown("**Model Prediction:**")
    st.warning("⚠️ Polluting (Confidence: 0.65)")

with col2:
    with st.form("validation_form"):
        choice = st.radio("Is this correct?", ["Yes, it is Polluting", "No, it is Nature/Human", "Unsure"])
        correction = st.selectbox("Correct Class if wrong", ["Construction", "Traffic", "Siren", "Bird", "Wind"])
        submitted = st.form_submit_button("Submit & Retrain")
        
        if submitted:
            st.success("Feedback recorded. Model will be updated in next nightly run.")