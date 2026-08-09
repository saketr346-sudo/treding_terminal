import random
import string
import streamlit as st


def generate_captcha():
  return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def generate_otp():
  return "".join(random.choices(string.digits, k=6))


@st.dialog("🔑 Reset Password")
def forgot_password_dialog():
  st.markdown(
      "<div style='text-align: center;'>अपने रजिस्टर मोबाइल या ईमेल पर OTP प्राप्त"
      " करें।</div>",
      unsafe_allow_html=True,
  )
  reset_input = st.text_input("Enter Email or Mobile", key="reset_user_input")

  if "reset_otp" not in st.session_state:
    st.session_state.reset_otp = None

  col_a, col_b = st.columns([1, 1])
  with col_a:
    if st.button("Send Reset OTP", key="btn_send_reset_otp"):
      if reset_input:
        st.session_state.reset_otp = generate_otp()
        st.success(f"OTP Sent! Demo OTP: {st.session_state.reset_otp}")
      else:
        st.warning("Please enter Email or Mobile.")

  with col_b:
    entered_reset_otp = st.text_input(
        "Enter OTP", key="reset_otp_input", label_visibility="collapsed"
    )

  new_pwd = st.text_input("New Password", type="password", key="reset_new_pwd")

  if st.button(
      "Update Password", type="primary", use_container_width=True, key="btn_update_pwd"
  ):
    if (
        st.session_state.reset_otp
        and entered_reset_otp == st.session_state.reset_otp
    ):
      if new_pwd:
        st.success("Password Updated Successfully!")
        st.session_state.reset_otp = None
        st.rerun()
      else:
        st.warning("Please enter a new password.")
    else:
      st.error("Invalid OTP!")


