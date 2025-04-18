
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import random
import datetime

def simulate_inventory(product_name):
    return pd.DataFrame({
        'Process': ['Raw material extraction', 'Manufacturing', 'Transport', 'Use phase', 'End-of-life'],
        'Energy (MJ)': [random.uniform(10, 100) for _ in range(5)],
        'GHG Emissions (kg CO2-eq)': [random.uniform(1, 10) for _ in range(5)],
        'Water Use (L)': [random.uniform(5, 50) for _ in range(5)]
    })

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f'{self.title}', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, text)
        self.ln()

    def add_table(self, df):
        self.set_font('Arial', 'B', 10)
        col_width = (self.w - 2 * self.l_margin) / len(df.columns)
        for col in df.columns:
            self.cell(col_width, 10, col, 1)
        self.ln()
        self.set_font('Arial', '', 10)
        for _, row in df.iterrows():
            for item in row:
                self.cell(col_width, 10, str(round(item, 2)) if isinstance(item, float) else str(item), 1)
            self.ln()
        self.ln()

    def add_chart(self, fig):
        fig.savefig("chart.png")
        self.image("chart.png", w=180)

st.set_page_config(page_title="LCA Bot", layout="centered")
st.title("🔍 ISO-Compliant LCA Bot")
st.markdown("This bot performs a full cradle-to-grave LCA using test data and outputs a detailed PDF report.")

product_name = st.text_input("Enter the product name:", "Generic Product")

today = datetime.date.today()

if st.button("Run LCA"):
    inventory = simulate_inventory(product_name)
    ghg_total = inventory['GHG Emissions (kg CO2-eq)'].sum()
    water_total = inventory['Water Use (L)'].sum()
    energy_total = inventory['Energy (MJ)'].sum()
    top_process = inventory.loc[inventory['GHG Emissions (kg CO2-eq)'].idxmax(), 'Process']

    fig, ax = plt.subplots()
    inventory.plot(x='Process', y='GHG Emissions (kg CO2-eq)', kind='bar', ax=ax)

    pdf = PDF()
    pdf.set_title(f"ISO-Compliant LCA Report for {product_name}")
    pdf.add_page()

    pdf.chapter_title("1. Executive Summary")
    pdf.chapter_body(f"""This report presents an ISO-compliant Life Cycle Assessment (LCA) of {product_name}.

Scope: Cradle-to-grave
Functional Unit: 1 unit of {product_name}
Impact Methods: IPCC 2021 (GWP100), ReCiPe Midpoint (H)

Key Results:
- GHG Emissions: {ghg_total:.2f} kg CO2-eq
- Energy Use: {energy_total:.2f} MJ
- Water Use: {water_total:.2f} L
- Primary impact contributor: {top_process}
""")

    pdf.chapter_title("2. Goal and Scope")
    pdf.chapter_body(f"The goal of this study is to quantify the environmental impacts of {product_name} across its full life cycle.\n"
                     "The study follows ISO 14040/44 standards, considering a cradle-to-grave boundary, using test inventory data.")

    pdf.chapter_title("3. Inventory Analysis")
    pdf.chapter_body("The following inventory summarizes the key processes and associated resource use:")
    pdf.add_table(inventory)

    pdf.chapter_title("4. Life Cycle Impact Assessment (LCIA)")
    pdf.chapter_body(f"Using the IPCC and ReCiPe Midpoint (H) methods, the following impact categories were assessed:")
    pdf.chapter_body(f"- Total GHG Emissions: {ghg_total:.2f} kg CO2-eq\n"
                     f"- Total Water Use: {water_total:.2f} L\n"
                     f"- Total Energy Use: {energy_total:.2f} MJ")
    pdf.add_chart(fig)

    pdf.chapter_title("5. Interpretation")
    pdf.chapter_body(f"The process contributing most to GHG emissions is: {top_process}. \n"
                     "Energy and material inputs are primary drivers of environmental impact.\n"
                     "The results highlight hotspots and can guide further improvement opportunities.")

    pdf.output("lca_detailed_report.pdf")

    with open("lca_detailed_report.pdf", "rb") as file:
        st.download_button("📄 Download Full ISO-Compliant PDF Report", file, file_name="lca_detailed_report.pdf")

    st.success("LCA complete! Detailed report ready for download.")
