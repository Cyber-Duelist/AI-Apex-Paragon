"""
ComplianceAI - Authentication Module
Provides password hashing, user registration/login, and a Streamlit auth UI.
"""

import bcrypt
import streamlit as st

import database


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt and return the hashed string."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# Registration & login logic
# ---------------------------------------------------------------------------

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new user.

    Returns
    -------
    tuple[bool, str]
        (success, message)
    """
    existing = database.get_user(username)
    if existing is not None:
        return False, "Username already exists. Please choose a different one."

    password_hash = hash_password(password)
    database.create_user(username, email, password_hash)
    return True, "Registration successful! You can now log in."


def login_user(username: str, password: str) -> tuple[bool, dict | None]:
    """Authenticate a user.

    Returns
    -------
    tuple[bool, dict | None]
        (success, user_dict or None)
    """
    user = database.get_user(username)
    if user is None:
        return False, None

    if verify_password(password, user["password_hash"]):
        return True, user

    return False, None


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def check_auth() -> bool:
    """Return True if the current session is authenticated."""
    return st.session_state.get("authenticated", False)


def logout():
    """Clear authentication state and rerun the app."""
    for key in ["authenticated", "user", "user_id", "username"]:
        st.session_state.pop(key, None)
    st.rerun()


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

def render_auth_page() -> None:
    """Render a Streamlit login / register page with two tabs."""
    st.set_page_config(page_title="ComplianceAI – Login", page_icon="🔒", layout="centered")

    st.markdown(
        """
        <style>
        .auth-title {
            text-align: center;
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .auth-sub {
            text-align: center;
            color: #888;
            margin-bottom: 2rem;
        }
        </style>
        <div class="auth-title">🔒 ComplianceAI</div>
        <div class="auth-sub">AI-Powered Compliance Analysis Platform</div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    # ── Login tab ──────────────────────────────────────────────────────────
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                success, user = login_user(username, password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.session_state["user_id"] = user["id"]
                    st.session_state["username"] = user["username"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    # ── Register tab ───────────────────────────────────────────────────────
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = register_user(new_username, new_email, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
