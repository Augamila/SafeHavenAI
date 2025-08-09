import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import base64, os

st.set_page_config(layout="wide", page_title="SafeHaven Fundraising AI", page_icon="💜")

def load_css(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("styles.css")

def app_bar():
    logo_path_svg = "assets/logo.svg"
    if os.path.exists(logo_path_svg):
        with open(logo_path_svg, "r", encoding="utf-8") as f:
            svg = f.read()
        svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        logo_html = f'<img src="data:image/svg+xml;base64,{svg_b64}" alt="SafeHaven Logo" />'
    else:
        logo_html = "<span style='font-weight:700;font-size:1.1rem;'>SafeHaven</span>"
    st.markdown(f'''
        <div class="safehaven-appbar">
          {logo_html}
          <div class="safehaven-tag">Live • Synthetic Data</div>
        </div>
        ''', unsafe_allow_html=True)

app_bar()

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = px.colors.sequential.Purples

def generate_synthetic_donors(n_donors=500):
    data = {
        'donor_id': range(1001, 1001 + n_donors),
        'name': [f'Donor_{i}' for i in range(n_donors)],
        'join_date': [datetime.now().date() - timedelta(days=np.random.randint(30, 730)) for _ in range(n_donors)],
        'total_donations': np.random.randint(1, 50, n_donors),
        'total_amount': np.random.lognormal(4, 1.5, n_donors).astype(int)
    }
    donors_df = pd.DataFrame(data)
    donors_df['avg_donation'] = donors_df['total_amount'] / donors_df['total_donations']
    return donors_df

def get_live_donations_data(donors_df, num_donations=100):
    donor_ids = np.random.choice(donors_df['donor_id'], num_donations)
    data = {
        'timestamp': pd.to_datetime(pd.date_range(datetime.now().date(), periods=num_donations, freq='h')),
        'amount': np.random.lognormal(3, 1, num_donations).astype(int) + 5,
        'campaign': np.random.choice(['Summer Appeal', 'Holiday Drive', 'Emergency Fund'], num_donations, p=[0.5, 0.3, 0.2]),
        'donor_id': donor_ids
    }
    return pd.DataFrame(data).merge(donors_df[['donor_id', 'name']], on='donor_id', how='left')

def get_donor_segments(donors_df):
    conditions = [
        (donors_df['total_amount'] > 150) & (donors_df['total_donations'] > 10),
        (donors_df['total_amount'] > 50) & (donors_df['join_date'] > (datetime.now().date() - timedelta(days=90))),
        (donors_df['total_donations'] == 1),
    ]
    choices = ['💜 Champions', 'Emerging Supporters', 'One-Time Givers']
    donors_df['segment'] = np.select(conditions, choices, default='At-Risk Donors')
    segment_counts = donors_df['segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'count']
    return segment_counts

def get_churn_risk_donors(donors_df, num_at_risk=5):
    at_risk_candidates = donors_df[donors_df['join_date'] < (datetime.now().date() - timedelta(days=180))]\
                            .sort_values('total_donations').head(num_at_risk).copy()
    at_risk_candidates['churn_risk_score'] = np.random.uniform(0.7, 0.95, size=num_at_risk).round(2)
    at_risk_candidates['suggested_action'] = 'Personal Call'
    return at_risk_candidates[['name', 'join_date', 'total_donations', 'churn_risk_score', 'suggested_action']]

def get_donation_nudges(donors_df, num_nudges=5):
    nudge_candidates = donors_df.sample(num_nudges).copy()
    nudge_candidates['suggested_ask'] = (nudge_candidates['avg_donation'] * 1.25).round(0)
    nudge_candidates['suggested_channel'] = np.random.choice(['Email', 'Targeted Ad', 'SMS'], num_nudges)
    return nudge_candidates[['name', 'avg_donation', 'suggested_ask', 'suggested_channel']]

with st.sidebar:
    st.markdown("### 💜 SafeHaven")
    st.caption("Fundraising AI Dashboard")
    st.markdown("---")
    st.markdown("**Brand Settings**")
    st.caption("Replace `assets/logo.svg` with your own to update the header.")
    st.markdown("---")
    st.caption("This demo uses synthetic data only.")

st.title("💜 Live Fundraising Dashboard for DV Survivors")
st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")

donors = generate_synthetic_donors()
live_donations = get_live_donations_data(donors)

st.header("📊 Real-Time Metrics (Today)")
col1, col2, col3 = st.columns(3)
total_raised_today = live_donations['amount'].sum()
new_donations_today = live_donations.shape[0]
col1.metric("Total Raised", f"${total_raised_today:,}")
col2.metric("New Donations", f"{new_donations_today}")
col3.metric("New Donors Reached", f"{live_donations['donor_id'].nunique()}")

st.header("🤖 AI-Powered Insights")
tab1, tab2, tab3 = st.tabs(["**Donor Segmentation**", "**Churn Prevention**", "**Donation Nudging**"])

with tab1:
    st.subheader("Live Donor Segments")
    segments_df = get_donor_segments(donors)
    fig_pie = px.pie(segments_df, names='segment', values='count', hole=0.4, title="Donor Distribution by Segment")
    fig_pie.update_layout(legend_title_text='Segments')
    st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("🚨 Donors at Risk of Churn")
    churn_df = get_churn_risk_donors(donors)
    st.dataframe(churn_df, use_container_width=True, hide_index=True,
                 column_config={"churn_risk_score": st.column_config.ProgressColumn("Churn Risk", format="%.2f", min_value=0, max_value=1)})
    if st.button("Launch Retention Campaign"):
        st.success("A targeted re-engagement campaign has been initiated for at-risk donors.")

with tab3:
    st.subheader("🎯 Personalized Donation Nudging")
    nudge_df = get_donation_nudges(donors)
    st.dataframe(nudge_df, use_container_width=True, hide_index=True,
                 column_config={
                     "avg_donation": st.column_config.NumberColumn(format="$%.2f"),
                     "suggested_ask": st.column_config.NumberColumn("Suggested Ask", format="$%.2f"),
                 })
    if st.button("Start Nudge Campaign"):
        st.success("A personalized nudge campaign has been launched via suggested channels.")

st.header("📈 Live Campaign Performance")
donations_by_campaign = live_donations.groupby('campaign')['amount'].sum().reset_index().sort_values('amount', ascending=False)
fig_bar = px.bar(donations_by_campaign, x='campaign', y='amount',
                 title='Total Raised by Campaign (Live)',
                 labels={'campaign': 'Campaign', 'amount': 'Total Raised ($)'},
                 color='campaign')
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown('<div class="footer-note">© {year} SafeHaven • Branding demo • Streamlit</div>'.format(year=datetime.now().year), unsafe_allow_html=True)