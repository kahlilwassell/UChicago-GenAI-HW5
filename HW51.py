from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re
import streamlit as st

# load environment variables from a .env file
load_dotenv()

# standard hangman settings
MAX_WRONG_GUESSES = 6

# set up the streamlit app page configuration
st.set_page_config(page_title="AI Hangman (HW 5.1)", layout="centered")
# set the title and caption of the app
st.title("AI Hangman (HW 5.1)")
st.caption("The LLM selects a word and you guess letters to find it! Try to guess before you run out of wrong guesses.")


def llm_select_word():
    """Use an LLM to select a random word for the hangman game."""
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that selects a random English word."),
        ("user", "Please provide a single random English word between 5 and 12 letters long.")
    ])
    response = model.invoke(prompt.format_messages())
    word = re.search(r'\b[a-zA-Z]{5,12}\b', getattr(response, "content", str(response)))
    return word.group(0).lower() if word else "hangman"


def display_game_state(word, guessed_letters):
    """Display the current state of the game."""
    displayed_word = ' '.join([letter if letter in guessed_letters else '_' for letter in word])
    st.write(f"Word: {displayed_word}")
    st.write(f"Guessed Letters: {' '.join(sorted(guessed_letters))}")
    st.write(f"Wrong Guesses Left: {MAX_WRONG_GUESSES - len([l for l in guessed_letters if l not in word])}")


# Form for the user to input their guesses
with st.form(key='hangman_form'):
    st.write("Try to guess the word by entering one letter at a time!")
    guess = st.text_input("Enter your letter guess (a-z):", max_chars=1).lower()
    submit_button = st.form_submit_button(label='Submit Guess')
    # Initialize session state (game) variables
    if 'word' not in st.session_state:
        st.session_state.word = llm_select_word()
        st.session_state.guessed_letters = set()
        st.session_state.wrong_guesses = 0

    # Check for win/loss conditions
    if all(letter in st.session_state.guessed_letters for letter in st.session_state.word):
        st.success(f"Congratulations! You've guessed the word: {st.session_state.word}")
        st.session_state.word = llm_select_word()
        st.session_state.guessed_letters = set()
        st.session_state.wrong_guesses = 0
    elif st.session_state.wrong_guesses >= MAX_WRONG_GUESSES:
        st.error(f"Game Over! The word was: {st.session_state.word}")
        st.session_state.word = llm_select_word()
        st.session_state.guessed_letters = set()
        st.session_state.wrong_guesses = 0

    # Process the guess
    if submit_button and guess.isalpha() and len(guess) == 1:
        if guess not in st.session_state.guessed_letters:
            st.session_state.guessed_letters.add(guess)
            if guess not in st.session_state.word:
                st.session_state.wrong_guesses += 1

    # Check for win/loss conditions
    if all(letter in st.session_state.guessed_letters for letter in st.session_state.word):
        st.success(f"Congratulations! You've guessed the word: {st.session_state.word}")
        st.session_state.word = llm_select_word()
        st.session_state.guessed_letters = set()
        st.session_state.wrong_guesses = 0
    elif st.session_state.wrong_guesses >= MAX_WRONG_GUESSES:
        st.error(f"Game Over! The word was: {st.session_state.word}")
        st.session_state.word = llm_select_word()
        st.session_state.guessed_letters = set()
        st.session_state.wrong_guesses = 0
    # Display the current game state
    display_game_state(st.session_state.word, st.session_state.guessed_letters)    