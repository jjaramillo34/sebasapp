import os
import pandas as pd
import streamlit as st
import time
from datetime import datetime
#from streamlit_option_menu import option_menu
from streamlit_option_menu import option_menu
from database import *

# set page config and initial setup
st.set_page_config(page_title='Brakes YES', page_icon='🚀', layout='wide', initial_sidebar_state='auto')

# Initial setup
DATA_FILE = 'clients_data.csv'
columnas_clientes = ['Nombre', 'Apellido', 'Direccion', 'Telefono', 'Email', 'Cedula', 'Fecha de Registro']
columnas_productos = ['Nombre', 'Marca', 'Modelo', 'Precio', 'Cantidad', 'Fecha de Registro']
columnas_ventas = ['Cliente', 'Producto', 'Precio', 'Cantidad', 'Total', 'Fecha de Registro']
columnas_proveedores = ['Nombre', 'Direccion', 'Telefono', 'Email', 'Cedula', 'Fecha de Registro']

if not os.path.exists(DATA_FILE):
    clients_data = pd.DataFrame(columns=['Client Name', 'Client Email', 'Part Name', 'Price', 'Quantity', 'Total'])
    clients_data.to_csv(DATA_FILE, index=False)

# Load data
#@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(data):
    data.to_csv(DATA_FILE, index=False)
    
def generar_reporte(quantity, price, total):
    total = quantity * price
    tax = total * 0.12
    grand_total = total + tax
    
    summario = f"""
    ## Summario
    
    ## Quantity: {quantity}
    
    """
    

# Main app
def main():
    st.title('Auto Parts Sales Management')

    st.sidebar.title('Menu')
    menu = st.sidebar.radio('Select an option:', ['Sales', 'Clients'])

    if menu == 'Sales':
        st.header('New Sale')
        client_name = st.text_input('Client Name')
        client_email = st.text_input('Client Email')
        part_name = st.text_input('Part Name')
        price = st.number_input('Price', min_value=0.0, step=0.01)
        quantity = st.number_input('Quantity', min_value=1, step=1)

        if st.button('Submit Sale'):
            total = price * quantity
            new_data = pd.DataFrame({'Client Name': [client_name],
                                     'Client Email': [client_email],
                                     'Part Name': [part_name],
                                     'Price': [price],
                                     'Quantity': [quantity],
                                     'Total': [total]})
            clients_data = load_data()
            # append new data to existing data
            clients_data = clients_data.merge(new_data, how='outer')
            save_data(clients_data)
            st.success('Sale submitted successfully')

        st.header('Sales History')
        sales_data = load_data()
        st.write(sales_data)

    elif menu == 'Clients':
        st.header('Client List')
        clients_data = load_data()
        unique_clients = clients_data.drop_duplicates(subset='Client Email')
        st.write(unique_clients[['Client Name', 'Client Email']])
        
def inicio():
    st.title("Inicio de la aplicacion de ventas")
    st.subheader("Bienvenido a la aplicacion de ventas")
    cols = st.columns(4)
    # count clientes
    c = get_clientes()
    cols[0].metric(label="Clientes", value=len(list(c)))
    
    # count productos
    count_clientes = get_clientes()
    cols[1].metric(label="Productos", value=len(list(count_clientes)))
    
