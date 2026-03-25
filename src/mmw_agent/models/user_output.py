from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from mmw_agent.schemas.a2a import WriterResponse


class UserOutput:
    def __init__(self, work_dir: str | Path, ques_count: int):
        self.work_dir = Path(work_dir)
        self.res: dict[str, dict] = {}
        self.ques_count: int = ques_count
        self.footnotes: dict[str, dict] = {}
        self.seq: list[str] = []
        self._init_seq()

    def _init_seq(self) -> None:
        ques_str = [f"ques{i}" for i in range(1, self.ques_count + 1)]
        self.seq = [
            "firstPage",
            "RepeatQues",
            "analysisQues",
            "modelAssumption",
            "symbol",
            "eda",
            *ques_str,
            "sensitivity_analysis",
            "judge",
        ]

    def set_res(self, key: str, writer_response: WriterResponse) -> None:
        self.res[key] = {
            "response_content": writer_response.response_content,
            "footnotes": writer_response.footnotes,
        }

    def load_res(self, res: dict[str, dict] | None) -> None:
        self.res = res or {}

    def get_res(self) -> dict[str, dict]:
        return self.res

    def get_model_build_solve(self) -> str:
        return ",".join(
            f"{key}-{value}"
            for key, value in self.res.items()
            if key.startswith("ques") and key != "ques_count"
        )

    def replace_references_with_uuid(self, text: str) -> str:
        references = re.findall(r"\{\[\^(\d+)\]:\s*(.*?)\}", text, re.DOTALL)

        for ref_num, ref_content in references:
            normalized = ref_content.strip().rstrip(".")
            existing_uuid = None
            for foot_uuid, footnote_data in self.footnotes.items():
                if footnote_data["content"] == normalized:
                    existing_uuid = foot_uuid
                    break

            if existing_uuid:
                text = re.sub(
                    rf"\{{\[\^{ref_num}\]:.*?\}}",
                    f"[{existing_uuid}]",
                    text,
                    flags=re.DOTALL,
                )
            else:
                new_uuid = str(uuid.uuid4())
                self.footnotes[new_uuid] = {"content": normalized}
                text = re.sub(
                    rf"\{{\[\^{ref_num}\]:.*?\}}",
                    f"[{new_uuid}]",
                    text,
                    flags=re.DOTALL,
                )

        return text

    def sort_text_with_footnotes(self, replace_res: dict) -> dict:
        sort_res = {}
        ref_index = 1

        for seq_key in self.seq:
            text = replace_res.get(seq_key, {}).get("response_content", "")
            uuid_list = re.findall(r"\[([a-f0-9-]{36})\]", text)
            for uid in uuid_list:
                text = text.replace(f"[{uid}]", f"[^{ref_index}]")
                if self.footnotes[uid].get("number") is None:
                    self.footnotes[uid]["number"] = ref_index
                ref_index += 1
            sort_res[seq_key] = {"response_content": text}

        return sort_res

    def append_footnotes_to_text(self, text: str) -> str:
        text += "\n\n## 参考文献"
        sorted_footnotes = sorted(self.footnotes.items(), key=lambda x: x[1]["number"])
        for _, footnote in sorted_footnotes:
            text += f"\n\n[^{footnote['number']}]: {footnote['content']}"
        return text

    def get_result_to_save(self) -> str:
        replace_res = {}

        for key, value in self.res.items():
            new_text = self.replace_references_with_uuid(value["response_content"])
            replace_res[key] = {"response_content": new_text}

        sort_res = self.sort_text_with_footnotes(replace_res)

        full_text = "\n\n".join([sort_res[key]["response_content"] for key in self.seq])
        return self.append_footnotes_to_text(full_text)

    def save_result(self) -> tuple[Path, Path]:
        res_json = self.work_dir / "res.json"
        res_md = self.work_dir / "res.md"

        res_json.write_text(json.dumps(self.res, ensure_ascii=False, indent=2), encoding="utf-8")
        res_md.write_text(self.get_result_to_save(), encoding="utf-8")
        return res_json, res_md
