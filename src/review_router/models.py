from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StepType(StrEnum):
    TRIGGER = "trigger"
    TRANSFORM = "transform"
    AI = "ai"
    ROUTE = "route"
    REVIEW_GATE = "review_gate"
    DESTINATION = "destination"
    HANDOFF = "handoff"


class ErrorTaxonomy(StrEnum):
    VALIDATION_ERROR = "validation_error"
    AI_UNCERTAINTY = "ai_uncertainty"
    ROUTING_ERROR = "routing_error"
    DESTINATION_ERROR = "destination_error"
    TRANSIENT_ERROR = "transient_error"


class WorkflowBoundary(BaseModel):
    service: str
    secret_name: str
    required_scopes: list[str] = Field(default_factory=list)
    live_enabled_by_default: bool = False


class StepFailurePath(BaseModel):
    error: ErrorTaxonomy
    next_step_id: str


class RouteOption(BaseModel):
    key: str
    next_step_id: str
    description: str


class ReviewPolicy(BaseModel):
    reason: str
    queue: str = "default"
    candidate_routes: list[str] = Field(default_factory=list)
    recommended_next_action: str


class BaseStep(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    title: str
    type: StepType
    description: str
    next_step_id: str | None = None
    failure: StepFailurePath | None = None
    credential_boundaries: list[WorkflowBoundary] = Field(default_factory=list)


class TriggerStep(BaseStep):
    type: Literal[StepType.TRIGGER] = StepType.TRIGGER
    source: str


class TransformStep(BaseStep):
    type: Literal[StepType.TRANSFORM] = StepType.TRANSFORM
    transform: str


class AIStep(BaseStep):
    type: Literal[StepType.AI] = StepType.AI
    model_family: str = "deterministic-mock"
    uncertainty_threshold: float = 0.75
    output_fields: list[str] = Field(default_factory=list)


class RouteStep(BaseStep):
    type: Literal[StepType.ROUTE] = StepType.ROUTE
    route_key_field: str
    routes: list[RouteOption]


class ReviewGateStep(BaseStep):
    type: Literal[StepType.REVIEW_GATE] = StepType.REVIEW_GATE
    policy: ReviewPolicy


class DestinationStep(BaseStep):
    type: Literal[StepType.DESTINATION] = StepType.DESTINATION
    destination: str


class HandoffStep(BaseStep):
    type: Literal[StepType.HANDOFF] = StepType.HANDOFF
    note_template: str


WorkflowStep = (
    TriggerStep
    | TransformStep
    | AIStep
    | RouteStep
    | ReviewGateStep
    | DestinationStep
    | HandoffStep
)


class WorkflowTemplate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    version: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    fixture_safe: bool = True
    live_services_used: bool = False
    synthetic_data_only: bool = True
    review_queue: str = "default"
    tags: list[str] = Field(default_factory=list)
    steps: list[
        TriggerStep
        | TransformStep
        | AIStep
        | RouteStep
        | ReviewGateStep
        | DestinationStep
        | HandoffStep
    ]
