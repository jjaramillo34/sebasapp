import streamlit as st
import json
from typing import List

# Load invoice data from JSON file
with open('invoice_data.json', 'r', encoding='utf-8') as json_file:
    invoice_data = json.load(json_file)

# Function to calculate the total cost
def calculate_total(items: List[dict]) -> float:
    total = 0
    for item in items:
        total += item['quantity'] * item['price']
    return total

# Streamlit app
st.title('Generador de Facturas')

# Company and client info
st.write(f"**Empresa:** {invoice_data['company_name']}")
st.write(f"**Cliente:** {invoice_data['client_name']}")

# Invoice table
st.write("**Productos:**")
st.write("| Producto | Cantidad | Precio |")
st.write("| --- | --- | --- |")
for item in invoice_data['items']:
    st.write(f"| {item['product']} | {item['quantity']} | ${item['price']} |")

# Calculate subtotal and total
subtotal = calculate_total(invoice_data['items'])
tax_rate = invoice_data['tax_rate']
tax = subtotal * tax_rate
total = subtotal + tax

# Display totals
st.write(f"**Subtotal:** ${subtotal:.2f}")
st.write(f"**IVA ({tax_rate*100}%):** ${tax:.2f}")
st.write(f"**Total:** ${total:.2f}")

# Download button for the invoice as HTML
st.write("\n\n")
st.markdown('<a href="" download="invoice.html">Descargar Factura en HTML</a>', unsafe_allow_html=True)
