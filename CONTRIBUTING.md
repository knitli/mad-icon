# Contributing to mad-icon

You can contribute to this project in several ways:

- **Report bugs** or issues [here](https://github.com/knitli/mad-icon/issues).
- **Submit feature requests** or suggestions, also [here](https://github.com/knitli/mad-icon/issues).
- **Submit a pull request** with your changes or improvements. If your code adds or changes functionality, please include tests to ensure it works as expected.
- **Improve the documentation* by suggesting edits or corrections (or even better, we could use a docs site...).
- **Give it a star** on GitHub to show your support and help others find the project.
- **Share it with others who might find it useful**. Or, hoard it to yourself and convince everyone you are a PWA asset ninja :ninja:.
- **Broadcast to the social media universe** how awesome it is to have a PWA icon generator that covers all the bases and is *probably the first step towards world peace*.
- *Write a blog post or tutorial* about how to use the project.
- Or just, you know, use it.

## Code Contributions

Anyone can contribute code regardless of their experience. We all started somewhere and we all have something to learn. A good place to start is to look at the [issues](https://github.com/knitli/mad-icon/issues) and see if there is something you can help with. We will try to label issues that are good for beginners with the `good first issue` label. If you have an idea for a new feature or improvement, feel free to open an issue and discuss it with us.

If you have no idea what to do but still want to contribute, submit an issue and we'll help you get started.

The easiest way to follow our style guidelines is to use our Ruff formatting and linting, which is already configured in the project.

### Setup

The project requires Python >= 3.11, with 3.13 recommended.

We use [`uv`](https://docs.astral.sh/uv/) to manage the project environment, dependencies, build, etc. If you don't have `uv` installed, you can install it with `pip install uv`, or depending on your system and tools: `brew install uv`, `winget install uv`, `scoop install uv`, `mise use uv`, `cargo install --git https://github.com/astral-sh/uv uv`, or directly with `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/MacOS)/ `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows).

```bash
git clone https://github.com/knitli/mad-icon.git
cd mad-icon
uv venv .venv
source .venv/bin/activate
uv pip install .
```

If you use `vscode`, you can just install all of the [recommended extensions](.vcode/extensions.json) and the editor will automatically pick up our `ruff` configuration and `pyright` type checking. If you use another editor, you can run `ruff` and `pyright` from the command line to check your code.

```bash
ruff check .
ruff format .
pyright .
```

If you want to run the tests, you can use `pytest`:

```bash
uv pytest
```

If you want to run the tests with coverage, you can use `pytest-cov`:

```bash
uv pytest --cov
```

If you want to run the tests with coverage and generate a report, you can use `pytest-cov`:

```bash
uv pytest --cov --cov-report html
```

If you want to run the tests with coverage and generate a report in the terminal, you can use `pytest-cov`:

```bash
uv pytest --cov --cov-report term-missing
```

## Ground Rules

Don't be a jerk. If you are rude, condescending, or dismissive, you will be banned from the project. We are all here to learn and grow, and we want to create a positive and inclusive environment for everyone.
