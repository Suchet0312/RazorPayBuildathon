from app.domain.models.recovery import (
    ExecutionRequest,
    ExecutionResult,
)
from app.tools.registry import ToolRegistry


class RecoveryToolService:
    """
    Application service responsible for controlled recovery
    tool execution.

    This service provides a stable boundary between the workflow
    and concrete tool implementations.

    In the future, this boundary can be exposed through MCP tools
    without changing LangGraph orchestration logic.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ) -> None:
        self.registry = (
            registry
            if registry is not None
            else ToolRegistry()
        )

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Execute the tool registered for the requested recovery action.
        """

        tool = self.registry.get_tool(
            request.action,
        )

        if tool is None:
            return ExecutionResult(
                success=False,
                action=request.action,
                message=(
                    "No execution tool is registered for this "
                    "recovery action."
                ),
                error_code="TOOL_NOT_REGISTERED",
            )

        return tool.execute(
            request,
        )