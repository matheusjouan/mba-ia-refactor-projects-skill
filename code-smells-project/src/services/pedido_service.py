from models import pedido_model, produto_model
from services import notification_service


class PedidoError(Exception):
    """Erro de regra de negócio ao processar um pedido."""


def criar_pedido(usuario_id, itens):
    total = 0
    produtos_por_id = {}

    for item in itens:
        produto = produto_model.get_por_id(item["produto_id"])
        if produto is None:
            raise PedidoError(f"Produto {item['produto_id']} não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise PedidoError(f"Estoque insuficiente para {produto['nome']}")
        total += produto["preco"] * item["quantidade"]
        produtos_por_id[item["produto_id"]] = produto

    pedido_id = pedido_model.criar(usuario_id, total)

    for item in itens:
        produto = produtos_por_id[item["produto_id"]]
        pedido_model.adicionar_item(pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
        produto_model.decrementar_estoque(item["produto_id"], item["quantidade"])

    notification_service.notificar_pedido_criado(usuario_id, pedido_id)
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_status_atualizado(pedido_id, novo_status)
