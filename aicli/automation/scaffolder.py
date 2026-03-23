"""Scaffolder — renders Jinja2 templates and creates project files with rollback."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from aicli.automation.registry import get_template_dir
from aicli.interfaces import ScaffoldRequest


class Scaffolder:
    def scaffold(self, req: ScaffoldRequest) -> list[str]:
        """Create a project from a template. Returns list of created file paths.
        Rolls back all created files if an error occurs.
        """
        template_dir = get_template_dir(req.template)
        target = Path(req.target_dir).resolve()

        if target.exists():
            raise FileExistsError(
                f"Directory '{target}' already exists. Choose a different name."
            )

        created: list[str] = []
        try:
            target.mkdir(parents=True)
            created_files = self._render_tree(template_dir, target, req)
            created.extend(created_files)
        except Exception:
            # Rollback — remove everything we created
            if target.exists():
                shutil.rmtree(target)
            raise

        return [str(Path(p).relative_to(target)) for p in created]

    def _render_tree(
        self, template_dir: Path, target: Path, req: ScaffoldRequest
    ) -> list[str]:
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            keep_trailing_newline=True,
        )
        context = {
            "project_name": req.project_name,
            "project_name_slug": req.project_name.lower().replace(" ", "_").replace("-", "_"),
            **req.extra_params,
        }

        created: list[str] = []

        for root, _dirs, files in os.walk(template_dir):
            root_path = Path(root)
            relative = root_path.relative_to(template_dir)
            dest_dir = target / relative
            dest_dir.mkdir(parents=True, exist_ok=True)

            for fname in files:
                src_file = root_path / fname
                template_rel = str(relative / fname).replace("\\", "/")

                # Strip .j2 extension from destination filename
                dest_name = fname[:-3] if fname.endswith(".j2") else fname
                dest_file = dest_dir / dest_name

                if fname.endswith(".j2"):
                    tmpl = env.get_template(template_rel)
                    dest_file.write_text(tmpl.render(**context))
                else:
                    shutil.copy2(src_file, dest_file)

                created.append(str(dest_file))

        return created
