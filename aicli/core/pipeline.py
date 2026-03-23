"""Pipeline — orchestrates the full request lifecycle."""

from __future__ import annotations

from aicli.automation.scaffolder import Scaffolder
from aicli.core.controller import route
from aicli.core.executor import Executor
from aicli.core.input_handler import parse_input
from aicli.core.session import SessionManager
from aicli.interfaces import (
    CommandRequest,
    ExecutionResult,
    LLMResponse,
    ScaffoldRequest,
)
from aicli.llm.engine import LLMEngine
from aicli.security.shield import SecurityShield
from aicli.ui import display


class Pipeline:
    def __init__(
        self,
        engine: LLMEngine,
        executor: Executor,
        scaffolder: Scaffolder,
        session: SessionManager,
        shield: SecurityShield,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        self._engine = engine
        self._executor = executor
        self._scaffolder = scaffolder
        self._session = session
        self._shield = shield
        self._dry_run = dry_run
        self._verbose = verbose

    def run(self, raw_input: str) -> None:
        """Execute the full pipeline for one user request."""
        parsed = parse_input(raw_input)

        context = self._session.get_context()
        try:
            llm_response: LLMResponse = self._engine.process(
                parsed.text, parsed.language.value, context
            )
        except RuntimeError as exc:
            display.error(str(exc))
            return

        if self._verbose:
            display.debug(llm_response)

        display.command_preview(llm_response)

        routed = route(llm_response, dry_run=self._dry_run)

        if routed is None:
            display.dangerous_warning(llm_response.explanation)
            self._session.add_entry(raw_input, llm_response.explanation, "blocked")
            return

        if isinstance(routed, str):
            display.info(routed)
            self._session.add_entry(raw_input, llm_response.explanation, "info")
            return

        if isinstance(routed, CommandRequest):
            self._handle_command(raw_input, llm_response, routed)
        elif isinstance(routed, ScaffoldRequest):
            self._handle_scaffold(raw_input, llm_response, routed)

    # ------------------------------------------------------------------
    # Private handlers
    # ------------------------------------------------------------------

    def _handle_command(
        self, raw_input: str, llm_response: LLMResponse, req: CommandRequest
    ) -> None:
        # Security check against the full command list
        check = self._shield.check(req)
        if not check.allowed:
            display.security_block(check.reason)
            self._session.add_entry(raw_input, llm_response.explanation, "security_block")
            return

        if check.needs_confirmation:
            cmds_preview = ", ".join(f"[bold]{c}[/bold]" for c in req.commands)
            confirmed = display.confirm(
                f"Run: {cmds_preview}  "
                f"(affects: {', '.join(req.affects_paths) or 'none'})"
            )
            if not confirmed:
                display.info("Aborted.")
                self._session.add_entry(raw_input, llm_response.explanation, "aborted")
                return

        if req.dry_run:
            display.dry_run(req.commands)
            self._session.add_entry(raw_input, llm_response.explanation, "dry_run")
            return

        # Run all commands in sequence; stop on first failure
        total = len(req.commands)
        overall_status = "success"
        for i, cmd in enumerate(req.commands, 1):
            display.step_header(i, total, cmd)
            result: ExecutionResult = self._executor.run(
                cmd, cwd=self._session.working_dir
            )
            display.execution_result(result, step=i if total > 1 else None)
            if not result.success:
                overall_status = f"error:{result.exit_code}"
                display.error(f"Step {i} failed — stopping execution.")
                break

        self._session.add_entry(raw_input, llm_response.explanation, overall_status)

    def _handle_scaffold(
        self, raw_input: str, llm_response: LLMResponse, req: ScaffoldRequest
    ) -> None:
        try:
            created = self._scaffolder.scaffold(req)
            display.scaffold_success(req.project_name, created)
            self._session.add_entry(raw_input, llm_response.explanation, "scaffold_ok")
        except Exception as exc:
            display.error(f"Scaffold failed: {exc}")
            self._session.add_entry(raw_input, llm_response.explanation, "scaffold_error")
