from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from review_router.models import AIStep, ReviewGateStep, RouteStep, WorkflowTemplate


@dataclass
class ValidationIssue:
    code: str
    message: str


@dataclass
class ValidationReport:
    valid: bool
    issues: list[ValidationIssue]

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "issues": [{"code": issue.code, "message": issue.message} for issue in self.issues],
        }

    def to_text(self) -> str:
        if self.valid:
            return "VALID: workflow template passed all contract checks"
        return "\n".join(
            ["INVALID: workflow template failed contract checks"]
            + [f"- {issue.code}: {issue.message}" for issue in self.issues]
        )


REQUIRED_BOUNDARY_SERVICES = {"n8n", "make", "zapier", "api"}


def load_template(data: dict[str, object]) -> WorkflowTemplate:
    try:
        return WorkflowTemplate.model_validate(data)
    except ValidationError as exc:
        issues = [ValidationIssue(code="schema_error", message=err["msg"]) for err in exc.errors()]
        raise ValueError(ValidationReport(valid=False, issues=issues).to_text()) from exc


class WorkflowValidator:
    def validate(self, template: WorkflowTemplate) -> ValidationReport:
        issues: list[ValidationIssue] = []
        step_ids = {step.id for step in template.steps}
        if len(step_ids) != len(template.steps):
            issues.append(
                ValidationIssue("duplicate_step_id", "workflow contains duplicate step ids")
            )

        review_steps = [step for step in template.steps if isinstance(step, ReviewGateStep)]
        if not review_steps:
            issues.append(
                ValidationIssue(
                    "missing_review_path",
                    "workflow template must include an explicit manual review gate",
                )
            )

        ai_steps = [step for step in template.steps if isinstance(step, AIStep)]
        if not ai_steps:
            issues.append(
                ValidationIssue(
                    "missing_ai_step",
                    "workflow template must contain at least one AI step",
                )
            )

        for step in template.steps:
            if step.failure is None:
                issues.append(
                    ValidationIssue(
                        "missing_failure_path",
                        f"step '{step.id}' is missing an explicit failure path",
                    )
                )
            elif step.failure.next_step_id not in step_ids:
                issues.append(
                    ValidationIssue(
                        "unknown_failure_target",
                        (
                            f"step '{step.id}' points to unknown failure target "
                            f"'{step.failure.next_step_id}'"
                        ),
                    )
                )

            if step.next_step_id is not None and step.next_step_id not in step_ids:
                issues.append(
                    ValidationIssue(
                        "unknown_next_step",
                        f"step '{step.id}' points to unknown next step '{step.next_step_id}'",
                    )
                )

            if isinstance(step, RouteStep):
                for route in step.routes:
                    if route.next_step_id not in step_ids:
                        issues.append(
                            ValidationIssue(
                                "unknown_route_target",
                                (
                                    f"route '{route.key}' in step '{step.id}' points "
                                    f"to unknown step '{route.next_step_id}'"
                                ),
                            )
                        )

        boundary_services = {
            boundary.service for step in template.steps for boundary in step.credential_boundaries
        }
        if not REQUIRED_BOUNDARY_SERVICES.issubset(boundary_services):
            missing = ", ".join(sorted(REQUIRED_BOUNDARY_SERVICES - boundary_services))
            issues.append(
                ValidationIssue(
                    "missing_credential_boundaries",
                    f"workflow is missing explicit credential boundary declarations for: {missing}",
                )
            )

        return ValidationReport(valid=not issues, issues=issues)
