from .graph import graph


def chat_llm(content: str, thread_id: str):
    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )
    message = result["messages"][-1]
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(text)
            elif hasattr(item, "text") and item.text:
                parts.append(item.text)
        if parts:
            return "".join(parts)
    return str(content[0]['text'])
