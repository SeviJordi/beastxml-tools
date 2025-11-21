from rich import print
from rich.console import Console
from rich.panel import Panel

from beastxml_tools.utils.xml_loader import BeastXML, XMLLoadError

console = Console()


class BeastXMLValidator:
    """
    Class of BeastXML to add validation methods.
    """

    def __init__(self, xml: BeastXML):
        self.xml = xml
        self._issues = []
        self._duplicated_ids = []
        self.validate()

    def validate(self):
        """
        Validate the loaded XML against BEAST requirements.
        """
        issues = []

        # Check for <run> element
        run_elements = self.xml.search("//run")
        if not run_elements:
            issues.append("Missing <run> element (BEAST analysis block).")

        # Check at posterior, likelihood and prior
        posterior = self.xml.search("//distribution[@id='posterior']")
        likelihood = self.xml.search("//distribution[@id='likelihood']")
        prior = self.xml.search("//distribution[@id='prior']")
        if not posterior:
            issues.append("Missing <distribution id='posterior'> element.")
        if not likelihood:
            issues.append("Missing <distribution id='likelihood'> element.")
        if not prior:
            issues.append("Missing <distribution id='prior'> element.")

        self._issues = issues

        self._duplicated_ids = self.get_duplicated_ids()

    @property
    def issues(self):
        return self._issues

    @property
    def duplicated_ids(self):
        return self._duplicated_ids

    def has_duplicated_ids(self):
        """
        Check for duplicated IDs in the XML.
        """
        return len(self._duplicated_ids) > 0

    def get_duplicated_ids(self):
        """
        Return a list of duplicated IDs found in the XML.
        """
        id_count = {}
        for elem in self.xml.search("//*[@id]"):
            eid = elem.get("id")
            if eid:
                if eid in id_count:
                    id_count[eid] += 1
                else:
                    id_count[eid] = 1

        return [eid for eid, count in id_count.items() if count > 1]


def validate_xml(path: str):
    """
    Validate that a BEAST XML file is well-formed and readable.
    """
    console.print(f"[bold cyan]Validating:[/bold cyan] {path}")

    try:
        beast_xml = BeastXML(path)
        validator = BeastXMLValidator(beast_xml)

    except XMLLoadError as e:
        console.print(Panel.fit(str(e), title="❌ XML Error", style="bold red"))
        return

    # If reached here, XML is well-formed.
    console.print(Panel.fit("XML is well-formed ✔", style="bold green"))

    # Print issues if any
    issues = validator.issues
    if issues:
        console.print(
            Panel.fit(
                "\n".join(issues), title="⚠️ Possible BEAST Issues", style="bold red"
            )
        )
    else:
        console.print(Panel.fit("Basic BEAST structure looks OK ✔", style="bold green"))

    # Check for duplicated IDs
    if validator.has_duplicated_ids():
        console.print(
            Panel.fit(
                "Duplicated IDs found in the XML. This may cause issues in BEAST runs.",
                title="⚠️ Duplicated IDs",
                style="bold red",
            )
        )

        for did in validator.duplicated_ids:
            console.print(f" - [red]{did}[/red]")

    else:
        console.print(Panel.fit("No duplicated IDs found ✔", style="bold green"))
