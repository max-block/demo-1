from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Type, Union

from markupsafe import Markup
from starlette.templating import Jinja2Templates

from app.core.core import Core


def timestamp(value: Optional[Union[datetime, int]], format_: str = "%Y-%m-%d %H:%M:%S") -> str:
    if isinstance(value, datetime):
        return value.strftime(format_)
    if isinstance(value, int):
        return datetime.fromtimestamp(value).strftime(format_)
    return ""


def empty(value):
    return value if value else ""


def yes_no(value, is_colored=True, hide_no=False, none_is_false=False, on_off=False):
    clr = "black"
    if none_is_false and value is None:
        value = False

    if value is True:
        value = "on" if on_off else "yes"
        clr = "green"
    elif value is False:
        if hide_no:
            value = ""
        else:
            value = "off" if on_off else "no"
        clr = "red"
    elif value is None:
        value = ""
    if not is_colored:
        clr = "black"
    return Markup(f"<span style='color: {clr};'>{value}</span>")


def nformat(value, prefix="", suffix="", separator="_", hide_zero=True, digits=2):
    if value is None or value == "":
        return ""
    if float(value) == 0:
        if hide_zero:
            return ""
        else:
            return f"{prefix}0{suffix}"
    if float(value) > 1000:
        value = "".join(
            reversed([x + (separator if i and not i % 3 else "") for i, x in enumerate(reversed(str(int(value))))]),
        )
    else:
        value = round(value, digits)

    return f"{prefix}{value}{suffix}"


def raise_(msg):
    raise Exception(msg)


def configure_jinja(core: Core) -> Jinja2Templates:
    current_dir = Path(__file__).parent.absolute()
    templates = Jinja2Templates(directory=current_dir.joinpath("templates"))
    templates.env.filters["timestamp"] = timestamp
    templates.env.filters["dt"] = timestamp
    templates.env.filters["empty"] = empty
    templates.env.filters["yes_no"] = yes_no
    templates.env.filters["nformat"] = nformat
    templates.env.filters["n"] = nformat
    templates.env.globals["config"] = core.config
    templates.env.globals["now"] = datetime.utcnow
    templates.env.globals["raise"] = raise_
    templates.env.globals["confirm"] = """ onclick="return confirm('sure?')" """

    return templates


def form_choices(choices: Union[List[str], Type[Enum]], title=""):
    result = []
    if title:
        result.append(("", title + "..."))
    if isinstance(choices, list):
        for value in choices:
            result.append((value, value))
    else:
        for value in [e.value for e in choices]:
            result.append((value, value))
    return result
