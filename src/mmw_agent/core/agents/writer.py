from __future__ import annotations

from mmw_agent.config import Settings, settings
from mmw_agent.prompts import get_writer_prompt
from mmw_agent.schemas.a2a import WriterResponse
from mmw_agent.schemas.enums import AgentRole, CompTemplate, FormatOutPut
from mmw_agent.tools import OpenAlexScholar

from .base import RoleAgentBase


class WriterRoleAgent(RoleAgentBase):
    def __init__(
        self,
        *,
        scholar: OpenAlexScholar,
        comp_template: CompTemplate = CompTemplate.CHINA,
        format_output: FormatOutPut = FormatOutPut.Markdown,
        cfg: Settings = settings,
        agent=None,
    ):
        self.scholar = scholar
        self.comp_template = comp_template
        self.format_output = format_output
        self.available_images: list[str] = []

        super().__init__(
            role=AgentRole.WRITER,
            system_prompt=get_writer_prompt(format_output=format_output),
            tools=[self.search_papers],
            cfg=cfg,
            agent_name="mmw-writer-agent",
            agent=agent,
        )

    def search_papers(self, query: str) -> str:
        """Search papers from OpenAlex and return serialized results."""
        papers = self.scholar.search_papers(query)
        return self.scholar.papers_to_str(papers)

    def run(self, prompt: str, available_images: list[str] | None = None, sub_title: str | None = None) -> WriterResponse:
        final_prompt = prompt
        _ = sub_title

        if available_images:
            self.available_images = available_images
            image_lines = "\n".join([f"- ![{img}]({img})" for img in available_images])
            image_prompt = (
                "\n\n【必须插入的图片列表】\n"
                "以下图片是代码手生成的，你必须在论文相关段落后用 Markdown 格式逐一插入：\n"
                f"{image_lines}\n"
                "插入格式为独占一行的 ![描述](文件名)，每张图片后需配3行以上的分析解读。\n"
            )
            final_prompt += image_prompt

        response = self.agent.input(final_prompt, max_iterations=self.max_iterations)
        return WriterResponse(response_content=response, footnotes=[])

