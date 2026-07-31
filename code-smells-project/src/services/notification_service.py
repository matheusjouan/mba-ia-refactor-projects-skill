import logging

logger = logging.getLogger("loja.notifications")


def notificar_pedido_criado(usuario_id, pedido_id):
    logger.info("Notificação (email/SMS/push): pedido %s criado para usuário %s", pedido_id, usuario_id)


def notificar_status_atualizado(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("Notificação: pedido %s aprovado, preparar envio", pedido_id)
    elif novo_status == "cancelado":
        logger.info("Notificação: pedido %s cancelado, devolver estoque", pedido_id)
