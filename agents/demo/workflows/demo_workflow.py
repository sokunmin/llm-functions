import asyncio

from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step


class DemoWorkflow(Workflow):

    @step
    def my_step(self, ev: StartEvent) -> StopEvent:
        from datetime import datetime
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return StopEvent(result=dt)


async def demo_workflow():
    workflow = DemoWorkflow(verbose=False)
    result = await workflow.run()
    return result