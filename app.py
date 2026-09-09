import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="E-commerce Analytics",
    page_icon="🛒",
    layout="wide"
)


# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------

st.sidebar.title("🛒 E-commerce Analytics")

page = st.sidebar.radio(
    "Navigate to",
    [
        "📊 Business Overview",
        "👥 Customer Analytics",
        "🛍️ Product Recommendations"
    ]
)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():

    rfm = pd.read_csv(
        "data/processed/customer_rfm_segments.csv"
    )

    segment_analysis = pd.read_csv(
        "data/processed/customer_segment_analysis.csv"
    )

    similarity_df = pd.read_csv(
        "data/processed/product_similarity_matrix.csv",
        index_col=0
    )

    product_data = pd.read_csv(
        "data/raw/olist_products_dataset.csv"
    )

    order_items = pd.read_csv(
        "data/raw/olist_order_items_dataset.csv"
    )

    return (
        rfm,
        segment_analysis,
        similarity_df,
        product_data,
        order_items
    )


rfm, segment_analysis, similarity_df, product_data, order_items = load_data()


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("🛒 E-commerce Analytics Dashboard")

st.caption(
    "Customer segmentation, business performance, and product recommendation insights"
)

st.divider()


# =================================================
# PAGE 1 — BUSINESS OVERVIEW
# =================================================

if page == "📊 Business Overview":

    st.header("📊 Business Overview")

    total_customers = rfm["customer_id"].nunique()
    total_revenue = rfm["Monetary"].sum()
    avg_revenue = rfm["Monetary"].mean()
    total_segments = rfm["Customer_Segment"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        f"{total_customers:,}"
    )

    col2.metric(
        "Total Revenue",
        f"₹{total_revenue:,.0f}"
    )

    col3.metric(
        "Avg Revenue / Customer",
        f"₹{avg_revenue:,.0f}"
    )

    col4.metric(
        "Customer Segments",
        total_segments
    )

    st.divider()

    # -------------------------------------------------
    # BUSINESS OVERVIEW CHARTS (Side-by-Side)
    # -------------------------------------------------

    chart_col1, chart_col2 = st.columns(2)

    # Customer distribution
    with chart_col1:

        st.subheader("👥 Customer Segments")

        segment_counts = (
            rfm["Customer_Segment"]
            .value_counts()
            .reset_index()
        )

        segment_counts.columns = [
            "Customer_Segment",
            "Customers"
        ]

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.bar(
            segment_counts["Customer_Segment"],
            segment_counts["Customers"]
        )

        ax.set_xlabel("Segment")
        ax.set_ylabel("Customers")

        plt.xticks(rotation=30)
        plt.tight_layout()

        st.pyplot(fig)

    # Revenue distribution
    with chart_col2:

        st.subheader("💰 Revenue by Segment")

        revenue_data = (
            segment_analysis
            .sort_values(
                "Total_Revenue",
                ascending=False
            )
        )

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.bar(
            revenue_data["Customer_Segment"],
            revenue_data["Total_Revenue"]
        )

        ax.set_xlabel("Segment")
        ax.set_ylabel("Revenue")

        plt.xticks(rotation=30)
        plt.tight_layout()

        st.pyplot(fig)


# =================================================
# PAGE 2 — CUSTOMER ANALYTICS
# =================================================

