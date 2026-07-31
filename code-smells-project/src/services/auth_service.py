from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario_model


def hash_senha(senha):
    return generate_password_hash(senha)


def autenticar(email, senha):
    usuario = usuario_model.get_por_email(email)
    if usuario and check_password_hash(usuario["senha"], senha):
        return usuario
    return None
