import asyncio

from llama_index.core.workflow import (
    InputRequiredEvent,
    HumanResponseEvent,
    Workflow,
    step,
    Event,
    Context,
    StopEvent,
    StartEvent,
)
from llama_index.core.workflow.handler import WorkflowHandler


# if the user says the research is not good enough, we retry the workflow
class RetryEvent(Event):
    pass


# if the user says the research is good enough, we generate a report
class ReportEvent(Event):
    pass


# we emit progress events to the frontend so the user knows what's happening
class ProgressEvent(Event):
    pass


# this is a dummy workflow to show how to do human in the loop workflows
# the purpose of the flow is to research a topic, get human review, and then write a report
class HITLWorkflow(Workflow):

    # this does the "research", which might involve searching the web or
    # looking up data in a database or our vector store.
    @step()
    async def research_query(
        self, ctx: Context, ev: StartEvent | RetryEvent
    ) -> InputRequiredEvent:
        ctx.write_event_to_stream(
            ProgressEvent(
                msg=f"I am doing some research on the subject of '{ev.query}'"
            )
        )
        await ctx.set("original_query", ev.query)

        # once we've done the research, we send what we've found back to the human for review
        # this gets handled by the frontend, and we expect a HumanResponseEvent to be sent back
        return InputRequiredEvent(
            prefix="",
            query=ev.query,
            payload="This is a bunch of placeholder text. It is not relevant to the research being done.",
        )

    # this accepts the HumanResponseEvent, which is either approval or rejection
    # if it's approval, we write the report, otherwise we do more research
    @step
    async def human_review(
        self, ctx: Context, ev: HumanResponseEvent
    ) -> ReportEvent | RetryEvent:
        ctx.write_event_to_stream(
            ProgressEvent(msg=f"The human has responded: {ev.response}")
        )
        if ev.response == "yes":
            return ReportEvent(
                result=f"Here is the research on {await ctx.get('original_query')}"
            )
        else:
            ctx.write_event_to_stream(
                ProgressEvent(msg=f"The human has rejected the research, retrying")
            )
            return RetryEvent(query=await ctx.get("original_query"))

    # this write the report, which would be an LLM operation with a bunch of context.
    @step
    async def write_report(self, ctx: Context, ev: ReportEvent) -> StopEvent:
        ctx.write_event_to_stream(
            ProgressEvent(
                msg=f"The human has approved the research, generating final report"
            )
        )
        # generate a report here
        return StopEvent(
            result=f"This is a report on {await ctx.get('original_query')}"
        )


# Assuming the HITLWorkflow and related classes are already defined as provided


async def run_hitl_workflow():
    # Example of setting a retry policy when initializing the workflow
    # Initialize the workflow
    workflow = HITLWorkflow(timeout=None)

    # Start the workflow with a StartEvent
    start_event = StartEvent(query="Artificial Intelligence")
    handler: WorkflowHandler = workflow.run(start_event=start_event)

    # Simulate the workflow execution
    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            # Simulate human response
            print(f"Research result: {event.payload}")
            human_response = (
                input("Is the research good enough? (yes/no): ").strip().lower()
            )
            handler.ctx.send_event(HumanResponseEvent(response=human_response))
        elif isinstance(event, ProgressEvent):
            # Print progress messages
            print(event.msg)

    # Await the final result
    final_result = await handler
    print(f"Final result: {final_result}")


if __name__ == "__main__":
    asyncio.run(run_hitl_workflow())


