# Python Code Style Instructions

## Typing

- Use strongly typed variables and functions that use specific, well-defined types.
- Use modern Python typing features, and avoid using `Any` unless absolutely necessary. Prefer scoped generic types over `Any`.
- Use `typing.Literal`, `typing.LiteralString`, `typing.NamedTuple`, or `enum.Enum` classes instead of `str` or `int` for specific values.
- Use **built-in types for annotations** instead of their typing module types (e.g., use `list` instead of `List`, `dict` instead of `Dict`, etc.). The typing module versions have been deprecated.
- Use `|` for union types instead of `Union`.
- Use `typing.TypeGuard` or `typing.TypeIs` for type narrowing.
- Avoid creating generic dictionaries or lists unless necessary. Use `typing.TypedDict` or `typing.Protocol` for more complex structures.
- You may use `typing.cast` to resolve typing issues if necessary, but use it sparingly and only when you are sure of the type.
- Use `typing.overload` for function overloading if a function can accept different types of arguments and return different types based on the input.
- Use the `type` keyword to define type aliases, such as `type NoneList = list[None]` instead of `NoneList = list[None]`.
- If using features newer than Python 3.10, import from `typing_extensions` instead of `typing`.

## Style

- Generally follow the Google Python Style Guide.
- Follow Google Style for docstrings, but docstrings CAN be one line if the function/method's purpose is obvious and it's well annotated (that is, don't include Arguments, Returns, or Raises if they are clear from the context). Use active voice and keep them concise.
- Never include the type of a variable in the variable name. For example, use `icon_name` instead of `str_icon_name` or `icon_name_str`.
- Don't include types in the docstrings if the function is already strongly typed.
- Assume `black` style formatting; the project uses `ruff` for linting and formatting.
- Use `is` for comparing to `None`, `True`, or `False`, but only when you need to check for identity. If you are checking for truthiness, use `if x:` instead of `if x is True:`.
- Use `isinstance` for type checking instead of `type`.
- Use `assert` statements for debugging and testing, but avoid using them in production code. You may use `typing.assert_type` (forcing an Exception or allowing you to handle the Exception) if the code requires strict types to work as expected.
- If data would benefit from validation, use `pydantic` (version 2.x) for data validation and parsing. Use `pydantic.BaseModel` for defining data models, and use `pydantic.Field` for defining fields with validation rules. Make liberal use of `typing.Annotated` for defining field types and constraints.
- Use `dataclass.dataclass` for defining simple data classes, but prefer `pydantic.BaseModel` for more complex data models.

## Packaging

- Use `uv` for package management. For dependencies, uv's interface is the same as pip's, but uses `uv pip` instead of `pip`.
- Use `uv add` or `uv add --dev` to add packages. Use `uv remove` to remove packages. The project uses a `pyproject.toml`. Don't use legacy `requirements.txt` files.
- `uv` also handles virtual environments, so you can use `uv venv` to create and manage virtual environments, and it's used to build and publish packages.

## Code Patterns

- Strongly favor composition over inheritance.
- Avoid using stateful classes unless absolutely necessary. Use functions or stateless classes instead.
- Avoid using `@staticmethod`.
- Use functional approaches where possible, especially for data processing and transformation, and functional paradigms (`map`, `filter`, `reduce`) are acceptable if the code is clear and maintainable. If you need to repeatedly call a function with similar arguments, consider using `functools.partial` to make the code more readable or `functools.lru_cache` to cache results. You may also use `rpartial` and other functional tools from third party libraries, such as `funcy.rpartial`.
- Keep functions small and focused on a single task. If a function is doing too much, consider breaking it down into smaller helper functions.
- Don't hardcode values in the code. Use constants or configuration files instead.
