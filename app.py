import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px # ახალი ბიბლიოთეკა გრაფიკებისთვის

# 1. ფაილის სახელი
DATA_FILE = "my_finance_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["თარიღი", "კატეგორია", "ტიპი", "თანხა"])

df = load_data()

st.set_page_config(page_title="Unitech Analytics", layout="wide")
st.title("📊 Unitech ფინანსური მენეჯერი")

# --- Sidebar ---
st.sidebar.header("➕ ახალი ჩანაწერი")
input_date = st.sidebar.date_input("აირჩიეთ თარიღი", date.today())
category = st.sidebar.selectbox("კატეგორია", ["საკვები", "ტრანსპორტი", "ხელფასი", "ბიზნესი", "გართობა", "სხვა"])
t_type = st.sidebar.radio("ტიპი", ["შემოსავალი", "გასავალი"])
amount = st.sidebar.number_input("თანხა (₾)", min_value=0.0, step=1.0)

if st.sidebar.button("შენახვა"):
    new_entry = {"თარიღი": str(input_date), "კატეგორია": category, "ტიპი": t_type, "თანხა": amount}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.sidebar.success("მონაცემი შენახულია!")
    st.rerun()

# --- მთავარი ეკრანი ---
if not df.empty:
    # ბარათები (Metrics)
    total_income = df[df["ტიპი"] == "შემოსავალი"]["თანხა"].sum()
    total_expense = df[df["ტიპი"] == "გასავალი"]["თანხა"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("ჯამური შემოსავალი", f"{total_income} ₾")
    col2.metric("ჯამური ხარჯი", f"{total_expense} ₾")
    col3.metric("მიმდინარე ბალანსი", f"{balance} ₾")

    st.divider()

    # --- გრაფიკების სექცია ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("🍕 ხარჯების განაწილება")
        expenses_df = df[df["ტიპი"] == "გასავალი"]
        if not expenses_df.empty:
            # წრიული დიაგრამა
            fig_pie = px.pie(expenses_df, values='თანხა', names='კატეგორია', 
                             hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.write("ჯერ არ გაქვთ გასავლები გრაფიკისთვის.")

    with chart_col2:
        st.subheader("📊 შემოსავალი vs გასავალი")
        summary_df = df.groupby("ტიპი")["თანხა"].sum().reset_index()
        # სვეტოვანი დიაგრამა
        fig_bar = px.bar(summary_df, x="ტიპი", y="თანხა", color="ტიპი",
                         color_discrete_map={"შემოსავალი": "#00CC96", "გასავალი": "#EF553B"})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ცხრილი
    st.subheader("📋 ტრანზაქციების ისტორია")
    st.dataframe(df.sort_values(by="თარიღი", ascending=False), use_container_width=True)
    
    if st.button("🗑️ ყველა მონაცემის წაშლა"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.rerun()
else:
    st.info("შეიყვანეთ მონაცემები გვერდითა პანელიდან ანალიტიკის სანახავად.")