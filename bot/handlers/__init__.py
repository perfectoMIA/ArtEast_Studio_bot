# Этот файл объединяет все роутеры из модулей в один "главный" роутер, который потом подключается в main.py
from .handlers import router as main_router
from .fsm_handlers import router as fsm_router

routers = [main_router, fsm_router]

__all__ = ['routers']