def render_login_page():
  if "captcha_code" not in st.session_state:
    st.session_state.captcha_code = generate_captcha()

  if "sent_otp" not in st.session_state:
    st.session_state.sent_otp = None

  st.markdown(
      """
        <style>
        /* Hide Top Headers & Footers */
        header, footer, [data-testid="stHeader"] {
            display: none !important;
        }

        /* Clean Light Background */
        html, body, .stApp {
            overflow: hidden !important;
            height: 100vh !important;
            background-color: #F9F9F7 !important;
        }

        /* Left Yellow Accent Bar */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 8px;
            height: 100vh;
            background-color: #FFE01B;
            z-index: 9999;
        }

        /* Continuous Stock Ticker Columns */
        .stock-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            opacity: 0.18;
            font-family: 'Consolas', 'Courier New', monospace;
            font-weight: 700;
            font-size: 14px;
            display: flex;
            justify-content: space-around;
            pointer-events: none;
            user-select: none;
        }

        .stock-col {
            display: flex;
            flex-direction: column;
            gap: 28px;
            animation: moveStock 16s linear infinite;
        }

        .stock-col:nth-child(even) {
            animation-direction: reverse;
        }

        @keyframes moveStock {
            0% { transform: translateY(0); }
            100% { transform: translateY(-50%); }
        }

        .up { color: #007C89; }
        .down { color: #D14343; }

        /* Main Container */
        [data-testid="stMainBlockContainer"] {
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            z-index: 10 !important;
            width: 100% !important;
            max-width: 720px !important;
            padding: 0 !important;
        }

        /* Minimalist Card Container */
        [data-testid="stVerticalBlockBorderWrapper"], 
        div[data-testid="stVerticalBlock"] {
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #E6E6E4 !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
            padding: 0px !important;
            overflow: hidden !important;
            gap: 0.1rem !important;
        }

        /* Header - Strictly Centered */
        .custom-card-header {
            background-color: #E7F6F7 !important;
            padding: 6px 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            border-bottom: 1px solid #D2EBEB;
            width: 100%;
        }

        .custom-card-header-title {
            font-size: 17px;
            font-weight: 800;
            color: #242424 !important;
            margin: 0;
            text-align: center !important;
        }

        /* Card Content Body */
        .card-content-body {
            background-color: #FFFFFF !important;
            padding: 6px 20px;
            text-align: center !important;
        }

        /* ==================== CENTER ALIGNMENT FIXES ==================== */

        /* 1. Force Text Align Center Globally */
        *, .stMarkdown, p, span, div, h1, h2, h3, h4, h5, h6 {
            text-align: center !important;
        }

        /* 2. Center Tabs (Sign In / Register) */
        div[data-baseweb="tab-highlight-title"],
        div[data-baseweb="tab-list"],
        div[data-testid="stTabs"] {
            justify-content: center !important;
            display: flex !important;
            width: 100% !important;
        }

        button[data-baseweb="tab"] {
            color: #6B6B6B !important;
            background-color: transparent !important;
            padding: 6px 20px !important;
            justify-content: center !important;
            text-align: center !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #007C89 !important;
            font-weight: 800 !important;
            border-bottom-color: #007C89 !important;
        }

        /* 3. Center Radio Buttons (Email & Password / Mobile & OTP) */
        div[role="radiogroup"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin-bottom: 4px !important;
        }

        div[role="radiogroup"] label {
            justify-content: center !important;
            display: flex !important;
            align-items: center !important;
        }

        /* 4. Center Input Field Labels (Mobile Number, OTP, etc.) */
        div[data-testid="stWidgetLabel"],
        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            text-align: center !important;
            font-weight: 600 !important;
            color: #242424 !important;
            margin-bottom: 2px !important;
        }

        /* 5. Input Text Center Align */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            border: 1px solid #BDBDBD !important;
            border-radius: 4px !important;
            height: 28px !important;
            min-height: 28px !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #007C89 !important;
        }
        div[data-baseweb="input"] input {
            color: #242424 !important;
            text-align: center !important;
            padding: 0px 8px !important;
            height: 28px !important;
        }
        div[data-baseweb="input"] input::placeholder {
            text-align: center !important;
        }

        /* SelectBox Text Alignment */
        div[data-baseweb="select"] > div {
            padding: 0px 8px !important;
            min-height: 28px !important;
            height: 28px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Element Spacing */
        div[data-testid="stElementContainer"] {
            margin-bottom: 1px !important;
        }

        /* Primary Button Style */
        .stButton > button[kind="primary"] {
            background-color: #007C89 !important;
            background-image: none !important;
            border: none !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            height: 30px !important;
            border-radius: 4px !important;
            margin-top: 2px !important;
            text-align: center !important;
            transition: background-color 0.2s ease;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #005F69 !important;
        }

        /* Forgot Password Right Corner Wrapper */
        .forgot-pwd-wrapper {
            display: flex;
            justify-content: flex-end;
            width: 100%;
            margin-top: 2px;
        }

        .forgot-pwd-wrapper .stButton > button {
            text-align: right !important;
            padding: 0 !important;
            height: auto !important;
            font-size: 12px !important;
            color: #007C89 !important;
            text-decoration: underline;
            border: none !important;
            background: transparent !important;
        }

        /* Captcha Box Centered */
        .captcha-box-ui {
            background-color: #FFFBE6;
            color: #242424 !important;
            font-size: 15px;
            font-weight: 800;
            letter-spacing: 4px;
            text-align: center !important;
            border-radius: 4px;
            height: 28px;
            line-height: 28px;
            border: 1px solid #FFE01B;
            user-select: none;
        }

        /* Google Sign In Button */
        .google-btn-class > button {
            background-color: #FFFFFF !important;
            color: #242424 !important;
            font-weight: 600 !important;
            border: 1px solid #BDBDBD !important;
            height: 28px !important;
            border-radius: 4px !important;
            text-align: center !important;
        }

        /* Divider Line */
        .or-divider {
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #757575 !important;
            margin: 2px 0;
            font-size: 11px;
        }
        .or-divider::before, .or-divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #E0E0E0;
        }
        .or-divider:not(:empty)::before {
            margin-right: .5em;
        }
        .or-divider:not(:empty)::after {
            margin-left: .5em;
        }
        </style>

        <!-- Continuous Stock Numbers Overlay -->
        <div class="stock-bg">
            <div class="stock-col">
                <span class="up">NIFTY 24,320 ▲1.2%</span>
                <span class="down">SENSEX 79,800 ▼0.4%</span>
                <span class="up">AAPL $224.30 ▲2.1%</span>
                <span class="up">RELIANCE 3,120 ▲0.8%</span>
                <span class="down">TSLA $210.15 ▼1.5%</span>
                <span class="up">NVDA $128.50 ▲3.4%</span>
            </div>
            <div class="stock-col">
                <span class="down">HDFCBANK 1,610 ▼0.3%</span>
                <span class="up">INFY 1,820 ▲1.5%</span>
                <span class="up">AMZN $186.40 ▲0.9%</span>
                <span class="down">GOOGL $165.20 ▼0.7%</span>
                <span class="up">TCS 4,250 ▲1.1%</span>
                <span class="up">TATAMOTORS 1,020 ▲2.0%</span>
            </div>
            <div class="stock-col">
                <span class="up">BANKNIFTY 52,100 ▲0.9%</span>
                <span class="down">BTC/USD $61,200 ▼2.1%</span>
                <span class="up">ETH/USD $3,380 ▲1.8%</span>
                <span class="up">ICICIBANK 1,230 ▲1.4%</span>
                <span class="down">GOLD 72,400 ▼0.1%</span>
                <span class="up">SUNPHARMA 1,750 ▲0.5%</span>
            </div>
            <div class="stock-col">
                <span class="up">WIPRO 540 ▲1.8%</span>
                <span class="down">SBIN 840 ▼0.6%</span>
                <span class="up">MSFT $448.90 ▲1.2%</span>
                <span class="up">META $512.30 ▲2.5%</span>
                <span class="down">AXISBANK 1,180 ▼0.9%</span>
                <span class="up">LT 3,650 ▲0.7%</span>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  with st.container(border=True):
    st.markdown(
        """
        <div class="custom-card-header">
            <span>⚙️</span>
            <span class="custom-card-header-title">User Login</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-content-body">', unsafe_allow_html=True)

    tab_signin, tab_register = st.tabs(["🔒 Sign In", "📝 Register"])

    with tab_signin:
      login_method = st.radio(
          "Login Method",
          ["Email & Password", "Mobile & OTP"],
          horizontal=True,
          label_visibility="collapsed",
      )

      if login_method == "Email & Password":
        email = st.text_input(
            "Email / User ID",
            placeholder="Enter Email or User ID",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter Password",
            key="login_pass",
        )

      else:
        mobile = st.text_input(
            "Mobile Number", placeholder="+91 XXXXX XXXXX", key="login_mobile"
        )
        otp_col1, otp_col2 = st.columns([2.5, 1])

        with otp_col1:
          user_otp = st.text_input(
              "OTP", placeholder="Enter 6-digit OTP", key="login_otp"
          )
        with otp_col2:
          if st.button("Send OTP", key="btn_send_otp"):
            if mobile:
              st.session_state.sent_otp = generate_otp()
              st.toast(
                  f"OTP Sent! Demo OTP: {st.session_state.sent_otp}", icon="📩"
              )
            else:
              st.warning("Please enter Mobile Number.")

      cap_c1, cap_c2, cap_c3 = st.columns([2.2, 0.8, 2.5])
      with cap_c1:
        st.markdown(
            f'<div class="captcha-box-ui">{st.session_state.captcha_code}</div>',
            unsafe_allow_html=True,
        )
      with cap_c2:
        if st.button("↻", key="cap_ref"):
          st.session_state.captcha_code = generate_captcha()
          st.rerun()
      with cap_c3:
        user_captcha = st.text_input(
            "Captcha",
            placeholder="Enter Captcha",
            label_visibility="collapsed",
            key="cap_input",
        )

      if st.button(
          "CLICK TO LOGIN",
          use_container_width=True,
          type="primary",
          key="btn_login",
      ):
        if user_captcha.strip().upper() != st.session_state.captcha_code.upper():
          st.error("Invalid Captcha!")
          st.session_state.captcha_code = generate_captcha()
        else:
          if login_method == "Email & Password":
            if not email or not password:
              st.warning("Please enter Email and Password.")
            else:
              st.session_state.logged_in = True
              st.toast("Login Successful!", icon="🚀")
              st.rerun()
          else:
            if not mobile or not user_otp:
              st.warning("Please enter Mobile Number and OTP.")
            elif (
                st.session_state.sent_otp
                and user_otp == st.session_state.sent_otp
            ):
              st.session_state.logged_in = True
              st.toast("Login Successful!", icon="🚀")
              st.rerun()
            else:
              st.error("Invalid OTP!")

      # Forgot Password (Right Corner)
      if login_method == "Email & Password":
        st.markdown(
            '<div class="forgot-pwd-wrapper">', unsafe_allow_html=True
        )
        if st.button("Forgot Password?", key="btn_forgot_pwd"):
          forgot_password_dialog()
        st.markdown("</div>", unsafe_allow_html=True)

      st.markdown(
          '<div class="or-divider">OR</div>', unsafe_allow_html=True
      )
      st.markdown('<div class="google-btn-class">', unsafe_allow_html=True)
      if st.button(
          "🌐 Sign in with Google", use_container_width=True, key="btn_google"
      ):
        st.session_state.logged_in = True
        st.toast("Google Sign-In Successful!", icon="🚀")
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)

    with tab_register:
      reg_name = st.text_input(
          "Name", placeholder="Enter Full Name", key="reg_name"
      )
      reg_pass = st.text_input(
          "New Password",
          type="password",
          placeholder="Create Password",
          key="reg_pass",
      )

      countries = [
          "India",
          "United States",
          "United Kingdom",
          "Canada",
          "Australia",
          "United Arab Emirates",
          "Germany",
          "Singapore",
      ]
      reg_country = st.selectbox(
          "Country", countries, index=0, key="reg_country"
      )

      if st.button(
          "Register Account",
          use_container_width=True,
          type="primary",
          key="btn_reg",
      ):
        if not reg_name or not reg_pass:
          st.warning("Please fill all required fields.")
        else:
          st.success("Account created successfully! Please Sign In.")

    st.markdown("</div>", unsafe_allow_html=True)