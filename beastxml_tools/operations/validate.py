from rich import print
from rich.console import Console
from rich.panel import Panel

from beastxml_tools.utils.xml_loader import load_xml, XMLLoadError

console = Console()

def validate_xml(path: str):
    """
    Validate that a BEAST XML file is well-formed and readable.
    """
    console.print(f"[bold cyan]Validating:[/bold cyan] {path}")

    try:
        tree, root = load_xml(path)

    except XMLLoadError as e:
        console.print(Panel.fit(str(e), title="❌ XML Error", style="bold red"))
        return

    # If reached here, XML is well-formed.
    console.print(Panel.fit("XML is well-formed ✔", style="bold green"))

    # Optional: basic BEAST structure sanity checks
    issues = []

    # Check for <run> element
    run_elements = root.xpath("//run")
    if not run_elements:
        issues.append("Missing <run> element (BEAST analysis block).")

    # Check at posterior, likelihood and prior
    posterior = root.xpath("//distribution[@id='posterior']")
    likelihood = root.xpath("//distribution[@id='likelihood']")
    prior = root.xpath("//distribution[@id='prior']")
    if not posterior:
        issues.append("Missing <distribution id='posterior'> element.")
    if not likelihood:
        issues.append("Missing <distribution id='likelihood'> element.")
    if not prior:
        issues.append("Missing <distribution id='prior'> element.")

    if issues:
        console.print(Panel.fit(
            "\n".join(issues),
            title="⚠️ Possible BEAST Issues",
            style="bold yellow"
        ))
    else:
        console.print(Panel.fit("Basic BEAST structure looks OK ✔", style="bold green"))