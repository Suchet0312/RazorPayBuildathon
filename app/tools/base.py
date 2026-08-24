from typing import Protocol

from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)


class RecoveryTool(Protocol):
    """
    Contract for a controlled recovery execution capability.

    Tools provide capability only.
    They do not evaluate policy or decide whether an action is allowed.
    """

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        ...