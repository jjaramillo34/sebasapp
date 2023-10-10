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
    st.markdown("""
        <style>
        div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 5% 5% 5% 10%;
        border-radius: 5px;
        color: rgb(30, 103, 119);
        overflow-wrap: break-word;
        }

        /* breakline for metric text         */
        div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
        overflow-wrap: break-word;
        white-space: break-spaces;
        color: red;
        }
        </style>
        """
        , unsafe_allow_html=True)
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
            input_precio = st.text_input("Precio", value="0.00")
            
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
    
    productos = get_productos()
    sales = []
    doc_sales = {}
    # array de productos
    
    for p in productos:
        doc_sales['producto'] = p['codigo']
        doc_sales['nombre'] = p['aplicacion']
        doc_sales['precio'] = float(p['precio'])
        doc_sales['cantidad'] = p['stock']
        if int(p['stock']) > 0:
            sales.append(doc_sales)
            doc_sales = {}
        
    #st.write(sales)
        
    # array de productos
    for c in cliente:
        cliente_a.append(c['cedula'])
        clientes_doc[c['cedula']] = c
    st.subheader("Datos del cliente")
    cliente_seleccionado = st.multiselect('Selecciona un cliente', cliente_a, default=cliente_a[0])
    cliente_descuento = st.sidebar.checkbox('Aplicar descuento')
    cliente_taller_almacen = st.sidebar.radio('Tipo de cliente', ('Taller', 'Almacen'))
    cols = st.columns(2)
    
    with cols[0]:
        if cliente_seleccionado:
            nombre = clientes_doc[cliente_seleccionado[0]]['nombre']
            apellido = clientes_doc[cliente_seleccionado[0]]['apellido']
            cedula = clientes_doc[cliente_seleccionado[0]]['cedula']
            
            input_nombre = st.text_input('Nombre', value=nombre)
            input_apellido = st.text_input('Apellido', value=apellido)
            input_cedula = st.text_input('Cedula', value=cedula)
            
    with cols[1]:
        telefono = clientes_doc[cliente_seleccionado[0]]['telefono']
        direcion = clientes_doc[cliente_seleccionado[0]]['direccion']
        input_telefono = st.text_input('Telefono', value=telefono)
        input_direccion = st.text_area('Direccion', value=direcion, height=130)
    st.write('---')
    cols = st.columns(1)
    sales_data = []
    with cols[0]:
        st.subheader("Datos de la venta")
        producto = st.multiselect('Selecciona un producto', [s['producto'] for s in sales])
        
        #productos = get_productos()
        
        #st.write('----')
        #st.write(productos)
        
        
        total = 0
        if len(producto) > 4:
            num_cols = len(producto) // 4 + 1
            for i in range(num_cols):
                cols = st.columns(4)
                for j in range(4):
                    if i*5+j < len(producto):
                        cantidad = cols[j].number_input(f"{sales[i*4+j]['nombre']}", min_value=0, step=1, key=f"cantidad_{producto[i*4+j]}")
                        precio = float(sales[i*4+j]['precio']) * cantidad
                        precio_iva = float(precio) * 1.12
                        # multiplicar por el precio
                        cols[j].write(precio)
                        total += precio_iva
            st.write(format(total, '.2f'))
                    
        else:
            cols = st.columns(2)
            for p in range(len(producto)):
                with cols[0]:
                    cantidad = st.number_input(f"No. {p+1} Nombre del producto: {sales[p]['nombre']}", min_value=0, step=1, key=f"cantidad_{producto[p]}")
                with cols[1]:
                    descuento = st.number_input(f"Descuento", min_value=0, step=1, key=f"descuento_{producto[p]}")
                #descuento = st.number_input(f"Descuento", min_value=0, step=1, key=f"descuento_{producto[p]}")
                precio = sales[p]['precio'] * cantidad
                precio_iva = precio * 1.12
                total += precio_iva
                sales_data.append({
                    'producto': producto[p],
                    'cantidad': cantidad,
                })
            st.write(format(total, '.2f'))
            
    st.write('----')
    if st.button('Enviar venta'):
        with st.spinner('Enviando venta...'):
            time.sleep(2)
            st.success('Venta enviada con exito')
            #st.write(sales_data)
            for sale in sales_data:
                st.write(sale)
                cantidad_now = sales[p]['cantidad'] - sale['cantidad']
                
