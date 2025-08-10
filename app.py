from __future__ import annotations
import os
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from src.i18n import Translator, SUPPORTED_LANGUAGES
from src import data as data_utils
from src import ml as ml_utils
from src import ui_components as ui
from src import maps as maps_utils
from src import reports as reports_utils
from src.auth import verify_password, find_user, register_user
from src.config import get_ors_api_key, get_openweather_api_key
from src.services import get_route_openrouteservice, get_weather_openweather

st.set_page_config(page_title="SurakshitPath", page_icon="🛡️", layout="wide")

# Global styles
st.markdown(
    """
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .kpi-card { background: #0F172A; border-radius: 14px; padding: 16px 18px; border: 1px solid #1F2937; }
    .kpi-title { color: #9CA3AF; font-size: 0.9rem; }
    .kpi-value { color: #F9FAFB; font-size: 1.6rem; font-weight: 700; margin-top: 6px; }
    .login-card { background: #0F172A; border: 1px solid #1F2937; border-radius: 16px; padding: 28px; max-width: 480px; margin: auto; }
    .app-title { font-weight: 800; font-size: 1.2rem; color: #E5E7EB; text-align: center; margin-bottom: 10px; }
    .brand { text-align:center; font-size: 1.8rem; margin-bottom: 18px; }
    .footer-note { color: #9CA3AF; font-size: 0.8rem; text-align: center; margin-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session init
if "lang" not in st.session_state:
    st.session_state.lang = "en"
translator = Translator(st.session_state.lang)

def t(key: str, default: str | None = None) -> str:
    return translator.t(key, default)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "df" not in st.session_state:
    st.session_state.df = None
if "model" not in st.session_state:
    st.session_state.model = None

# Sidebar controls (available post-login)

def sidebar_controls():
    with st.sidebar:
        st.subheader(t("sidebar.title"))
        # Language switcher
        lang = st.selectbox(t("lang.select"), options=list(SUPPORTED_LANGUAGES.keys()), format_func=lambda x: SUPPORTED_LANGUAGES[x], index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.lang))
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            translator.set_lang(lang)
            st.rerun()

        # Upload
        st.markdown("---")
        st.caption(t("sidebar.upload"))
        uploaded = st.file_uploader("CSV", type=["csv"], label_visibility="collapsed")
        if uploaded is not None:
            st.session_state.df = data_utils.load_dataset(uploaded.getvalue())
        else:
            if st.session_state.df is None:
                st.session_state.df = data_utils.load_dataset(None)

        df = st.session_state.df

        # Filters
        st.markdown("---")
        st.caption(t("sidebar.filters"))
        states = st.multiselect(t("sidebar.state"), sorted(df["state"].dropna().unique().tolist()))
        products = st.multiselect(t("sidebar.product"), sorted(df["product"].dropna().unique().tolist()))
        risks = st.multiselect(t("sidebar.risk"), ["Low", "Medium", "High"])

        # Toggles
        st.markdown("---")
        st.caption(t("sidebar.toggles"))
        show_weather = st.toggle(t("sidebar.toggle.weather"), value=True)
        show_zones = st.toggle(t("sidebar.toggle.riskzones"), value=True)

        # About
        st.markdown("---")
        st.caption(t("sidebar.about"))
        st.info(t("about.text"))

        # Logout
        st.markdown("---")
        if st.button(t("sidebar.logout")):
            st.session_state.logged_in = False
            st.rerun()

        return states, products, risks, show_weather, show_zones


# Login page

def login_view():
    st.write("")
    col = st.container()
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown(f"<div class='brand'>🛡️</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='app-title'>{t('app.name')}</div>")
        st.markdown("<br>", unsafe_allow_html=True)
        # Language selector on login
        lang_login = st.selectbox(t("lang.select"), options=list(SUPPORTED_LANGUAGES.keys()), format_func=lambda x: SUPPORTED_LANGUAGES[x], index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.lang))
        if lang_login != st.session_state.lang:
            st.session_state.lang = lang_login
            translator.set_lang(lang_login)
            st.rerun()
        email = st.text_input(t("login.email"), key="login_email")
        password = st.text_input(t("login.password"), type="password", key="login_password")
        c1, c2, c3 = st.columns([1, 0.2, 1])
        with c1:
            if st.button(t("login.button")):
                user = find_user(email)
                if user and verify_password(password, user.password_hash):
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
                else:
                    st.error(t("login.error"))
        with c2:
            st.write(t("login.or"))
        with c3:
            if st.button(t("login.demo")):
                st.session_state.logged_in = True
                st.session_state.email = "demo@surakshitpath.ai"
                st.rerun()

        with st.expander(t("login.signup")):
            n_email = st.text_input(t("login.email"), key="signup_email")
            n_pass = st.text_input(t("login.password"), type="password", key="signup_password")
            if st.button(t("login.signup"), key="signup_btn"):
                if n_email and n_pass and register_user(n_email, n_pass):
                    st.success("Registered! You can log in now.")
                else:
                    st.warning("User exists or invalid input.")
        st.markdown('<div class="footer-note">Predict · Prevent · Prosper</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Tabs content

def tab_overview(df: pd.DataFrame):
    total, avg_risk, high_risk, avg_delay = data_utils.compute_kpis(df)
    c1, c2, c3, c4 = st.columns(4)
    ui.kpi_card(t("kpi.total_vendors"), f"{total}", c1)
    ui.kpi_card(t("kpi.avg_risk"), f"{avg_risk:.1f}", c2)
    ui.kpi_card(t("kpi.high_risk"), f"{high_risk}", c3)
    ui.kpi_card(t("kpi.avg_delay"), f"{avg_delay:.1f}%", c4)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        ui.risk_distribution_chart(df, t("charts.risk_distribution"))
    with col2:
        ui.products_by_risk_pie(df, t("charts.products_by_risk"))

    st.markdown("---")
    st.subheader(t("table.vendors"))
    st.dataframe(data_utils.style_risk_table(df), use_container_width=True)


def tab_prediction(df: pd.DataFrame, show_weather: bool):
    st.subheader(t("prediction.controls"))
    c1, c2, c3 = st.columns(3)
    with c1:
        distance = st.slider(t("prediction.distance"), min_value=0, max_value=2000, value=500, step=10)
    with c2:
        past_delays = st.slider(t("prediction.past_delays"), min_value=0, max_value=20, value=3, step=1)
    with c3:
        if show_weather:
            weather = st.slider(t("prediction.weather"), min_value=0, max_value=100, value=50, step=1)
        else:
            st.caption(t("prediction.weather") + ": hidden")
            weather = 50

    # Train model lazily
    if st.session_state.model is None:
        with st.spinner("Training model..."):
            result = ml_utils.train_model(df)
            st.session_state.model = result.model
            st.info(f"R2: {result.r2:.2f}, MAE: {result.mae:.2f}")

    pred = ml_utils.predict_delay(st.session_state.model, distance, past_delays, weather)
    st.success(f"Predicted Delay: {pred:.1f}%")

    pred_df = ml_utils.add_predictions(df, st.session_state.model).sort_values("predicted_delay_pct", ascending=False)
    st.markdown("---")
    st.subheader(t("prediction.results"))
    st.dataframe(pred_df[["vendor_id","vendor_name","state","product","risk_level","avg_delay_pct","predicted_delay_pct"]], use_container_width=True)

    st.markdown("---")
    st.subheader(t("prediction.top_risky"))
    top = pred_df.head(10).sort_values("predicted_delay_pct", ascending=False)
    import altair as alt
    chart = alt.Chart(top).mark_bar().encode(
        x=alt.X("predicted_delay_pct:Q", title=t("kpi.avg_delay")),
        y=alt.Y("vendor_name:N", sort='-x', title="Vendor"),
        tooltip=["vendor_name", alt.Tooltip("predicted_delay_pct:Q", format=".1f")]
    ).properties(height=360)
    st.altair_chart(chart, use_container_width=True)


def tab_routing(df: pd.DataFrame, show_zones: bool, show_weather: bool):
    col1, col2 = st.columns(2)
    with col1:
        src_lat = st.number_input(t("routing.source")+" Lat", value=float(df["lat"].iloc[0]))
        src_lon = st.number_input(t("routing.source")+" Lon", value=float(df["lon"].iloc[0]))
    with col2:
        dst_lat = st.number_input(t("routing.destination")+" Lat", value=float(df["lat"].iloc[-1]))
        dst_lon = st.number_input(t("routing.destination")+" Lon", value=float(df["lon"].iloc[-1]))

    if st.button(t("routing.plot")):
        route_coords = None
        distance_km = None
        duration_min = None
        ors_key = get_ors_api_key()
        if ors_key:
            try:
                rd = get_route_openrouteservice((src_lat, src_lon), (dst_lat, dst_lon), ors_key)
                route_coords = rd["coords"]
                distance_km = rd["distance_km"]
                duration_min = rd["duration_min"]
            except Exception as e:
                st.warning(f"Routing API error: {e}. Falling back to straight line.")
        else:
            st.info("Set ORS_API_KEY in .env to enable real routing.")

        weather_data = {}
        if show_weather:
            owm_key = get_openweather_api_key()
            if owm_key:
                try:
                    weather_data["source"] = get_weather_openweather(src_lat, src_lon, owm_key)
                    weather_data["dest"] = get_weather_openweather(dst_lat, dst_lon, owm_key)
                except Exception as e:
                    st.warning(f"Weather API error: {e}")
            else:
                st.info("Set OPENWEATHER_API_KEY in .env to show weather.")

        def popup(row):
            risk = str(row.get("risk_level", "Medium"))
            return f"<b>{row.get('vendor_name')}</b><br/>Risk: {risk}<br/>Delay: {row.get('avg_delay_pct',0):.1f}%"
        fmap = maps_utils.create_map(df, popup, show_zones, (src_lat, src_lon), (dst_lat, dst_lon), route_coords=route_coords, weather=weather_data if weather_data else None)

        # Show route metrics if available
        if distance_km is not None and duration_min is not None:
            m1, m2 = st.columns(2)
            m1.metric("Distance (km)", f"{distance_km:.1f}")
            m2.metric("ETA (min)", f"{duration_min:.0f}")
        st_folium(fmap, width=1200, height=600)


def tab_reports(df: pd.DataFrame):
    total, avg_risk, high_risk, avg_delay = data_utils.compute_kpis(df)
    st.subheader(t("reports.summary"))
    c1, c2, c3 = st.columns(3)
    ui.kpi_card(t("kpi.total_vendors"), f"{total}", c1)
    ui.kpi_card(t("kpi.avg_delay"), f"{avg_delay:.1f}%", c2)
    ui.kpi_card(t("kpi.high_risk"), f"{high_risk}", c3)

    st.markdown("---")
    st.write(t("reports.summary_text"))

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(t("reports.export_csv"), data=reports_utils.export_csv_bytes(df), file_name="surakshitpath_export.csv", mime="text/csv")
    with c2:
        pdf_bytes = reports_utils.build_pdf_summary({
            t("kpi.total_vendors"): total,
            t("kpi.avg_risk"): f"{avg_risk:.1f}",
            t("kpi.high_risk"): high_risk,
            t("kpi.avg_delay"): f"{avg_delay:.1f}%",
        })
        st.download_button(t("reports.export_pdf"), data=pdf_bytes, file_name="surakshitpath_summary.pdf", mime="application/pdf")


# App Routing
if not st.session_state.logged_in:
    login_view()
else:
    states, products, risks, show_weather, show_zones = sidebar_controls()
    df = data_utils.apply_filters(st.session_state.df, states, products, risks)

    tabs = st.tabs([t("tabs.overview"), t("tabs.prediction"), t("tabs.routing"), t("tabs.reports")])
    with tabs[0]:
        tab_overview(df)
    with tabs[1]:
        tab_prediction(df, show_weather)
    with tabs[2]:
        tab_routing(df, show_zones, show_weather)
    with tabs[3]:
        tab_reports(df)