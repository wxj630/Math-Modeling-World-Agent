from enum import Enum


class CompTemplate(str, Enum):
    CHINA = "CHINA"
    AMERICAN = "AMERICAN"


class FormatOutPut(str, Enum):
    Markdown = "Markdown"
    LaTeX = "LaTeX"


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    MODELER = "modeler"
    CODER = "coder"
    WRITER = "writer"


class WorkflowMode(str, Enum):
    COMPETITION = "competition"
    AI_TUTOR = "ai_tutor"
