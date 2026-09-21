from user_auth.models import AgentActionLog

def log_agent_action(
    *,
    user,
    session_id: str = "",
    user_query: str = "",
    tool_name: str,
    operation: str = "",
    entity_type: str = "",
    entity_id: str = "",
    input_data: dict | None = None,
    output_data: dict | None = None,
    status: str = AgentActionLog.Status.SUCCESS,
    error_message: str = "",
) -> None:
    AgentActionLog.objects.create(
        user=user,
        session_id=session_id,
        user_query=user_query,
        tool_name=tool_name,
        operation=operation,
        entity_type=entity_type,
        entity_id=entity_id or None,
        input_data=input_data or {},
        output_data=output_data or {},
        status=status,
        error_message=error_message[:4000],
    )
