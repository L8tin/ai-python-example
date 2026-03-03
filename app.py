import matplotlib
matplotlib.use('Agg')  # Ensure non-GUI backend
from flask import Flask, request, render_template_string, send_from_directory, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import tempfile
from functools import wraps
import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, redirect, url_for, render_template, session, flash


#### OpenAI Additions ####
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, flash
from dotenv import load_dotenv
import os

load_dotenv()  # load .env variables

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = bool(OPENAI_API_KEY)
if USE_OPENAI:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
MAX_GENERATIONS_PER_SESSION = 20

@app.route("/catbio", methods=["GET", "POST"])
def generate_bio():
    if "bio_count" not in session:
        session["bio_count"] = 0

    bio = ""
    # default form values
    form_fields = {
        "name": "",
        "age": "",
        "personality": "",
        "energy": "",
        "good_with_kids": "Yes",
        "gender": "M",
        "breed": "D.S.H.",
        "combo_vaccine_date": "",
        "rabies_vaccine_date": "",
        "arrival_date": "",
        "adoption_fee": "",
        "extra_info": ""
    }

    if request.method == "POST":
        if session["bio_count"] >= MAX_GENERATIONS_PER_SESSION:
            flash(f"You have reached the limit of {MAX_GENERATIONS_PER_SESSION} bios per session.", "error")
            return render_template("catbio.html", **form_fields, bio=bio)

        session["bio_count"] += 1

        # Grab all form fields
        for key in form_fields:
            form_fields[key] = request.form.get(key, "")

        # Generate the bio
        if USE_OPENAI:
            try:
                prompt = f"""
                Write a heartwarming, adoption-ready description for a rescue cat in under 200 words. 
                Make it friendly, engaging, and highlight the cat's personality and special quirks. 
                Include the following details naturally: 

                - Name: {form_fields['name']}
                - Age: {form_fields['age']}
                - Personality: {form_fields['personality']}
                - Energy level: {form_fields['energy']}
                - Good with kids: {form_fields['good_with_kids']}

                End with a short inviting sentence encouraging potential adopters to meet the cat.
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                bio = response.choices[0].message.content
            except Exception as e:
                bio = f"(OpenAI call failed: {e})\nUsing mock bio instead.\n" \
                      f"{form_fields['name']} is a {form_fields['age']}-year-old cat with {form_fields['personality']} personality, energy: {form_fields['energy']}, good with kids: {form_fields['good_with_kids']}."
        else:
            bio = f"{form_fields['name']} is a {form_fields['age']}-year-old cat with {form_fields['personality']} personality, energy: {form_fields['energy']}, good with kids: {form_fields['good_with_kids']}."

    return render_template("catbio.html", **form_fields, bio=bio)


@app.route('/')
def home():
    return render_template('catcranium.html')


if __name__ == "__main__":
    app.run(debug=True)
