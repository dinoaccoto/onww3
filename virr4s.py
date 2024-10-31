import streamlit as st
import random
import re

# Load verbs from file
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
            "Translation": columns[5]
        })

# Shuffle verbs before splitting into batches
random.shuffle(verbs)

# Set batch size
batch_size = 20  # or set this to any other value, e.g., 20

# Split shuffled verbs into batches using batch_size
batches = [verbs[i:i + batch_size] for i in range(0, len(verbs), batch_size)]
batch_count = len(batches)

# Initialize session state for batch management
if 'current_batch_index' not in st.session_state:
    st.session_state['current_batch_index'] = 0
if 'mistaken_cards' not in st.session_state:
    st.session_state['mistaken_cards'] = []
if 'incorrect_count' not in st.session_state:
    st.session_state['incorrect_count'] = 0
if 'cards_to_review' not in st.session_state:
    st.session_state['cards_to_review'] = list(batches[st.session_state['current_batch_index']])
if 'original_count' not in st.session_state:
    st.session_state['original_count'] = len(st.session_state['cards_to_review'])
if 'current_verb' not in st.session_state:
    st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review']) if st.session_state['cards_to_review'] else None
if 'show_answer' not in st.session_state:
    st.session_state['show_answer'] = False

# Helper function to pick a new card only when needed
def pick_new_card():
    if st.session_state['cards_to_review']:
        st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review'])
        st.session_state['cards_to_review'].remove(st.session_state['current_verb'])
    else:
        if not st.session_state['mistaken_cards'] and st.session_state['current_batch_index'] < batch_count - 1:
            st.session_state['current_batch_index'] += 1
            st.session_state['cards_to_review'] = list(batches[st.session_state['current_batch_index']])
            st.session_state['original_count'] = len(st.session_state['cards_to_review'])
            st.session_state['incorrect_count'] = 0
            st.session_state['mistaken_cards'] = []
            st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review'])
            st.session_state['cards_to_review'].remove(st.session_state['current_verb'])
        elif st.session_state['mistaken_cards']:
            st.session_state['cards_to_review'] = st.session_state['mistaken_cards'][:]
            st.session_state['mistaken_cards'] = []
            st.session_state['incorrect_count'] = 0
            st.session_state['original_count'] = len(st.session_state['cards_to_review'])
            st.session_state['current_verb'] = random.choice(st.session_state['cards_to_review'])
            st.session_state['cards_to_review'].remove(st.session_state['current_verb'])
        else:
            st.session_state['current_verb'] = None

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
# st.markdown("<h4>Onregelmatige werkwoorden (Niveau 3) Flashcards</h4>", unsafe_allow_html=True)

# Display progress bars
if st.session_state['original_count'] > 0:
    correct_progress = (st.session_state['original_count'] - len(st.session_state['cards_to_review']) - st.session_state['incorrect_count']) / st.session_state['original_count']
    incorrect_progress = st.session_state['incorrect_count'] / st.session_state['original_count']
    
    st.progress(correct_progress)
    st.markdown(
        f"""
        <div style="position: relative; background-color: #e0e0e0; border-radius: 4px; height: 8px; margin-top: 10px; overflow: hidden;">
        <div style="background-color: red; width: {incorrect_progress * 100}%; height: 8px; border-radius: 4px; position: absolute; right: 0;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display current verb and translation
if st.session_state['current_verb']:
    st.markdown(f"**<span style='font-size:1.5em;'>{st.session_state['current_verb']['Infinitief']}</span>**", unsafe_allow_html=True)
    if st.session_state['current_verb']["Translation"]:
        st.write(f"({st.session_state['current_verb']['Translation']})")
    
    if st.session_state['show_answer']:
        # Display normal face for Imperfectum and Participium labels and bold for details
        st.markdown(f"Imperfectum: **{st.session_state['current_verb']['Imperfectum sing']}**, **{st.session_state['current_verb']['Imperfectum plur']}**")
        st.markdown(f"Participium: **{st.session_state['current_verb']['Participium']}** ({st.session_state['current_verb']['h/z']})")
        
        # Display buttons with equal width in two columns with minimal spacing
        col1, col2 = st.columns([1, 1])

        with col1:
            st.button("Ja", on_click=mark_as_known)
        
        with col2:
            st.button("Neen", on_click=mark_as_unknown)
    else:
        st.button("Toon", on_click=show_answer)

# Display remaining count and batch
remaining = st.session_state['original_count'] - len(st.session_state['cards_to_review'])
st.write(f"Progress: {remaining}/{st.session_state['original_count']} in Batch {st.session_state['current_batch_index'] + 1}/{batch_count}")

# Display message if no more verbs are left to review
if not st.session_state['current_verb']:
    st.write("No more verbs to review")
