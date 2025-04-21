from openai import OpenAI

from console_gpt.config_manager import fetch_variable
from console_gpt.custom_stdout import custom_print
from console_gpt.general_utils import capitalize
from console_gpt.menus.assistant_menu import (create_message, run_thread,
                                              update_conversation)
from console_gpt.menus.command_handler import command_handler
from console_gpt.prompts.assistant_prompt import assistance_reply
from console_gpt.prompts.user_prompt import assistant_user_prompt
from mcp_servers.mcp_tcp_client import MCPClient


def assistant(console, data) -> None:
    from console_gpt.constants import BASE_URL
    client = OpenAI(api_key=data.model["api_key"], base_url=BASE_URL) if BASE_URL else OpenAI(api_key=data.model["api_key"])
    # Step 3: Add a Message to a Thread
    while True:
        user_input = assistant_user_prompt()
        # Command Handler
        if not user_input or user_input.lower() in ("exit", "quit", "bye"):  # Used to catch SIGINT
            if fetch_variable("features", "mcp_client"):
                with MCPClient(auto_start=False) as mcp:
                    if mcp is not None:
                        mcp.stop_server()
            custom_print("exit", "Goodbye, see you soon!", 130)
        elif user_input.lower() == "save":
            custom_print("info", "Assistant conversations are not saved locally.")
            continue
        elif user_input.lower() == "image":
            custom_print("warn", "Assistant conversations do not support processing images yet.")
            continue
        elif user_input.lower() == "tools":
            custom_print("warn", "Assistant tools may be currently selected only before the converstaion.")
            continue
        elif user_input.lower() in ["flush", "new"]:
            break
        # TODO implement dedicated command handler for assistants
        handled_user_input = command_handler(
            data.model["model_title"], data.model["model_name"], user_input, "", False, []
        )
        match handled_user_input:
            case "continue" | None:
                continue
            case "break":
                break
            case _:
                user_input = handled_user_input
        try:
            message = create_message(client, data.thread_id, user_input)
        except (OpenAI.NotFoundError, OpenAI.APIConnectionError, OpenAI.APIError) as e:
            custom_print(
                "error",
                "The thread specified in the local assistant file does not exist. Please edit the assistant and try again.",
            )
            break
        conversation = message.id
        # Start the loading bar until API response is returned
        with console.status("[bold green]Generating a response...", spinner="aesthetic"):
            # Step 4: Run the Assistant
            run_thread(client, data.assistant_id, data.thread_id)
        # Step 6: Display the Assistant's Response
        conversation, new_replies = update_conversation(client, conversation, data.thread_id)
        if new_replies:
            for reply in new_replies:
                assistance_reply(reply["content"], capitalize(data.assistant_name))
