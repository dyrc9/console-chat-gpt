import re
from typing import Optional

from questionary import text

from console_gpt.catch_errors import eof_wrapper
from console_gpt.constants import custom_style, style
from console_gpt.custom_stdin import custom_input
from console_gpt.custom_stdout import custom_print
from console_gpt.general_utils import flush_lines, use_emoji_maybe


def _validate_url(url: str) -> str | bool:
    """
    Verify if the provided URL is valid
    :param url: URL
    :return: Either an error message or True represented as string for compatibility
    """
    url_pattern = re.compile(
        r"^(?:(?:https?|ftp)://"  # Optional scheme (http, https, ftp)
        r")?(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # Domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP address
        r"(?::\d+)?"  # Optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if url_pattern.match(url):
        return True
    return "Invalid URL"


@eof_wrapper
def input_url() -> Optional[str]:
    """
    A base prompt for getting URL
    :return: Either none if SIGINT or the URL
    """
    url = text(
        message="Provide a URL:", style=custom_style, validate=_validate_url, qmark=use_emoji_maybe("\U0001f30d")
    ).ask()
    if not url:
        flush_lines(4)
        custom_print("info", "Cancelled the URL prompt.")
    return url


@eof_wrapper
def additional_info(content: str) -> str:
    """
    Asking for additional info besides the existing
    :return: The content or content + additional info
    """

    additional_data = custom_input(
        auto_exit=False,
        message="Additional clarifications? (Press 'ENTER' to skip):",
        style=style,
        qmark="❯",
    )

    if additional_data:
        return additional_data, f"This is the content of a webpage:\n{content}"
    else:
        return None, f"This is the content of a webpage:\n{content}"
