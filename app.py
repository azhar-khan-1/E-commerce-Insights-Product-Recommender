import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Page configuration
st.set_page_config(
    page_title="E-commerce Insights & Recommendation System",
    page_icon="🛒",
    layout="wide"
)


# Dashboard title
st.title("🛒 E-commerce Insights & Product Recommendation System")

st.markdown(
    """
    **Interactive analytics dashboard** for customer segmentation,
    business performance analysis, and product recommendations.
    """
)

st.divider()

# Load processed data

rfm = pd.read_csv("data/processed/customer_rfm_segments.csv")
segment_analysis = pd.read_csv("data/processed/customer_segment_analysis.csv")

recommendations = pd.read_csv(
    "data/processed/sample_product_recommendations.csv"
)

st.success("Data loaded successfully!")

print(rfm.shape)
print(segment_analysis.shape)
print(recommendations.shape)

# Key Business Metrics

total_customers = rfm["customer_id"].nunique()
total_revenue = rfm["Monetary"].sum()
avg_revenue = rfm["Monetary"].mean()
total_segments = rfm["Customer_Segment"].nunique()

st.subheader("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col3.metric("Avg Revenue / Customer", f"₹{avg_revenue:,.0f}")
col4.metric("Customer Segments", total_segments)

# Customer Segment Filter

st.subheader("🔎 Explore Customer Segment")

selected_segment = st.selectbox(
    "Select Customer Segment",
    ["All Segments"] + sorted(rfm["Customer_Segment"].unique().tolist())
)

if selected_segment == "All Segments":
    filtered_rfm = rfm
else:
    filtered_rfm = rfm[
        rfm["Customer_Segment"] == selected_segment
    ]

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

# Customer Segment Distribution

st.subheader("👥 Customer Segmentation")

segment_counts = (
    rfm["Customer_Segment"]
    .value_counts()
    .reset_index()
)

segment_counts.columns = ["Customer_Segment", "Customers"]

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    segment_counts["Customer_Segment"],
    segment_counts["Customers"]
)

ax.set_xlabel("Customer Segment")
ax.set_ylabel("Number of Customers")
ax.set_title("Customer Distribution by Segment")

plt.xticks(rotation=30)
plt.tight_layout()

st.pyplot(fig)

# Revenue by Customer Segment

st.subheader("💰 Revenue by Customer Segment")

revenue_data = segment_analysis.sort_values(
    "Total_Revenue",
    ascending=False
)

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    revenue_data["Customer_Segment"],
    revenue_data["Total_Revenue"]
)

ax.set_xlabel("Customer Segment")
ax.set_ylabel("Total Revenue")
ax.set_title("Revenue Contribution by Customer Segment")

plt.xticks(rotation=30)
plt.tight_layout()

st.pyplot(fig)
# Load Product Category Mapping

product_data = pd.read_csv("data/raw/olist_products_dataset.csv")

product_category_map = (
    product_data[['product_id', 'product_category_name']]
    .drop_duplicates('product_id')
    .set_index('product_id')['product_category_name']
    .to_dict()
)

# Product Recommendation Section

st.subheader("🛍️ Product Recommendation")

# Load product similarity matrix
similarity_df = pd.read_csv(
    "data/processed/product_similarity_matrix.csv",
    index_col=0
)

# Load product data
product_data = pd.read_csv(
    "data/raw/olist_products_dataset.csv"
)

# Product category mapping
product_category_map = (
    product_data[['product_id', 'product_category_name']]
    .drop_duplicates('product_id')
    .set_index('product_id')['product_category_name']
    .to_dict()
)

# Product popularity
order_items = pd.read_csv(
    "data/raw/olist_order_items_dataset.csv"
)

product_popularity = (
    order_items['product_id']
    .value_counts()
)

product_ids = similarity_df.index.tolist()

selected_product = st.selectbox(
    "Select a Product ID",
    product_ids
)

if selected_product:

    # Get similarity scores
    similarity_scores = (
        similarity_df[selected_product]
        .drop(selected_product)
        .sort_values(ascending=False)
    )

    # Keep only products with positive similarity
    similar_products = similarity_scores[
        similarity_scores > 0
    ].head(5)

    # If no meaningful similarity exists, use popularity fallback
    if len(similar_products) == 0:

        st.info(
            "No strong co-purchase similarity found. "
            "Showing popular products as fallback recommendations."
        )

        fallback_products = (
            product_popularity
            .drop(index=selected_product, errors='ignore')
            .head(5)
        )

        recommendation_table = pd.DataFrame({
            "Recommended_Product_ID": fallback_products.index,
            "Popularity": fallback_products.values
        })

        recommendation_table["Category"] = (
            recommendation_table["Recommended_Product_ID"]
            .map(product_category_map)
            .fillna("Unknown")
        )

        recommendation_table["Recommendation_Type"] = "Popularity Fallback"

    else:

        recommendation_table = pd.DataFrame({
            "Recommended_Product_ID": similar_products.index,
            "Similarity_Score": similar_products.values
        })

        recommendation_table["Category"] = (
            recommendation_table["Recommended_Product_ID"]
            .map(product_category_map)
            .fillna("Unknown")
        )

        recommendation_table["Recommendation_Type"] = "Similarity Based"

    st.write("### Top 5 Recommended Products")

    st.dataframe(
        recommendation_table,
        use_container_width=True
    )
# Load Product Category Mapping

product_data = pd.read_csv("data/raw/olist_products_dataset.csv")

product_category_map = (
    product_data[['product_id', 'product_category_name']]
    .drop_duplicates('product_id')
    .set_index('product_id')['product_category_name']
    .to_dict()
)   