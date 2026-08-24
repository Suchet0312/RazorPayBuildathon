from app.domain.enums.recovery_action import RecoveryAction
from app.domain.models.recovery import ExecutionRequest
from app.tools.alternate_method_tool import MockAlternateMethodTool
from app.tools.recovery_link_tool import MockRecoveryLinkTool
from app.tools.retry_tool import MockRetryTool


def make_request(
    action: RecoveryAction,
) -> ExecutionRequest:
    return ExecutionRequest(
        run_id="run_tool_001",
        payment_id="pay_tool_001",
        action=action,
        action_parameters={},
    )


def test_retry_tool_executes_retry_now():
    tool = MockRetryTool()

    result = tool.execute(
        make_request(
            RecoveryAction.RETRY_NOW,
        )
    )

    assert result.success is True

    assert result.action == (
        RecoveryAction.RETRY_NOW
    )

    assert (
        result.external_reference_id
        == "mock_retry_pay_tool_001"
    )


def test_retry_tool_executes_retry_later():
    tool = MockRetryTool()

    result = tool.execute(
        make_request(
            RecoveryAction.RETRY_LATER,
        )
    )

    assert result.success is True

    assert result.action == (
        RecoveryAction.RETRY_LATER
    )

    assert (
        result.external_reference_id
        == "mock_retry_pay_tool_001"
    )


def test_retry_tool_rejects_unsupported_action():
    tool = MockRetryTool()

    result = tool.execute(
        make_request(
            RecoveryAction.SEND_RECOVERY_LINK,
        )
    )

    assert result.success is False

    assert (
        result.error_code
        == "UNSUPPORTED_ACTION"
    )


def test_recovery_link_tool_executes():
    tool = MockRecoveryLinkTool()

    result = tool.execute(
        make_request(
            RecoveryAction.SEND_RECOVERY_LINK,
        )
    )

    assert result.success is True

    assert result.action == (
        RecoveryAction.SEND_RECOVERY_LINK
    )

    assert (
        result.external_reference_id
        == "mock_recovery_link_pay_tool_001"
    )


def test_recovery_link_tool_rejects_unsupported_action():
    tool = MockRecoveryLinkTool()

    result = tool.execute(
        make_request(
            RecoveryAction.RETRY_NOW,
        )
    )

    assert result.success is False

    assert (
        result.error_code
        == "UNSUPPORTED_ACTION"
    )


def test_alternate_method_tool_executes():
    tool = MockAlternateMethodTool()

    result = tool.execute(
        make_request(
            RecoveryAction.SUGGEST_ALTERNATE_METHOD,
        )
    )

    assert result.success is True

    assert result.action == (
        RecoveryAction.SUGGEST_ALTERNATE_METHOD
    )

    assert (
        result.external_reference_id
        == "mock_alternate_method_pay_tool_001"
    )


def test_alternate_method_tool_rejects_unsupported_action():
    tool = MockAlternateMethodTool()

    result = tool.execute(
        make_request(
            RecoveryAction.RETRY_NOW,
        )
    )

    assert result.success is False

    assert (
        result.error_code
        == "UNSUPPORTED_ACTION"
    )