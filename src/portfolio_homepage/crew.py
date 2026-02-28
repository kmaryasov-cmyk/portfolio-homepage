from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


class Segment(BaseModel):
    segment_id: str
    text: str
    lang: Literal["ru", "en", "mix", "other"] = "ru"
    flags: List[Literal["ocr", "broken", "placeholder"]] = Field(default_factory=list)


class SegmentsOutput(BaseModel):
    segments: List[Segment]


class Evidence(BaseModel):
    segment_id: str
    quote: str


class Claim(BaseModel):
    claim_id: str
    claim: str
    status: Literal["supported", "needs_clarification", "contradictory", "out_of_scope"]
    evidence: List[Evidence] = Field(default_factory=list)
    notes: Optional[str] = None


class ClaimsOutput(BaseModel):
    claims: List[Claim]


class Question(BaseModel):
    question_id: str
    question: str
    targets: List[str] = Field(default_factory=list)


class QuestionsOutput(BaseModel):
    questions: List[Question]


class TraceItem(BaseModel):
    sentence_id: str
    sentence_text: str
    claim_ids: List[str] = Field(default_factory=list)


class DraftOutput(BaseModel):
    homepage_md: str
    trace_map: List[TraceItem]


class QaIssue(BaseModel):
    issue_id: str
    type: Literal["ungrounded", "claim_not_supported", "missing_evidence", "other"] = "other"
    sentence_id: Optional[str] = None
    detail: str


class QaReport(BaseModel):
    issues: List[QaIssue] = Field(default_factory=list)


class FinalOutput(BaseModel):
    homepage_md: str
    trace_map: List[TraceItem]
    qa_report: QaReport


@CrewBase
class PortfolioHomepageCrew:
    """Turn raw source text into a fact-grounded Russian portfolio homepage."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def facts_extractor(self) -> Agent:
        return Agent(config=self.agents_config["facts_extractor"], verbose=True)  # type: ignore[index]

    @agent
    def homepage_writer(self) -> Agent:
        return Agent(config=self.agents_config["homepage_writer"], verbose=True)  # type: ignore[index]

    @agent
    def fact_qa(self) -> Agent:
        return Agent(config=self.agents_config["fact_qa"], verbose=True)  # type: ignore[index]

    @task
    def segment_source_task(self) -> Task:
        return Task(
            config=self.tasks_config["segment_source_task"],  # type: ignore[index]
            output_pydantic=SegmentsOutput,
        )

    @task
    def extract_claims_task(self) -> Task:
        return Task(
            config=self.tasks_config["extract_claims_task"],  # type: ignore[index]
            output_pydantic=ClaimsOutput,
        )

    @task
    def clarification_questions_task(self) -> Task:
        return Task(
            config=self.tasks_config["clarification_questions_task"],  # type: ignore[index]
            output_pydantic=QuestionsOutput,
        )

    @task
    def draft_homepage_task(self) -> Task:
        return Task(
            config=self.tasks_config["draft_homepage_task"],  # type: ignore[index]
            output_pydantic=DraftOutput,
        )

    @task
    def final_fact_qa_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_fact_qa_task"],  # type: ignore[index]
            output_pydantic=FinalOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
