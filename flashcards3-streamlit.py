import streamlit as st
import random
import re

# Load the verb data from the file
verbs = []
with open("verba.txt", "r", encoding="utf-8") as file:
    next(file)  # Skip header
    for line in file:
        columns = [col.strip() for col in re.split(r'\t+', line.strip())]
        columns += [""] * (6 - len(columns))  # Adjust for the new column
        verbs.append({
            "Infinitief": columns[0],
            "Imperfectum sing": columns[1],
            "Imperfectum plur": columns[2],
            "Participium": columns[3],
            "h/z": columns[4],
            "Translation": columns[5]  # New column for translation
        })

# Initialize session state
if 'show_answer' not in st.session_state:
    st.session_state['show_answer'] = False
if 'mistaken_cards' not in st.session_state:
    st.session_state['mistaken_cards'] = []
if 'incorrect_count' not in st.session_state:
    st.session_state['incorrect_count'] = 0
if 'cards_to_review' not in st.session_state:
    st.session_state['cards_to_review'] = list(verbs)
if 'original_count' not in st.session_state:
    st.session_state['original_count'] = len(st.session_state['cards_to_review'])
if 'current_verb' not in st.session_state:
    st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review']) if st.session_state['cards_to_review'] else None

# Helper function to pick a new card only when needed
def pick_new_card():
    if st.session_state['cards_to_review']:
        st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review'])
        st.session_state['cards_to_review'].remove(st.session_state['current_verb'])
    else:
        # Reset for mistaken cards review if available
        if st.session_state['mistaken_cards']:
            st.session_state['cards_to_review'] = st.session_state['mistaken_cards'][:]
            st.session_state['mistaken_cards'] = []
            st.session_state['incorrect_count'] = 0
            st.session_state['original_count'] = len(st.session_state['cards_to_review'])
            st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review'])
            st.session_state['cards_to_review'].remove(st.session_state['current_verb'])
        else:
            st.session_state['current_verb'] = None  # No more cards to review

# Define functions for button actions
def show_answer():
    st.session_state['show_answer'] = True

def mark_as_known():
    st.session_state['show_answer'] = False
    pick_new_card()

def mark_as_unknown():
    st.session_state['mistaken_cards'].append(st.session_state['current_verb'])
    st.session_state['incorrect_count'] += 1
    st.session_state['show_answer'] = False
    pick_new_card()

# Main interface
st.title("Onregelmatige werkwoorden (Niveau 3) Flashcards")

# Display progress bar
if st.session_state['original_count'] > 0:
    progress = (st.session_state['original_count'] - len(st.session_state['cards_to_review']) - st.session_state['incorrect_count']) / st.session_state['original_count']
    st.progress(progress)

# Display current verb and translation
if st.session_state['current_verb']:
    st.write("### Infinitief")
    st.write(st.session_state['current_verb']['Infinitief'])
    if st.session_state['current_verb']["Translation"]:
        st.write(f"({st.session_state['current_verb']['Translation']})")
    
    # Show answer if requested
    if st.session_state['show_answer']:
        st.write("### Conjugation")
        st.write(f"Imperfectum: {st.session_state['current_verb']['Imperfectum sing']}, {st.session_state['current_verb']['Imperfectum plur']}")
        st.write(f"Participium: {st.session_state['current_verb']['Participium']} ({st.session_state['current_verb']['h/z']})")

        # "Yes" and "No" buttons for tracking mistakes
        col1, col2 = st.columns(2)
        col1.button("Yes", on_click=mark_as_known)
        col2.button("No", on_click=mark_as_unknown)
    else:
        # Show answer button
        st.button("Show Answer", on_click=show_answer)

# Display remaining count
remaining = st.session_state['original_count'] - len(st.session_state['cards_to_review'])
st.write(f"Progress: {remaining}/{st.session_state['original_count']}")

# Display message if no more verbs are left to review
if not st.session_state['current_verb']:
    st.write("No more verbs to review!")
