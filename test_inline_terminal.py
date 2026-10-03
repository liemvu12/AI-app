"""
Test prototype for inline terminal stream
"""
import sys
import asyncio
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import Static, Input


class InlineTerminal(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static("[dim]AGY Terminal Console[/dim]", id="terminal-banner")
        with Horizontal(id="active-input-row"):
            yield Static("agy> ", id="prompt-prefix")
            yield Input(id="inline-input")

    def append_entry(self, cmd: str, response: str) -> None:
        input_row = self.query_one("#active-input-row")
        # Mount the command and response right above the input row
        self.mount(Static(f"[bold green]agy>[/bold green] {cmd}"), before=input_row)
        self.mount(Static(response), before=input_row)
        self.scroll_end(animate=False)


class TestApp(App):
    CSS = """
    Screen { background: #0c0e14; color: #d1d5db; }
    #terminal-scroll { height: 100%; padding: 0 1; }
    #active-input-row { height: 1; layout: horizontal; }
    #prompt-prefix { width: 5; color: #10b981; text-style: bold; }
    #inline-input { width: 1fr; height: 1; border: none; background: transparent; padding: 0; }
    """

    def compose(self) -> ComposeResult:
        yield InlineTerminal(id="terminal-scroll")


async def main():
    app = TestApp()
    async with app.run_test() as pilot:
        term = app.query_one("#terminal-scroll", InlineTerminal)
        inp = app.query_one("#inline-input", Input)
        assert inp is not None
        term.append_entry("help", "Available commands: /model, /skills")
        await pilot.pause(0.1)
        print("Inline terminal mount and append tested successfully!")


if __name__ == "__main__":
    asyncio.run(main())
