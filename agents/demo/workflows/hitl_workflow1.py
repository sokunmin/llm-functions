# Ref:
# * https://github.com/run-llama/python-agents-tutorial/blob/main/5_human_in_the_loop.py
# * https://github.com/run-llama/human_in_the_loop_workflow_demo
from dotenv import load_dotenv
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import (
    InputRequiredEvent,
    HumanResponseEvent,
    Context,
)
from llama_index.llms.groq import Groq

load_dotenv()

llm = Groq(
    model="qwen-2.5-32b",
)


def construct_workflow():
    # a tool that performs a dangerous task
    async def dangerous_task(ctx: Context) -> str:
        """A dangerous task that requires human confirmation."""

        # emit an event to the external stream to be captured
        ctx.write_event_to_stream(
            InputRequiredEvent(
                prefix="Are you sure you want to proceed? ",
                user_name="Laurie",
            )
        )

        # wait until we see a HumanResponseEvent
        response = await ctx.wait_for_event(
            HumanResponseEvent, requirements={"user_name": "Laurie"}
        )

        # act on the input from the event
        if response.response.strip().lower() == "yes":
            return "Dangerous task completed successfully."
        else:
            return "Dangerous task aborted."

    workflow = AgentWorkflow.from_tools_or_functions(
        [dangerous_task],
        llm=llm,
        system_prompt="You are a helpful assistant that can perform dangerous tasks.",
    )
    return workflow


async def hitl_workflow():
    workflow = construct_workflow()
    handler = workflow.run(user_msg="I want to proceed with the dangerous task.")

    async for event in handler.stream_events():
        # capture InputRequiredEvent
        if isinstance(event, InputRequiredEvent):
            # capture keyboard input
            response = input(event.prefix)
            # send our response back
            handler.ctx.send_event(
                HumanResponseEvent(
                    response=response,
                    user_name=event.user_name,
                )
            )

    response = await handler
    print(str(response))

