from pydantic import BaseModel, Field

from app.domain.enums.recovery_action import RecoveryAction


class ToolCapability(BaseModel):
    """
    Declarative description of a recovery execution capability.

    This metadata describes what a tool can do.
    It does not grant permission to execute the tool.
    """

    name: str = Field(
        min_length=1,
    )

    description: str = Field(
        min_length=1,
    )

    supported_actions: list[RecoveryAction] = Field(
        min_length=1,
    )

    requires_policy_approval: bool = True

    is_mock: bool = True