def productos():
    st.title("Inventario de Todos los productos")
    st.subheader("Aqui puedes ver todos los productos")
    options = st.sidebar.radio('Selecciona una opcion:', ['Crear Producto', 'Actualizar Producto', 'Eliminar Producto'])
    
    if options == 'Crear Producto':
        st.title("Crear un nuevo producto")
        cols = st.columns(2)
        with cols[0]:
            input_codigo = st.text_input("Codigo")
            input_aplicacion = st.text_input("Aplicacion")
            input_codigo_a = st.text_input("Codigo Alterno")
            input_marca = st.text_input("Marca")
            input_linea = st.text_input("Linea")
            input_familia = st.text_input("Familia")
            input_aux1 = st.text_input("Aux1")
            input_aux3 = st.text_input("Aux2")
            input_aux3_1 = st.text_input("Aux3")
        with cols[1]:
            input_stock = st.text_input("Stock")
            input_precio = st.text_input("Precio")
            
            # format prices 2 decimals
            precio_iva = float(input_precio) * 1.12
            # descuent 22%
            precio_22 = float(input_precio) - (float(input_precio) * 0.22)
            precio_24 = float(precio_iva) - (float(precio_iva) * 0.22)
            precio_almacen = float(precio_24) + (float(precio_iva)* 0.24)
            ganancia1 = float(precio_almacen)* 0.24
            precio_taller = float(precio_24) + (float(precio_iva)* 0.35)
            ganancia2 = float(precio_taller)* 0.35
            
            if input_precio:
                input_precio_iva = st.text_input("Precio IVA", value=format(precio_iva, '.2f'), disabled=True)
                input_precio_22 = st.text_input("Precio 22%", value=format(precio_22, '.2f'), disabled=True)
                input_precio_24 = st.text_input("Precio 24%", value=format(precio_24, '.2f'), disabled=True)
                input_precio_almacen = st.text_input("Precio Almacen", value=format(precio_almacen, '.2f'), disabled=True)
                input_ganancia1 = st.text_input("Ganancia 1", value=format(ganancia1, '.2f'), disabled=True)
                input_precio_taller = st.text_input("Precio Taller", format(precio_taller, '.2f'), disabled=True)
                input_ganancia2 = st.text_input("Ganancia 2", value=format(ganancia2, '.2f'), disabled=True)

            
    elif options == 'Actualizar Producto':
        productos = get_productos()
        productos_a = []
        productos_b = []
        
        #st.write(productos)
        for p in productos:
            productos_a.append(p['codigo'] + " - " + p['aplicacion'])
            productos_b.append((p['codigo'], p['aplicacion'], p['codigo_alterno'], p['marca'], 
                                p['linea'], p['familia'], p['aux1'], p['aux2'], p['aux3'], p['stock'], 
                                p['precio'], p['precio_iva'], p['precio_22'], p['precio_24'], p['precio_almacen'],
                                p['ganancia1'], p['precio_taller'], p['ganancia2']
                                ))
        
        producto_seleccionado = st.selectbox('Selecciona un producto', productos_a)
        
        with st.form(key='actualizar_producto', clear_on_submit=True):
            if producto_seleccionado:
                #if producto_seleccionado:
                cols = st.columns(2)
                with cols[0]:
                    input_codigo = st.text_input("Codigo", value=productos_b[productos_a.index(producto_seleccionado)][0], disabled=True)
                    input_aplicacion = st.text_input("Aplicacion", value=productos_b[productos_a.index(producto_seleccionado)][1])
                    input_codigo_a = st.text_input("Codigo Alterno", value=productos_b[productos_a.index(producto_seleccionado)][2])
                    input_marca = st.text_input("Marca", value=productos_b[productos_a.index(producto_seleccionado)][3])
                    input_linea = st.text_input("Linea", value=productos_b[productos_a.index(producto_seleccionado)][4])
                    input_familia = st.text_input("Familia", value=productos_b[productos_a.index(producto_seleccionado)][5])
                    input_aux1 = st.text_input("Aux1", value=productos_b[productos_a.index(producto_seleccionado)][6])
                    input_aux3 = st.text_input("Aux2", value=productos_b[productos_a.index(producto_seleccionado)][7])
                    input_aux3_1 = st.text_input("Aux3", value=productos_b[productos_a.index(producto_seleccionado)][8])
                with cols[1]:
                    input_stock = st.text_input("Stock", value=productos_b[productos_a.index(producto_seleccionado)][9])
                    input_precio = st.text_input("Precio", value=productos_b[productos_a.index(producto_seleccionado)][10])
                    precio_iva = float(input_precio) * 1.12
                    # descuent 22%
                    precio_22 = float(input_precio) - (float(input_precio) * 0.22)
                    precio_24 = float(precio_iva) - (float(precio_iva) * 0.22)
                    precio_almacen = float(precio_24) + (float(precio_iva)* 0.24)
                    ganancia1 = float(precio_almacen)* 0.24
                    precio_taller = float(precio_24) + (float(precio_iva)* 0.35)
                    ganancia2 = float(precio_taller)* 0.35
                    input_precio_iva = st.text_input("Precio IVA", value=format(precio_iva, '.2f'), disabled=True)
                    input_precio_22 = st.text_input("Precio 22%", value=format(precio_22, '.2f'), disabled=True)
                    input_precio_24 = st.text_input("Precio 24%", value=format(precio_24, '.2f'), disabled=True)
                    input_precio_almacen = st.text_input("Precio Almacen", value=format(precio_almacen, '.2f'), disabled=True)
                    input_ganancia1 = st.text_input("Ganancia 1", value=format(ganancia1, '.2f'), disabled=True)
                    input_precio_taller = st.text_input("Precio Taller", format(precio_taller, '.2f'), disabled=True)
                    input_ganancia2 = st.text_input("Ganancia 2", value=format(ganancia2, '.2f'), disabled=True)
                    
                    date_updated = datetime.now()
            submit_button = st.form_submit_button(label='Actualizar Producto')
            if submit_button:
                update_producto_by_codigo(
                    input_codigo,
                    {
                        'aplicacion': input_aplicacion,
                        'codigo_alterno': input_codigo_a,
                        'marca': input_marca,
                        'linea': input_linea,
                        'familia': input_familia,
                        'aux1': input_aux1,
                        'aux2': input_aux3,
                        'aux3': input_aux3_1,
                        'stock': input_stock,
                        'precio': input_precio,
                        'precio_iva': input_precio_iva,
                        'precio_22': input_precio_22,
                        'precio_24': input_precio_24,
                        'precio_almacen': input_precio_almacen,
                        'ganancia1': input_ganancia1,
                        'precio_taller': input_precio_taller,
                        'ganancia2': input_ganancia2,
                        'date_updated': date_updated,
                        'usario_updated': 'Sebastian',
                    }
                )
                st.success('Producto actualizado exitosamente')
    elif "Eliminar producto":
        st.title("Eliminar Producto")
        st.subheader("Bienvenido a la seccion de eliminar productos")
        producto = get_productos()
        
