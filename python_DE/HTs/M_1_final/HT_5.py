import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import ClassVar, TypeAlias
import matplotlib.pyplot as plt


MoneyInput: TypeAlias = Decimal | int | float | str


class AccountType(str, Enum):
    """Типы банковских счетов.
    checking — расчётный счёт;
    savings — сберегательный счёт."""
    CHECKING = "checking"
    SAVINGS = "savings"


class OperationType(str, Enum):
    """Типы операций, записываемых в историю счёта.
    deposit — пополнение счёта;
    withdraw — снятие средств;
    interest — начисление процентов (для сберегательного счёта)."""
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    INTEREST = "interest"


class OperationStatus(str, Enum):
    """Результат выполнения операции."""
    SUCCESS = "success"
    FAIL = "fail"


@dataclass(frozen=True)
class Operation:
    """Неизменяемая запись об операции."""
    operation_type: OperationType
    amount: Decimal
    tstamp: datetime
    balance_after: Decimal
    status: OperationStatus

    def __str__(self) -> str:
        return (
            f"{self.tstamp:%Y-%m-%d %H:%M:%S} | "
            f"{self.operation_type.value:8} | сумма: {self.amount} | "
            f"баланс: {self.balance_after} | {self.status.value}"
        )


class BankAccount:
    """Общие данные и поведение банковских счетов.
    Атрибуты:
        _next_number — следующий номер счёта.
        account_type — тип счёта (определяется в подклассах).
    """

    NAME_PATTERN = re.compile(
        r"(?:[A-Z][a-z]*\s+[A-Z][a-z]*|[А-ЯЁ][а-яё]*\s+[А-ЯЁ][а-яё]*)"
    )

    _next_number: ClassVar[int] = 1000
    account_type: AccountType

    @staticmethod
    def _to_decimal(value: MoneyInput, field_name: str) -> Decimal:
        """Преобразует значение в конечный Decimal, исключая bool."""
        if isinstance(value, bool):
            raise ValueError(f"{field_name} должно быть числом.")

        try:
            result = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(
                f"Некорректное значение: {field_name.lower()}."
            ) from None

        if not result.is_finite():
            raise ValueError(f"{field_name} должно быть конечным числом.")

        return result

    @classmethod
    def _money(cls, value: MoneyInput, *,
               must_be_positive: bool = False) -> Decimal:
        """Проверяет и преобразует сумму в Decimal."""
        amount = cls._to_decimal(value, "Сумма")

        if must_be_positive and amount <= 0:
            raise ValueError("Сумма операции должна быть положительной.")

        return amount

    def __init__(self, owner: str, initial_balance: MoneyInput = 0) -> None:
        """Инициализация банковского счёта.
        Записывает имя владельца, начальный баланс
        и создаёт пустую историю операций."""
        if type(self) is BankAccount:
            raise TypeError("Создавайте CheckingAccount или SavingsAccount.")

        if not isinstance(owner, str):
            raise ValueError("Имя владельца должно быть строкой.")

        normalized_owner = owner.strip()
        if not self.NAME_PATTERN.fullmatch(normalized_owner):
            raise ValueError("Имя должно быть в формате «Имя Фамилия»,\n"
                             "с заглавных букв, только кириллицей/латиницей.")

        balance = self._money(initial_balance)
        if balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным.")

        self._owner: str = normalized_owner
        self._balance: Decimal = balance
        self._history: list[Operation] = []

        self._account_number: str = f"ACC-{BankAccount._next_number:04d}"
        BankAccount._next_number += 1

    @property
    def owner(self) -> str:
        """Возвращает имя владельца счёта."""
        return self._owner

    @property
    def account_number(self) -> str:
        """Возвращает номер счёта."""
        return self._account_number

    @property
    def balance(self) -> Decimal:
        """Возвращает текущий баланс счёта."""
        return self._balance

    def get_balance(self) -> Decimal:
        """Возвращает текущий баланс счёта.
        Метод для совместимости с интерфейсом."""
        return self._balance

    def _record_operation(self, operation_type: OperationType,
                          amount: Decimal,
                          status: OperationStatus) -> Operation:
        """Записывает операцию в историю, возвращает Operation."""
        operation = Operation(
            operation_type=operation_type,
            amount=amount,
            tstamp=datetime.now().astimezone(),
            balance_after=self._balance,
            status=status,
        )
        self._history.append(operation)
        return operation

    def deposit(self, amount: MoneyInput) -> Operation:
        """Пополнение счёта. Сумма должна быть положительной."""
        amount = self._money(amount, must_be_positive=True)
        self._balance += amount
        return self._record_operation(
            OperationType.DEPOSIT,
            amount,
            OperationStatus.SUCCESS,
        )

    def withdraw(self, amount: MoneyInput) -> Operation:
        """Обычное снятие средств.
        Если средств недостаточно, операция не выполняется."""
        amount = self._money(amount, must_be_positive=True)

        if amount > self._balance:
            return self._record_operation(
                OperationType.WITHDRAW,
                amount,
                OperationStatus.FAIL,
            )

        self._balance -= amount
        return self._record_operation(
            OperationType.WITHDRAW,
            amount,
            OperationStatus.SUCCESS,
        )

    def get_history(self) -> tuple[Operation, ...]:
        """Возвращает историю как неизменяемый кортеж."""
        return tuple(self._history)

    def format_history(self) -> str:
        """Возвращает историю операций в виде строки."""
        if not self._history:
            return "История операций пуста."
        return "\n".join(str(operation) for operation in self._history)

    def get_large_successful_operations(
            self,
            n: int,
            threshold: MoneyInput) -> tuple[Operation, ...]:
        """Возвращает последние N операций с суммой не меньше threshold."""
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            raise ValueError("N должно быть положительным целым числом.")

        minimum_amount = self._money(threshold, must_be_positive=True)
        matching_operations = [
            operation
            for operation in self._history
            if (
                operation.status is OperationStatus.SUCCESS
                and operation.amount >= minimum_amount
            )
        ]
        return tuple(matching_operations[-n:])

    def plot_balance_history(self) -> None:
        """Строит график баланса по времени и истории операций."""
        if not self._history:
            print("История операций пуста.")
            return

        tstamps = [operation.tstamp for operation in self._history]
        balances = [float(operation.balance_after)
                    for operation in self._history]

        plt.figure(figsize=(10, 5))
        plt.plot(tstamps, balances, marker="o", linestyle="-")
        plt.title(
            f"История баланса счёта {self.account_number} "
            f"({self.account_type.value})"
        )
        plt.xlabel("Время операции")
        plt.ylabel("Баланс после операции")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()


