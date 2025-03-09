import asyncio
import os
import urllib.request

def get_current_datetime():
    """
    Get current date time
    """
    from agents.demo.workflows.demo_workflow import demo_workflow
    return asyncio.run(demo_workflow())


def get_user_info():
    """
    Get user information and address
    """
    print("[get_user_info]")
    username = os.getenv("LLM_AGENT_VAR_USERNAME")
    address = os.getenv("LLM_AGENT_VAR_ADDRESS")
    print("username=", username)
    print("address=", address)
    return f"User: {username}, Address: {address}"


def get_ipinfo():
    """
    Get the ip info
    """
    with urllib.request.urlopen("https://httpbin.org/ip") as response:
        data = response.read()
        return data.decode('utf-8')


def run_hitl_workflow():
    """
    Run the Human-in-the-loop (HITL) workflow
    """
    from agents.demo.workflows.hitl_workflow1 import hitl_workflow
    asyncio.run(hitl_workflow())
