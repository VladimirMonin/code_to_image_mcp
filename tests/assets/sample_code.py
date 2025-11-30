"""
Тестовый Python модуль для проверки извлечения кода.

Содержит различные типы сущностей для тестирования AST экстрактора.
"""

from typing import List, Optional
from dataclasses import dataclass


# Простая функция
def calculate_sum(a: int, b: int) -> int:
    """Вычисляет сумму двух чисел."""
    return a + b


# Декорированная функция
def deprecated(func):
    """Декоратор для отметки устаревших функций."""

    def wrapper(*args, **kwargs):
        print(f"Warning: {func.__name__} is deprecated!")
        return func(*args, **kwargs)

    return wrapper


@deprecated
def old_function(x: str) -> str:
    """Устаревшая функция для примера."""
    return x.upper()


# Async функция
async def fetch_data(url: str) -> dict:
    """Асинхронная загрузка данных."""
    # Имитация async операции
    return {"url": url, "status": "ok"}


# Dataclass
@dataclass
class User:
    """Модель пользователя."""

    id: int
    name: str
    email: str
    is_active: bool = True

    def activate(self) -> None:
        """Активирует пользователя."""
        self.is_active = True

    def deactivate(self) -> None:
        """Деактивирует пользователя."""
        self.is_active = False


# Обычный класс с методами
class OrderService:
    """Сервис обработки заказов."""

    def __init__(self, db_connection):
        self.db = db_connection
        self.orders = []

    def create_order(self, user_id: int, items: List[dict]) -> dict:
        """
        Создаёт новый заказ.

        Args:
            user_id: ID пользователя
            items: Список товаров

        Returns:
            Информация о созданном заказе
        """
        order = {
            "id": len(self.orders) + 1,
            "user_id": user_id,
            "items": items,
            "status": "pending",
        }
        self.orders.append(order)
        return order

    @staticmethod
    def calculate_total(items: List[dict]) -> float:
        """Вычисляет общую стоимость."""
        return sum(item.get("price", 0) * item.get("quantity", 1) for item in items)

    @classmethod
    def from_config(cls, config: dict):
        """Создаёт сервис из конфигурации."""
        return cls(config.get("db_connection"))


# Вложенный класс
class PaymentProcessor:
    """Процессор платежей."""

    class PaymentError(Exception):
        """Ошибка обработки платежа."""

        pass

    def __init__(self, gateway: str):
        self.gateway = gateway

    async def process_payment(self, amount: float, card_token: str) -> bool:
        """Асинхронная обработка платежа."""
        if amount <= 0:
            raise self.PaymentError("Invalid amount")
        return True