class CheckingAccount(BankAccount):
    """Расчётный счёт: использует обычные правила базового класса."""
    account_type = AccountType.CHECKING


class SavingsAccount(BankAccount):
    """Сберегательный счёт: разрешено снимать не более 50% баланса."""
    account_type = AccountType.SAVINGS

    def withdraw(self, amount: MoneyInput) -> Operation:
        amount = self._money(amount, must_be_positive=True)
        maximum_withdrawal = self._balance / Decimal("2")

        if amount > maximum_withdrawal:
            return self._record_operation(
                OperationType.WITHDRAW,
                amount,
                OperationStatus.FAIL,
            )

        self._balance -= amount
        return self._record_operation(
            OperationType.WITHDRAW,
            amount,
            OperationStatus.SUCCESS,
        )

    def accrue_interest(self, rate: MoneyInput) -> Operation | None:
        """Начисляет проценты;
        rate задаётся в процентах.
        Если начисление равно нулю, операция не записывается.
        """
        rate_value = self._to_decimal(rate, "Ставка")
        if rate_value < 0:
            raise ValueError("Ставка не может быть отрицательной.")

        interest_amount = self._balance * rate_value / Decimal("100")

        if interest_amount == 0:
            return None

        self._balance += interest_amount
        return self._record_operation(
            OperationType.INTEREST,
            interest_amount,
            OperationStatus.SUCCESS,
        )