#            with st.container():
#                st.markdown(f"# Sumario de la venta")
#                st.markdown(f"### Detalles del cliente")
#                st.markdown(f"- Numero de orden: 1234")
#                st.markdown(f"- Nombre: {input_nombre}")
#                st.markdown(f"- Apellido: {input_apellido}")
#                st.markdown(f"- Cedula: {input_cedula}")
#                st.markdown(f"- Rating: {input_rating}")
#                st.markdown(f"### Detalles de la venta")
#                st.markdown("""| Producto | Cantidad | Precio | Precio con IVA |""")
#                st.markdown("""| -------- | -------- | ------ | -------------- |""")
#                for p in producto:
#                    st.markdown(f"""| {p} | {cantidad} | {precio} | {precio_iva} |""")
#                st.markdown(f"""| **Total**   |        |       | **{round(total)}** |""")
#                text1 = f"""
#                    ## Informacion del cliente
#                    - Nombre: {input_nombre}
#                    - Apellido: {input_apellido}
#                    - Cedula: {input_cedula}
#                    - Rating: {input_rating}
#                    - Numero de orden: 1234
#                """
#                
#                text_item = ""
#                
#                for p in producto:
#                    text_item += f"""
#                    ## Informacion del producto
#                    - Producto: {p}
#                    - Cantidad: {cantidad}
#                    - Precio: {precio}
#                    - Precio con IVA: {precio_iva}
#                    """
#                
#                text = f"""
#                    ## Order Details
#                    | Item        | Price |
#                    | ----------- | ----- |
#                    {text_item}
#
#                    Total: $45
#
#                    ## Payment Information
#                    - Payment Method: Credit Card
#                    - Card Number: **** **** **** 1234
#                    - Expiration Date: 05/24
#                """
#                markdown_text = text1 + text
#                st.markdown(f"""
#                <div style="background-color:#F5F5F5; border-radius:10px; padding: 10px">
#                {markdown_text}
#                </div>
#    """, unsafe_allow_html=True)

def home():
    opcion = st.sidebar.radio('Selecciona una opcion', ['Crear Cliente', 'Actualizar Cliente'])
    
    if opcion == 'Crear Cliente':
        st.write('Crear Cliente')
        
        with st.form(key='buscar_form', clear_on_submit=True):
            st.title('Chequear si el cliente existe')
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
            nombre = st.text_input('Nombres', placeholder='Juan Pedro')
            apellido = st.text_input('Apellidos', placeholder='Perez Perez')
            cedula = st.text_input('Cedula', placeholder='1234567890')
            telefono = st.text_input('Telefono', placeholder='0999999999')
            direccion = st.text_area('Direccion', placeholder='Av. 6 de Diciembre N34-56 y Av. Eloy Alfaro', height=100)
            date_created = datetime.now()
            
            submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                st.markdown('---')
                st.markdown(f'### Nombres: {nombre}')
                st.markdown(f'### Apellidos: {apellido}')
                st.markdown(f'### Cedula: {cedula}')
                st.markdown(f'### Telefono: {telefono}')
                st.markdown(f'### Direccion: {direccion}')
                cliente = {
                    'nombre': nombre,
                    'apellido': apellido,
                    'cedula': cedula,
                    'telefono': telefono,
                    'direccion': direccion,
                    'date_created': date_created,
                    
                }
                insert_cliente(cliente)
                st.success('Cliente guardado con exito')
        time.sleep(1)
        
    elif  opcion == 'Actualizar Cliente':
        st.title('Actualizar Cliente')
        clientes = get_clientes()
        clientes_a = []
        clientes_all = []
        for cliente in clientes:
            clientes_a.append(cliente['cedula'])
            clientes_all.append((cliente['cedula'], cliente['nombre'], cliente['apellido'], cliente['cedula'], cliente['telefono'], cliente['direccion'], cliente['date_created']))
            
        cliente_seleccionado = st.selectbox('Selecciona un cliente', clientes_a)
        with st.form(key='actualizar_cliente', clear_on_submit=True):
            if cliente_seleccionado:
                cols = st.columns(2)
                with cols[0]:
                    input_nombre = st.text_input('Nombres', clientes_all[clientes_a.index(cliente_seleccionado)][1])
                    input_apellido = st.text_input('Apellidos', clientes_all[clientes_a.index(cliente_seleccionado)][2])
                    input_cedula = st.text_input('Cedula', clientes_all[clientes_a.index(cliente_seleccionado)][3])
                with cols[1]:
                    input_telefono = st.text_input('Telefono', clientes_all[clientes_a.index(cliente_seleccionado)][4])
                    input_direccion = st.text_area('Direccion', clientes_all[clientes_a.index(cliente_seleccionado)][5], height=100)
            submit_button = st.form_submit_button(label='Actualizar')
            if submit_button:
                data = {
                    "nombre": input_nombre,
                    "apellido": input_apellido,
                    "cedula": input_cedula,
                    "telefono": input_telefono,
                    "direccion": input_direccion,
                    "date_updated": datetime.now(),
                    "user_updated": "admin"
                }
                
                update_cliente_by_cedula(cliente_seleccionado, data)
                    
                st.success('Cliente actualizado con exito')
                
        
    # show all clientes in dataframe
    df_columns = ['nombre', 'apellido', 'cedula', 'telefono', 'direccion', 'date_created']
    
    clientes = get_clientes()
    df = pd.DataFrame(clientes, columns=df_columns)
    sorted_df = df.sort_values(by=['date_created'], ascending=False)
    st.dataframe(sorted_df.head(10), use_container_width=True)
    
    
        
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
