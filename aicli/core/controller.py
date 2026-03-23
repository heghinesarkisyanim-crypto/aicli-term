"""Controller — routes LLMResponse to the correct handler."""

from __future__ import annotations

from aicli.interfaces import (
    CommandRequest,
    Intent,
    LLMResponse,
    ScaffoldRequest,
)


def route(response: LLMResponse, dry_run: bool = False) -> CommandRequest | ScaffoldRequest | str | None:
    """Return the appropriate request object based on LLM intent.

    Returns:
        CommandRequest  — for os_command intent
        ScaffoldRequest — for scaffold intent
        str             — explanation text for info intent
        None            — for dangerous intent (caller shows warning)
    """
    match response.intent:
        case Intent.OS_COMMAND:
            return CommandRequest(
                commands=response.commands,
                explanation=response.explanation,
                is_dangerous=response.is_dangerous,
                requires_sudo=response.requires_sudo,
                affects_paths=response.affects_paths,
                dry_run=dry_run,
            )

        case Intent.SCAFFOLD:
            # First command holds the template name + project name
            parts = response.command.split(maxsplit=1)
            template = parts[0] if parts else ""
            project_name = parts[1] if len(parts) > 1 else "my_project"
            return ScaffoldRequest(
                template=template,
                project_name=project_name,
                target_dir=f"./{project_name}",
            )

        case Intent.INFO:
            return response.explanation

        case Intent.DANGEROUS:
            return None

        case _:
            return None
