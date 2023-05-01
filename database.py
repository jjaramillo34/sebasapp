from bson import ObjectId
from pymongo import MongoClient
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.environ.get('MONGO_URI')
print(mongo_uri)

client = MongoClient(mongo_uri)
db = client['clientes_database']
clientes = db['clientes']
productos = db['productos']

def get_clientes():
    return clientes.find()

#get cliente by cedula
def get_cliente_cedula(cedula: str):
    return clientes.find_one({'cedula': cedula})
    
def get_cliente(id: str):
    cliente = clientes.find_one({'_id': ObjectId(id)})
    cliente['_id'] = str(cliente['_id'])
    
def insert_cliente(cliente):
    return clientes.insert_one(cliente)

def update_cliente(id: str, cliente):
    return clientes.update_one({'_id': ObjectId(id)}, {'$set': cliente})

def update_cliente_by_cedula(cedula: str, cliente):
    return clientes.update_one({'cedula': cedula}, {'$set': cliente})

def delete_cliente(id: str):
    return clientes.delete_one({'_id': ObjectId(id)})

def get_productos():
    return productos.find()

def insert_producto(producto):
    return productos.insert_one(producto)

def get_producto(id: str):
    producto = productos.find_one({'_id': ObjectId(id)})
    producto['_id'] = str(producto['_id'])
    return producto

def get_producto_codigo(codigo: str):
    return productos.find_one({'codigo': codigo})

def get_producto_nombre(nombre: str):
    return productos.find_one({'nombre': nombre})

def update_producto_by_codigo(codigo: str, producto):
    return productos.update_one({'codigo': codigo}, {'$set': producto})

#df = pd.read_csv('productos_sebas.csv')
#data = df.to_dict('records')
#productos.insert_many(data)

#update_producto_by_codigo('0001', {'nombre': 'Coca Cola', 'precio': 2000, 'cantidad': 100})