def ventas():
    cliente_a = []
    clientes_doc = {}
    st.title("Ventas")
    st.subheader("Bienvenido a la seccion de ventas")
    cliente = get_clientes()
    
    # array de productos
    sales = [
        {"producto": "Producto 1","nombre": "Name of producto 1", "precio": 10, "cantidad": 1},
        {"producto": "Producto 2","nombre": "Name of producto 2", "precio": 11, "cantidad": 2},
        {"producto": "Producto 3","nombre": "Name of producto 3", "precio": 12, "cantidad": 3},
        {"producto": "Producto 4","nombre": "Name of producto 4", "precio": 13, "cantidad": 4},
        {"producto": "Producto 5","nombre": "Name of producto 5", "precio": 14, "cantidad": 5},
        {"producto": "Producto 6","nombre": "Name of producto 6", "precio": 15, "cantidad": 6},
        {"producto": "Producto 7","nombre": "Name of producto 7", "precio": 16, "cantidad": 7},
        {"producto": "Producto 8","nombre": "Name of producto 8", "precio": 17, "cantidad": 8},
        {"producto": "Producto 9","nombre": "Name of producto 9", "precio": 18, "cantidad": 9},
        {"producto": "Producto 10","nombre": "Name of producto 10", "precio": 19, "cantidad": 10}
    ]
    # array de productos
    for c in cliente:
        cliente_a.append(c['cedula'])
        clientes_doc[c['cedula']] = c
        
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Datos del cliente")
        cliente_seleccionado = st.multiselect('Selecciona un cliente', cliente_a, default=cliente_a[0])
        if cliente_seleccionado:
            nombre = clientes_doc[cliente_seleccionado[0]]['nombre']
            apellido = clientes_doc[cliente_seleccionado[0]]['apellido']
            cedula = clientes_doc[cliente_seleccionado[0]]['cedula']
            
            input_nombre = st.text_input('Nombre', value=nombre)
            input_apellido = st.text_input('Apellido', value=apellido)
            input_cedula = st.text_input('Cedula', value=cedula)
            input_rating = st.number_input('Rating', min_value=0.0, max_value=5.0, step=0.1)
    with cols[1]:
        st.subheader("Datos de la venta")
        producto = st.multiselect('Selecciona un producto', [s['producto'] for s in sales], default=sales[0]['producto'])
        total = 0
        if len(producto) > 5:
            num_cols = len(producto) // 5 + 1
            for i in range(num_cols):
                cols = st.columns(5)
                for j in range(5):
                    if i*5+j < len(producto):
                        cantidad = cols[j].number_input(f"Cantidad: {producto[i*5+j]}", min_value=0, step=1, key=f"cantidad_{producto[i*5+j]}")
                        precio = sales[i*5+j]['precio'] * cantidad
                        precio_iva = precio * 1.12
                        # multiplicar por el precio
                        cols[j].write(precio)
                        total += precio_iva
            st.write(total)
                    
        else:
            for p in range(len(producto)):
                cantidad = st.number_input(f"Cantidad: {p}", min_value=0, step=1, key=f"cantidad_{p}")
                precio = sales[p]['precio'] * cantidad
                precio_iva = precio * 1.12
                total += precio_iva
            st.write(total)
        
    st.write('----')
    if st.button('Submit Sale'):
        with st.spinner('Submitting sale...'):
            time.sleep(2)
            with st.container():
                st.markdown(f"# Sumario de la venta")
                st.markdown(f"### Detalles del cliente")
                st.markdown(f"- Numero de orden: 1234")
                st.markdown(f"- Nombre: {input_nombre}")
                st.markdown(f"- Apellido: {input_apellido}")
                st.markdown(f"- Cedula: {input_cedula}")
                st.markdown(f"- Rating: {input_rating}")
                st.markdown(f"### Detalles de la venta")
                st.markdown("""| Producto | Cantidad | Precio | Precio con IVA |""")
                st.markdown("""| -------- | -------- | ------ | -------------- |""")
                for p in producto:
                    st.markdown(f"""| {p} | {cantidad} | {precio} | {precio_iva} |""")
                st.markdown(f"""| **Total**   |        |       | **{round(total)}** |""")
                text1 = f"""
                    ## Informacion del cliente
                    - Nombre: {input_nombre}
                    - Apellido: {input_apellido}
                    - Cedula: {input_cedula}
                    - Rating: {input_rating}
                    - Numero de orden: 1234
                """
                
                text_item = ""
                
                for p in producto:
                    text_item += f"""
                    ## Informacion del producto
                    - Producto: {p}
                    - Cantidad: {cantidad}
                    - Precio: {precio}
                    - Precio con IVA: {precio_iva}
                    """
                
                text = f"""
                    ## Order Details
                    | Item        | Price |
                    | ----------- | ----- |
                    {text_item}

                    Total: $45

                    ## Payment Information
                    - Payment Method: Credit Card
                    - Card Number: **** **** **** 1234
                    - Expiration Date: 05/24
                """
                markdown_text = text1 + text
                st.markdown(f"""
                <div style="background-color:#F5F5F5; border-radius:10px; padding: 10px">
                {markdown_text}
                
                </div>
                
                
                
    """, unsafe_allow_html=True)
        
    
        
