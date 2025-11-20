import typer
from beastxml_tools.operations.validate import validate_xml
from beastxml_tools.operations.summarize import summarize_xml

app = typer.Typer(help="Tools for working with BEAST XML files")

@app.command()
def validate(path: str):
    """Validate a BEAST XML file."""
    validate_xml(path)

@app.command()
def summarize(path: str):
    """
    Summarize key BEAST XML settings.
    """
    from beastxml_tools.operations.summarize import summarize_xml

    summarize_xml(path)

if __name__ == "__main__":
    app()