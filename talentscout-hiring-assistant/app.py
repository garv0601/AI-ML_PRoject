import streamlit as st
import pandas as pd
import openai
import os

# ---- Set OpenRouter API ----
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# ---- App Title ----
st.title("🤖 TalentScout: AI Hiring Assistant")

# ---- Candidate Info Form ----
st.header("📝 Candidate Information")
with st.form("candidate_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
    desired_position = st.text_input("Desired Position")
    location = st.text_input("Current Location")
    tech_stack = st.text_input("Tech Stack (e.g., Python, React, SQL)")
    submitted = st.form_submit_button("Submit")

if submitted:
    # ---- Save candidate info ----
    candidate_data = {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Experience": experience,
        "Desired Position": desired_position,
        "Current Location": location,
        "Tech Stack": tech_stack
    }

    df = pd.DataFrame([candidate_data])
    file_exists = os.path.exists("candidates.csv")
    df.to_csv("candidates.csv", mode="a", index=False, header=not file_exists)

    # ---- Generate 3 MCQ Questions using OpenRouter ----
    prompt = f"""
    You are an expert technical interviewer.
    Based on the following candidate profile:
    - Tech Stack: {tech_stack}
    - Desired Position: {desired_position}
    - Experience: {experience} years

    Generate 3 multiple-choice technical questions to assess their skills.
    Format:
    Q1. Question text?
    a) Option A
    b) Option B
    c) Option C
    d) Option D
    Correct Answer: <option letter>

    Q2...
    """

    with st.spinner("Generating technical questions..."):
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful technical interviewer."},
                {"role": "user", "content": prompt}
            ]
        )
        questions_text = response.choices[0].message.content

    # ---- Parse and Display Questions ----
    st.subheader("🧠 Technical MCQ Test")
    st.markdown("Please answer the following questions:")

    questions = []
    answers = []
    current_question = ""
    options = []

    for line in questions_text.splitlines():
        line = line.strip()
        if line.startswith("Q"):
            if current_question:
                questions.append((current_question, options, correct))
            current_question = line
            options = []
        elif line.startswith(("a)", "b)", "c)", "d)")):
            options.append(line)
        elif line.startswith("Correct Answer"):
            correct = line.split(":")[-1].strip().lower()

    if current_question:
        questions.append((current_question, options, correct))

    user_answers = {}
    with st.form("mcq_form"):
        for idx, (q_text, opts, _) in enumerate(questions):
            st.markdown(f"**{q_text}**")
            selected = st.radio(f"Select an answer for Question {idx+1}", opts, key=idx)
            user_answers[q_text] = selected
        submitted_mcq = st.form_submit_button("Submit Answers")

    # ---- Handle MCQ Submission ----
    if submitted_mcq:
        answers_df = pd.DataFrame([{
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Q": q,
            "Answer": a
        } for q, a in user_answers.items()])
        answers_df.to_csv("candidate_answers.csv", mode="a", index=False, header=not os.path.exists("candidate_answers.csv"))

        st.success("✅ Your answers have been submitted successfully!")
        st.markdown("🎉 **Thank you for participating in the assessment. We'll be in touch!**")




