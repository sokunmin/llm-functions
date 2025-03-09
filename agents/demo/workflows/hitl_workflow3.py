import asyncio
from typing import Any, List, Optional
import uuid

from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
import nest_asyncio
from llama_index.utils.workflow import draw_all_possible_flows

load_dotenv()

SEGMENT_GENERATION_TEMPLATE = """
您正在與人類合作創建一個「選擇你自己的冒險」風格的故事。

人類扮演故事中的主角角色，而您負責協助撰寫故事。為了創建故事，我們分步進行，每一步生成一個區塊。
每個區塊包含情節（PLOT）、主角可以採取的行動（ACTIONS）以及所選的行動（CHOICE）。

以下是迄今為止的冒險歷史。

先前的區塊：
---
{running_story}

請繼續故事，生成下一個區塊的情節和行動集。如果沒有先前的區塊，請開始一個全新的有趣故事。為主角取一個名字並設定一個有趣的挑戰。

使用提供的數據模型來構建您的輸出。
"""

FINAL_SEGMENT_GENERATION_TEMPLATE = """
您正在與人類合作創建一個「選擇你自己的冒險」風格的故事。

人類扮演故事中的主角角色，而您負責協助撰寫故事。為了創建故事，我們分步進行，每一步生成一個區塊。
每個區塊包含情節（PLOT）、主角可以採取的行動（ACTIONS）以及所選的行動（CHOICE）。以下是迄今為止的冒險歷史。

先前的區塊：
---
{running_story}

故事即將結束。根據先前的區塊，以一個結尾情節來總結故事。由於這是結尾情節，請勿生成新的行動集。

使用提供的數據模型來構建您的輸出。
"""

BLOCK_TEMPLATE = """
區塊
===
情節: {plot}
行動: {actions}
選擇: {choice}
"""


class Segment(BaseModel):
    """用於生成故事段落的數據模型。"""

    plot: str = Field(description="當前段落冒險的情節。情節不應超過3句話。")
    actions: List[str] = Field(
        default=[],
        description="主角可以採取的行動列表，這些行動將塑造下一個段落的情節和行動。",
    )


class Block(BaseModel):
    id_: str = Field(default_factory=lambda: str(uuid.uuid4()))
    segment: Segment
    choice: Optional[str] = None
    block_template: str = BLOCK_TEMPLATE

    def __str__(self):
        return self.block_template.format(
            plot=self.segment.plot,
            actions=", ".join(self.segment.actions),
            choice=self.choice or "",
        )


class NewBlockEvent(Event):
    block: Block


class HumanChoiceEvent(Event):
    block_id: str


class ChooseYourOwnAdventureWorkflow(Workflow):
    def __init__(self, max_steps: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.llm = Gemini()
        self.max_steps = max_steps

    @step
    async def create_segment(
        self, ctx: Context, ev: StartEvent | HumanChoiceEvent
    ) -> NewBlockEvent | StopEvent:
        blocks = await ctx.get("blocks", [])
        running_story = "\n".join(str(b) for b in blocks)

        if len(blocks) < self.max_steps:
            new_segment = self.llm.structured_predict(
                Segment,
                PromptTemplate(SEGMENT_GENERATION_TEMPLATE),
                running_story=running_story,
            )
            new_block = Block(segment=new_segment)
            blocks.append(new_block)
            await ctx.set("blocks", blocks)
            return NewBlockEvent(block=new_block)
        else:
            final_segment = self.llm.structured_predict(
                Segment,
                PromptTemplate(FINAL_SEGMENT_GENERATION_TEMPLATE),
                running_story=running_story,
            )
            final_block = Block(segment=final_segment)
            blocks.append(final_block)
            return StopEvent(result=blocks)

    @step
    async def prompt_human(self, ctx: Context, ev: NewBlockEvent) -> HumanChoiceEvent:
        block = ev.block

        # 獲取人類輸入
        human_prompt = f"\n===\n{ev.block.segment.plot}\n\n"
        human_prompt += "選擇你的冒險：\n\n"
        human_prompt += "\n".join(ev.block.segment.actions)
        human_prompt += "\n\n"
        human_input = input(human_prompt)

        blocks = await ctx.get("blocks")
        block.choice = human_input
        blocks[-1] = block
        await ctx.set("block", blocks)

        return HumanChoiceEvent(block_id=ev.block.id_)


# draw_all_possible_flows(ChooseYourOwnAdventureWorkflow, filename="hitl_workflow4.html")


def generate_example():
    # 讓我們看一個段落的範例
    llm = Gemini()
    segment = llm.structured_predict(
        Segment,
        PromptTemplate(SEGMENT_GENERATION_TEMPLATE),
        running_story="",
    )

    print(segment)
    block = Block(segment=segment)
    print(block)


async def main():
    nest_asyncio.apply()
    w = ChooseYourOwnAdventureWorkflow(timeout=None)
    result = await w.run()

    final_story = "\n\n".join(b.segment.plot for b in result)
    print(final_story)


if __name__ == "__main__":
    generate_example()
    asyncio.run(main())
