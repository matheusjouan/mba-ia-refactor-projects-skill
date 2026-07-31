import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-default")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
DB_PATH = os.environ.get("DB_PATH", "loja.db")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-only-admin-token")

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
