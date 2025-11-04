# HW51.py — Streamlit Hangman (LLM chooses the word)

import re
import string
from typing import List, Set
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Config
MAX_LIVES = 6
MODEL_NAME = "gpt-4o-mini"
WORD_REGEX = re.compile(r"^[a-z]{4,10}$")


# LLM Helpers
@st.cache_resource(show_spinner=False)
def get_model() -> ChatOpenAI:
    """Cache the OpenAI chat model once per session."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0.8)


def pick_secret_word_via_llm(model: ChatOpenAI, max_retries: int = 3) -> str:
    """
    Ask the LLM to choose a Hangman word. 
    - single word
    - lowercase a–z
    - 4–10 letters
    Retries a few times if needed.
    """
    system = (
        "You are selecting a secret word for a Hangman game.\n"
        "Return ONLY a single lowercase English word a–z, 4–10 letters, no spaces, no punctuation."
    )
    user = (
        "Choose a secret word for hangman now. "
        "Return only the word with no explanation, no quotes, and no punctuation."
    )

    for _ in range(max_retries):
        try:
            resp = model.invoke([{"role": "system", "content": system},
                                 {"role": "user", "content": user}])
            word = (resp.content or "").strip()
            # If model returns extra text, grab the first token-like match
            m = WORD_REGEX.search(word)
            if m:
                return m.group(0)
        except Exception as e:
            # Surface error but keep retrying
            st.info(f"Retrying word selection… ({type(e).__name__})")
    raise RuntimeError("Failed to obtain a valid secret word from the LLM. Please try again.")


# Game State
def new_game() -> None:
    """Start a fresh game using the LLM to get the secret word."""
    model = get_model()
    secret = pick_secret_word_via_llm(model)
    st.session_state.secret: str = secret
    st.session_state.lives: int = MAX_LIVES
    st.session_state.correct: Set[str] = set()
    st.session_state.wrong: Set[str] = set()
    st.session_state.revealed: List[str] = ["_" for _ in secret]
    st.session_state.game_over: bool = False
    st.session_state.won: bool = False
    st.session_state.history: List[str] = [f"New game started. Secret word is {len(secret)} letters long."]


def ensure_game_initialized() -> None:
    if "secret" not in st.session_state:
        new_game()


def apply_guess(ch: str) -> None:
    """Apply a single-letter guess to the game state."""
    if st.session_state.game_over:
        return

    ch = ch.lower().strip()
    if len(ch) != 1 or ch not in string.ascii_lowercase:
        st.warning("Please enter a single letter (A–Z).")
        return
    if ch in st.session_state.correct or ch in st.session_state.wrong:
        st.info(f"You already tried '{ch.upper()}'.")
        return

    secret = st.session_state.secret
    if ch in secret:
        st.session_state.correct.add(ch)
        for i, c in enumerate(secret):
            if c == ch:
                st.session_state.revealed[i] = c.upper()
        st.session_state.history.append(f"Correct: {ch.upper()}")
    else:
        st.session_state.wrong.add(ch)
        st.session_state.lives -= 1
        st.session_state.history.append(f"Wrong: {ch.upper()}")

    # Win/Lose check
    if "_" not in st.session_state.revealed:
        st.session_state.game_over = True
        st.session_state.won = True
        st.session_state.history.append("You solved the word!")
    elif st.session_state.lives <= 0:
        st.session_state.game_over = True
        st.session_state.won = False
        st.session_state.history.append(f"Out of lives. The word was {secret.upper()}.")


# UI Rendering
def render_header() -> None:
    st.set_page_config(page_title="HW 51: Hangman", layout="centered")
    st.title("HW 51 — LLM Hangman")
    st.caption("LLM chooses the word. You guess the letters.")


def render_status() -> None:
    # Word + Lives row
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        spaced = " ".join(st.session_state.revealed)
        st.markdown(f"### Word: `{spaced}`")
    with c2:
        lives = st.session_state.lives
        bar_full = "|" * lives
        bar_empty = "" * (MAX_LIVES - lives)
        st.markdown("### Lives")
        st.write(f"{bar_full}{bar_empty}  ({lives}/{MAX_LIVES})")

    # Wrong guesses
    if st.session_state.wrong:
        chips = "  ".join(f"`{c.upper()}`" for c in sorted(st.session_state.wrong))
        st.markdown(f"**Wrong guesses:** {chips}")


def render_controls() -> None:
    disabled = st.session_state.game_over

    # Clear the input automatically when the form submits
    with st.form("guess_form", clear_on_submit=True):
        guess = st.text_input(
            "Guess a letter",
            key="guess_input",
            max_chars=1,
            placeholder="Enter a letter (A-Z)",
            disabled=disabled,
        )
        submitted = st.form_submit_button("Guess", disabled=disabled)

    if submitted and not disabled:
        if guess:
            apply_guess(guess)
            st.rerun()
        else:
            st.warning("Type a single letter before submitting.")

    # Secondary actions
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("New game"):
            new_game()
            st.rerun()
    with c2:
        with st.expander("Reveal word (for testing)"):
            st.code(st.session_state.secret.upper())


def render_footer() -> None:
    # Game log/history
    with st.expander("Game log"):
        if st.session_state.history:
            for line in st.session_state.history[::-1]:
                st.write(line)
        else:
            st.write("No moves yet.")

    # End status
    if st.session_state.game_over:
        if st.session_state.won:
            st.success("You won! Great job!")
        else:
            st.error(f"You lost. The word was {st.session_state.secret.upper()}.")

    st.caption("Tip: Press Enter after typing a letter to submit quickly.")


# App
def main() -> None:
    render_header()
    ensure_game_initialized()
    render_status()
    st.divider()
    render_controls()
    st.divider()
    render_footer()


if __name__ == "__main__":
    main()