def home():
    st.title('Chequear si el cliente existe')
        
    with st.form(key='buscar_form', clear_on_submit=True):
        cedula = st.text_input('Cedula')
        find_cliente = get_cliente_cedula(cedula)
        submit_button = st.form_submit_button(label='Buscar cliente')
        if find_cliente:
            #st.success('Cliente encontrado')
            st.success(f"Nombre: {find_cliente['nombre']}, Apellido: {find_cliente['apellido']}, Cedula: {find_cliente['cedula']}")        
        else:
            st.error('Cliente no encontrado')
            
    #cliente_seleccionado = st.selectbox('Selecciona un cliente', clientes_array)
        
    st.write('----')
    st.title('Ingresa un nuevo cliente')
    with st.form(key='my_form', clear_on_submit=True):
        nombre = st.text_input('Nombre')
        apellido = st.text_input('Apellido')
        cedula = st.text_input('Cedula')
        submit_button = st.form_submit_button(label='Submit')
        if submit_button:
            st.write('Nombre: ', nombre)
            st.write('Apellido: ', apellido)
            st.write('Cedula: ', cedula)
            st.write('Guardando en la base de datos')
            cliente = {
                'nombre': nombre,
                'apellido': apellido,
                'cedula': cedula,
                'rating': 5
            }
            insert_cliente(cliente)
            st.success('Cliente guardado con exito')
    time.sleep(1)
    clientes = get_clientes()
    for cliente in clientes:
        st.write(cliente)
        

if __name__ == '__main__':
    # 1. as sidebar menu
    menu_items = ['Inicio', 'Clientes', 'Ventas', 'Productos', 'Proveedores', 'Reportes', 'Configuracion']
    menu_icons = ['app', 'app', 'cart', 'cubes', 'truck', 'file-text', 'gear']
    with st.sidebar:
        selected = option_menu("Brakes YES", menu_items,
            icons=menu_icons, menu_icon="cast", default_index=1)
    if selected == "Inicio":
        inicio()
    elif selected == "Productos":
        productos()
    elif selected == "Ventas":
        ventas()
    elif selected == "Clientes":
        home()
    elif selected == "Settings":
        main()