elif page == "👥 Customer Analytics":

    st.header("👥 Customer Analytics")

    st.markdown(
        """
        Analyze customer behavior using **RFM (Recency, Frequency,
        Monetary) segmentation**.
        """
    )

    st.divider()

    # Segment filter
    selected_segment = st.selectbox(
        "Select Customer Segment",
        [
            "All Segments"
        ] + sorted(
            rfm["Customer_Segment"].unique().tolist()
        )
    )

    if selected_segment == "All Segments":

        filtered_rfm = rfm

    else:

        filtered_rfm = rfm[
            rfm["Customer_Segment"] == selected_segment
        ]

    # Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Customers",
        f"{filtered_rfm['customer_id'].nunique():,}"
    )

    col2.metric(
        "Revenue",
        f"₹{filtered_rfm['Monetary'].sum():,.0f}"
    )

    col3.metric(
        "Avg Revenue / Customer",
        f"₹{filtered_rfm['Monetary'].mean():,.0f}"
    )

    st.divider()

    # RFM overview
    st.subheader("📋 RFM Segment Summary")

    display_data = (
        segment_analysis
        .sort_values(
            "Total_Revenue",
            ascending=False
        )
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Segment revenue
    st.subheader("💰 Segment Revenue Analysis")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        display_data["Customer_Segment"],
        display_data["Total_Revenue"]
    )

    ax.set_xlabel("Customer Segment")
    ax.set_ylabel("Total Revenue")
    ax.set_title("Revenue by Customer Segment")

    plt.xticks(rotation=25)
    plt.tight_layout()

    st.pyplot(fig)

    st.divider()

    # Customer-level RFM data
    st.subheader("🔎 Customer RFM Data")

    st.dataframe(
        filtered_rfm[
            [
                "customer_id",
                "Recency",
                "Frequency",
                "Monetary",
                "RFM_Score",
                "Customer_Segment"
            ]
        ].head(100),
        use_container_width=True,
        hide_index=True
    )


# =================================================
# PAGE 3 — PRODUCT RECOMMENDATIONS
# =================================================

elif page == "🛍️ Product Recommendations":

    st.header("🛍️ Product Recommendation System")

    st.markdown(
        """
        Select a product to discover the **top 5 products with
        similar purchase patterns**.
        """
    )

    st.divider()

    # Product category mapping
    product_category_map = (
        product_data[
            [
                "product_id",
                "product_category_name"
            ]
        ]
        .drop_duplicates("product_id")
        .set_index("product_id")[
            "product_category_name"
        ]
        .to_dict()
    )

    # Product popularity
    product_popularity = (
        order_items["product_id"]
        .value_counts()
    )

    product_ids = similarity_df.index.tolist()

    selected_product = st.selectbox(
        "Select a Product ID",
        product_ids
    )

    if selected_product:

        similarity_scores = (
            similarity_df[selected_product]
            .drop(selected_product)
            .sort_values(
                ascending=False
            )
        )

        similar_products = (
            similarity_scores[
                similarity_scores > 0
            ]
            .head(5)
        )

        # -----------------------------------------
        # Similarity based recommendation
        # -----------------------------------------

        if len(similar_products) > 0:

            recommendation_table = pd.DataFrame(
                {
                    "Recommended Product ID":
                        similar_products.index,

                    "Similarity Score":
                        similar_products.values
                }
            )

            recommendation_table[
                "Category"
            ] = (
                recommendation_table[
                    "Recommended Product ID"
                ]
                .map(product_category_map)
                .fillna("Unknown")
            )

            recommendation_table[
                "Recommendation Type"
            ] = "Similarity Based"

            st.success(
                "Similarity-based recommendations found."
            )

        # -----------------------------------------
        # Popularity fallback
        # -----------------------------------------

        else:

            st.info(
                "No strong co-purchase similarity found. "
                "Showing popular products as fallback recommendations."
            )

            fallback_products = (
                product_popularity
                .drop(
                    index=selected_product,
                    errors="ignore"
                )
                .head(5)
            )

            recommendation_table = pd.DataFrame(
                {
                    "Recommended Product ID":
                        fallback_products.index,

                    "Popularity":
                        fallback_products.values
                }
            )

            recommendation_table[
                "Category"
            ] = (
                recommendation_table[
                    "Recommended Product ID"
                ]
                .map(product_category_map)
                .fillna("Unknown")
            )

            recommendation_table[
                "Recommendation Type"
            ] = "Popularity Fallback"

        # -----------------------------------------
        # Display recommendations
        # -----------------------------------------

        st.subheader("⭐ Top 5 Recommended Products")

        st.dataframe(
            recommendation_table,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("📌 Selected Product")

        selected_category = (
            product_category_map
            .get(
                selected_product,
                "Unknown"
            )
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Product ID",
            selected_product
        )

        col2.metric(
            "Category",
            selected_category
        )