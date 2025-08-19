import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import logging
from app.scraper import Scraper
import tomllib
import plotly.express as px
import plotly.graph_objects as go

page_title = "Dev Environment"
st.set_page_config(page_title=page_title, layout="wide")


def get_environment():
    return os.getenv("ENVIRONMENT", "prod").lower()


def set_environment_styling(env: str, config_path=".streamlit/config.toml"):
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    env_config = config.get(env)
    if not env_config:
        raise ValueError(f"No config found for environment: {env}")

    if env != "prod":
        st.info(f"ℹ️ Using configuration for {env} environment")
    st.markdown(
        f"""
    <style>
    .main-header {{
        background: linear-gradient(90deg, {env_config['header_color']}, {env_config['header_color']}dd);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .stApp {{
        background-color: {env_config['background_color']};
    }}
    
    .environment-badge {{
        background-color: {env_config['header_color']};
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }}
    
    .metric-card {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {env_config['header_color']};
        margin-bottom: 1rem;
    }}
    
    .pet-card {{
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }}
    
    .pet-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .stat-container {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin: 1rem;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    return env_config


@st.cache_data(ttl=300)
def load_pet_data():
    csv_file = "petconnect_pets.csv"

    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            return df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None

    return None


def run_scraper():
    """Run the scraper with better error handling and progress indication"""
    try:
        with st.spinner("🔍 Fetching fresh pet data from PetConnect.be..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Initializing scraper...")
            progress_bar.progress(10)

            scraper = Scraper()
            status_text.text("Scraping pet data...")
            progress_bar.progress(50)

            pets = scraper.run_scraper(max_items=50)
            progress_bar.progress(80)

            if pets:
                status_text.text("Saving data...")
                scraper.save_to_csv("petconnect_pets.csv")
                progress_bar.progress(100)
                status_text.text("Complete!")

                df = pd.DataFrame(
                    [
                        {
                            "id": pet.get("id", ""),
                            "title": pet.get("title", ""),
                            "breed": pet.get("breed", ""),
                            "size": pet.get("size", ""),
                            "gender": pet.get("gender", ""),
                            "age_year": pet.get("age_year", ""),
                            "place_of_residence": pet.get("place_of_residence", ""),
                            "short_description": pet.get("short_description", ""),
                            "main_image": pet.get("main_image", ""),
                            "full_url": pet.get("full_url", ""),
                            "added_date": pet.get("added_date", ""),
                        }
                        for pet in pets
                    ]
                )

                return df
            else:
                st.error("❌ No pet data could be retrieved")
                return None

    except Exception as e:
        st.error(f"❌ Error running scraper: {str(e)}")
        logging.error(f"Scraper error: {str(e)}")
        return None


def create_analytics_dashboard(df):
    if df is None or df.empty:
        return

    st.subheader("📊 Pet Analytics Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_pets = len(df)
        st.markdown(
            f"""
        <div class="stat-container">
            <h3 style="color: #FF6B35; margin: 0;">🐾</h3>
            <h2 style="margin: 0;">{total_pets}</h2>
            <p style="margin: 0; color: #666;">Total Pets</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        unique_breeds = df["breed"].nunique() if "breed" in df.columns else 0
        st.markdown(
            f"""
        <div class="stat-container">
            <h3 style="color: #FF6B35; margin: 0;">🏷️</h3>
            <h2 style="margin: 0;">{unique_breeds}</h2>
            <p style="margin: 0; color: #666;">Breeds</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        locations = (
            df["place_of_residence"].nunique()
            if "place_of_residence" in df.columns
            else 0
        )
        st.markdown(
            f"""
        <div class="stat-container">
            <h3 style="color: #FF6B35; margin: 0;">📍</h3>
            <h2 style="margin: 0;">{locations}</h2>
            <p style="margin: 0; color: #666;">Locations</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if "size" in df.columns:
            size_counts = df["size"].value_counts()
            if not size_counts.empty:
                fig_pie = px.pie(
                    values=size_counts.values,
                    names=size_counts.index,
                    title="Distribution by Size",
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        if "gender" in df.columns:
            gender_counts = df["gender"].value_counts()
            if not gender_counts.empty:
                fig_bar = px.bar(
                    x=gender_counts.index,
                    y=gender_counts.values,
                    title="Distribution by Gender",
                )
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)


def display_pet_gallery(df):
    if df is None or df.empty:
        return

    st.subheader("🐾 Available Pets")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input(
            "🔍 Search pets", placeholder="Search by name, breed, or description..."
        )
    with col2:
        size_options = (
            ["All"] + list(df["size"].dropna().unique())
            if "size" in df.columns
            else ["All"]
        )
        size_filter = st.selectbox("Filter by size", size_options)
    with col3:
        gender_options = (
            ["All"] + list(df["gender"].dropna().unique())
            if "gender" in df.columns
            else ["All"]
        )
        gender_filter = st.selectbox("Filter by gender", gender_options)

    filtered_df = df.copy()

    if search_term:
        search_columns = ["title", "breed", "short_description"]
        mask = pd.Series([False] * len(filtered_df))
        for col in search_columns:
            if col in filtered_df.columns:
                mask |= filtered_df[col].str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[mask]

    if size_filter != "All" and "size" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["size"].str.contains(size_filter, case=False, na=False)
        ]

    if gender_filter != "All" and "gender" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["gender"].str.contains(gender_filter, case=False, na=False)
        ]

    st.info(f"Showing {len(filtered_df)} of {len(df)} pets")

    if len(filtered_df) == 0:
        st.warning("No pets match your search criteria")
        return

    cols_per_row = 3
    for i in range(0, len(filtered_df), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, (idx, pet) in enumerate(
            filtered_df.iloc[i : i + cols_per_row].iterrows()
        ):
            if j < len(cols):
                with cols[j]:

                    st.markdown(
                        f"""
                    <div class="pet-card">
                        <h4 style="color: #FF6B35; margin-bottom: 10px;">
                            {pet.get('title', 'Unknown')} 
                            {'🐕' if pet.get('gender') == 'Male' else '🐶' if pet.get('gender') == 'Female' else '🐾'}
                        </h4>
                        <p><strong>Breed:</strong> {pet.get('breed', 'N/A')}</p>
                        <p><strong>Size:</strong> {pet.get('size', 'N/A')}</p>
                        <p><strong>Gender:</strong> {pet.get('gender', 'N/A')}</p>
                        <p><strong>Age:</strong> {pet.get('age_year', 'N/A')}</p>
                        <p><strong>Location:</strong> {pet.get('place_of_residence', 'N/A')}</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    if pet.get("main_image"):
                        try:
                            st.image(pet["main_image"], use_container_width=True)
                        except Exception as e:
                            st.info("📷 Image not available")
                    else:
                        st.info("📷 No image available")

                    if pet.get("short_description"):
                        with st.expander("📝 View Description"):
                            st.write(pet["short_description"])

                    if pet.get("full_url"):
                        st.link_button("👀 View Details", pet["full_url"])


def main():
    """Main application with enhanced layout"""
    env = get_environment()
    config = set_environment_styling(env)

    # Header
    st.markdown(
        f"""
    <div class="main-header">
        <h1>{config['title']} {config.get('page_icon', '🐾')}</h1>

    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        if env != "prod":
            st.markdown(
                f"""
        <div class="environment-badge">
            {env.upper()} Environment
        </div>
        """,
                unsafe_allow_html=True,
            )

        st.markdown("### 🌍 System Info")
        st.markdown(
            f"""
        - **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        )

        st.markdown("### 📊 Data Management")
        st.markdown("**Source:** PetConnect.be")

        if st.button("🔄 Refresh Pet Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            df = run_scraper()
            if df is not None:
                st.success("✅ Data refreshed successfully!")
                st.rerun()

        # Data status
        csv_file = "petconnect_pets.csv"
        if os.path.exists(csv_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(csv_file))
            st.info(f"📅 Last updated: {file_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.warning("⚠️ No cached data available")

    # Main content
    df = load_pet_data()

    if df is None:
        st.warning(
            "⚠️ No pet data available. Click 'Refresh Pet Data' to fetch fresh data."
        )
        if st.button("🚀 Get Pet Data Now", type="primary"):
            df = run_scraper()
            if df is not None:
                st.rerun()
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🐾 Pet Gallery", "📋 Raw Data"])

        with tab1:
            create_analytics_dashboard(df)

        with tab2:
            display_pet_gallery(df)

        with tab3:
            st.subheader("📋 Raw Pet Data")

            col1, col2 = st.columns([3, 1])
            with col2:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=f"petconnect_data_{env}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True,
                )

            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "main_image": st.column_config.ImageColumn("Image", width="small"),
                    "full_url": st.column_config.LinkColumn("Details"),
                },
            )


if __name__ == "__main__":
    main()
