import pandas as pd
import json
import matplotlib.pyplot as plt
import streamlit as st
import re

def convert_persian_to_english(text):
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    english_numbers = '0123456789'
    translation_table = str.maketrans(persian_numbers, english_numbers)
    return text.translate(translation_table)

def extract_numeric_weight(weight_str):
    match = re.match(r"(\d+(\.\d+)?)", weight_str.replace(" گرم", "").strip())
    return float(match.group(1)) if match else None

with open('streamlit_brands_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for product in data:
    if product.get('price'):
        product['price'] = convert_persian_to_english(product['price'])
    if product.get('carat'):
        product['carat'] = convert_persian_to_english(product['carat'])
    if product.get('overall_score'):
        product['overall_score'] = convert_persian_to_english(product['overall_score'])
    if product.get('number_of_scorers'):
        product['number_of_scorers'] = convert_persian_to_english(product['number_of_scorers'])
    if product.get('number_of_comments'):
        product['number_of_comments'] = convert_persian_to_english(product['number_of_comments'])
    if product.get('number_of_questions'):
        product['number_of_questions'] = convert_persian_to_english(product['number_of_questions'])

df = pd.json_normalize(data)
df['weight'] = df['weight'].apply(extract_numeric_weight)

comments_list = []
for product in data:
    product_name = product['product_name']
    product_url = product['url']
    for comment in product.get('comments', []):
        comment['product_name'] = f'<a href="{product_url}" target="_blank">{product_name}</a>'
        comments_list.append(comment)
comments = pd.DataFrame(comments_list)

questions_list = []
for product in data:
    product_name = product['product_name']
    product_url = product['url']
    for question in product.get('questions', []):
        question['product_name'] = f'<a href="{product_url}" target="_blank">{product_name}</a>'
        questions_list.append(question)
questions = pd.DataFrame(questions_list)

comments_agg = comments.groupby('product_name').agg({
    'comment_text': 'count',
}).reset_index()

questions_agg = questions.groupby('product_name').agg({
    'question_text': 'count',
}).reset_index()

df = df.merge(comments_agg, on='product_name', how='left')
df = df.merge(questions_agg, on='product_name', how='left')

df['comment_text'] = df['comment_text'].fillna(0)

brand_comments_agg = df.groupby('brand_name')['comment_text'].sum().reset_index()
brand_questions_agg = df.groupby('brand_name')['question_text'].sum().reset_index()


# df = df.merge(comments, on='product_name', how='left', suffixes=('', '_comment'))
# df = df.merge(questions, on='product_name', how='left', suffixes=('', '_question'))

df['overall_score'] = pd.to_numeric(df['overall_score'], errors='coerce')
comments['comment_date'] = pd.to_datetime(comments['comment_date'], errors='coerce')

st.set_page_config(page_title="Product Dashboard", layout="wide")

st.markdown("""
    <style>
        /* General styles */
        body {
            direction: ltr;
            text-align: left;
            font-family: 'Arial', sans-serif;
        }
        .css-18e3th9, .css-1v3fvcr, .css-1vq4p4l, .css-1ybk5t4, .css-12w0q2b {
            direction: ltr;
        }
        table {
            direction: ltr;
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f4f4f4;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        .stMarkdown {
            font-family: 'Arial', sans-serif;
        }
        /* Custom CSS for table styles */
        .custom-table {
            width: 100% !important;
            border-collapse: collapse !important;
            overflow-x: auto !important; /* Ensures horizontal scrolling */
        }
        .custom-table th, .custom-table td {
            padding: 15px !important;
            border: 1px solid #ddd !important;
            font-size: 16px !important;
        }
        .custom-table th {
            background-color: #f4f4f4 !important;
            font-weight: bold !important;
        }
        .custom-table tbody tr:hover {
            background-color: #f1f1f1 !important;
        }
        .scrollable-table-container {
            max-height: 500px; /* Adjust the height as needed */
            overflow-y: auto; /* Vertical scrolling */
            overflow-x: auto; /* Horizontal scrolling if needed */
        }
    </style>
    """, unsafe_allow_html=True)


st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Arial:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

st.title("Product Dashboard")
# st.markdown("<h1 style='text-align: center;'>Product Dashboard</h1>", unsafe_allow_html=True)

st.sidebar.title('Navigation')
pages = ['Overview', 'Products', 'Comments', 'Questions', 'Brand Analysis']
selected_page = st.sidebar.radio('Select Page:', pages)

# Overview Page
if selected_page == 'Overview':
    st.header('Overview')


    df['weight'] = df['weight'].fillna('Unknown')
    weight_counts = df['weight'].value_counts()
    
    st.subheader('Number of Products by Weight')
    st.bar_chart(weight_counts)

    carat_counts = df['carat'].fillna('Unknown').value_counts()
    st.subheader('Number of Products by Carat')
    st.bar_chart(carat_counts)

    satisfaction = df['overall_score'].dropna()
    st.subheader('Overall Satisfaction')
    if not satisfaction.empty:
        st.write(f"Average Satisfaction Score: {satisfaction.mean():.2f}")
    else:
        st.write('Satisfaction score is not available.')

    total_comments = comments.shape[0]
    st.write(f'Total Number of Comments: {total_comments}')

    total_questions = questions.shape[0]
    st.write(f'Total Number of Questions: {total_questions}')

    brand_counts = df['brand_name'].fillna('Unknown').value_counts()
    st.subheader('Number of Products by Brand')
    st.bar_chart(brand_counts)

    brand_satisfaction = df.groupby('brand_name')['overall_score'].mean().sort_values()
    st.subheader('Satisfaction by Brand')
    st.bar_chart(brand_satisfaction)

# Products Page
elif selected_page == 'Products':
    st.header('Products')

    search_text = st.text_input('Search for a Product:', '')
    
    filtered_products = df[df['product_name'].str.contains(search_text, case=False, na=False)]
    
    if not filtered_products.empty:
        product_options = filtered_products[['product_name', 'url']].dropna()
        selected_product_info = st.selectbox('Select Product:', product_options.to_dict('records'), format_func=lambda x: x['product_name'])
        
        selected_product_name = selected_product_info['product_name']
        selected_product_url = selected_product_info['url']
        
        product_df = df[df['product_name'] == selected_product_name]

        if not product_df.empty:
            st.subheader('Product Details')
            st.markdown(f"Product Name: <a href='{selected_product_url}' target='_blank'>{selected_product_name}</a>", unsafe_allow_html=True)
            st.write(f"Carat: {product_df['carat'].iloc[0]}")
            st.write(f"Weight: {product_df['weight'].iloc[0]} gr")
            st.write(f"Price: {product_df['price'].iloc[0]} toman")
            st.write(f"Brand: {product_df['brand_name'].iloc[0]}")

            st.subheader('Comments')
            product_comments = comments[comments['product_name'].str.contains(selected_product_name, na=False)]
            if not product_comments.empty:
                comments_html = product_comments.to_html(escape=False, index=False, render_links=True)
                st.markdown(f'<div class="scrollable-table-container">{comments_html}</div>', unsafe_allow_html=True)
            else:
                st.write('No comments available for this product.')

            st.subheader('Questions')
            product_questions = questions[questions['product_name'].str.contains(selected_product_name, na=False)]
            if not product_questions.empty:
                questions_html = product_questions.to_html(escape=False, index=False, render_links=True)
                st.markdown(f'<div class="scrollable-table-container">{questions_html}</div>', unsafe_allow_html=True)
            else:
                st.write('No questions available for this product.')
    else:
        st.write('No products found matching the search criteria.')




elif selected_page == 'Comments':
    st.header('Comments')

    if not comments.empty:
        st.write('Click on the product names to view their details.')
        if 'product_url' in comments.columns:
            comments = comments.drop(columns='product_url')
        st.markdown('<div class="scrollable-table-container">' + comments.to_html(escape=False, index=False, classes='custom-table') + '</div>', unsafe_allow_html=True)
    else:
        st.write('No comments available for display.')

    st.subheader('Number of Comments Over Time')
    if not comments['comment_date'].dropna().empty:
        comments_over_time = comments['comment_date'].dropna().dt.to_period('M').value_counts().sort_index()
        plt.figure(figsize=(12, 6))
        plt.plot(comments_over_time.index.astype(str), comments_over_time.values, marker='o')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel('Date', loc='left')
        plt.ylabel('Number of Comments')
        plt.title('Number of Comments Over Time', loc='left')
        st.pyplot(plt)
    else:
        st.write('No comments available for display.')


elif selected_page == 'Questions':
    st.header('Questions')

    if not questions.empty:
        st.write('Click on the product names to view their details.')
        if 'product_url' in questions.columns:
            questions = questions.drop(columns='product_url')
        st.markdown('<div class="scrollable-table-container">' + questions.to_html(escape=False, index=False, classes='custom-table') + '</div>', unsafe_allow_html=True)
    else:
        st.write('No questions available for display.')




elif selected_page == 'Brand Analysis':
    st.header('Brand Analysis')

    brand_options = df['brand_name'].dropna().unique()
    selected_brand = st.selectbox('Select Brand:', brand_options)

    brand_df = df[df['brand_name'] == selected_brand]

    if not brand_df.empty:
        def extract_product_name(html):
            match = re.search(r'>(.*?)<', html)
            return match.group(1) if match else html

        brand_df['product_name_text'] = brand_df['product_name'].apply(
            lambda x: extract_product_name(x) if isinstance(x, str) else x
        )
        comments['product_name_text'] = comments['product_name'].apply(
            lambda x: extract_product_name(x) if isinstance(x, str) else x
        )

        brand_df['product_name_text'] = brand_df['product_name_text'].str.strip().str.lower()
        comments['product_name_text'] = comments['product_name_text'].str.strip().str.lower()
        
        questions['product_name_text'] = questions['product_name'].apply(
            lambda x: extract_product_name(x) if isinstance(x, str) else x
        )
        questions['product_name_text'] = questions['product_name_text'].str.strip().str.lower()
        
        # st.write("Standardized product names in brand_df:", brand_df['product_name_text'].unique())
        # st.write("Standardized product names in comments:", comments['product_name_text'].unique())
        # st.write("Standardized product names in questions:", questions['product_name_text'].unique())

        brand_df['product_name'] = brand_df.apply(
            lambda row: f"<a href='{row['url']}' target='_blank'>{row['product_name_text']}</a>", axis=1
        )

        st.subheader(f'Products of Brand {selected_brand}')
        st.markdown('<div class="scrollable-table-container">' +
                    brand_df[['product_name', 'carat', 'weight', 'price', 'overall_score']].to_html(escape=False, index=False, classes='custom-table') +
                    '</div>', unsafe_allow_html=True)

        brand_comments = comments[comments['product_name_text'].isin(brand_df['product_name_text'])]
        brand_questions = questions[questions['product_name_text'].isin(brand_df['product_name_text'])]

        total_comments = brand_comments.shape[0]
        total_questions = brand_questions.shape[0]
        st.write(f'Total Comments: {total_comments}')
        st.write(f'Total Questions: {total_questions}')

        st.subheader(f'Number of Comments for Brand {selected_brand} Over Time')

        if not brand_comments.empty:
            brand_comments['comment_date'] = pd.to_datetime(brand_comments['comment_date'], errors='coerce')
            
            valid_dates = brand_comments['comment_date'].dropna()
            if not valid_dates.empty:
                brand_comments_over_time = valid_dates.dt.to_period('M').value_counts().sort_index()

                # st.write("Comments Over Time:")
                # st.write(brand_comments_over_time)

                plt.figure(figsize=(12, 6))
                plt.plot(brand_comments_over_time.index.astype(str), brand_comments_over_time.values, marker='o')
                plt.xticks(rotation=45, ha='right')
                plt.xlabel('Date', loc='left')
                plt.ylabel('Number of Comments')
                plt.title('Number of Comments Over Time', loc='left')
                st.pyplot(plt)
            else:
                st.write('No valid comment dates available for display.')
        else:
            st.write('No comments available for the selected brand.')
    else:
        st.write('No products found for the selected brand.')
