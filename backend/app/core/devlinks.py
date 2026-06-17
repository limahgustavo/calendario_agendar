import logging

from app.core.config import settings

logger = logging.getLogger("devlinks")


def log_link(kind: str, email: str, link: str, delivered: bool) -> None:
    """Em DEBUG (ou quando o email falhou), imprime o link mágico no console
    para permitir testar o fluxo sem depender de entrega de email."""
    if settings.DEBUG or not delivered:
        logger.warning("🔗 [%s] link para %s → %s", kind, email, link)
