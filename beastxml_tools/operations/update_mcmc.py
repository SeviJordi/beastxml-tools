from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from lxml import etree
from beastxml_tools.utils.xml_loader import BeastXML, XMLLoadError

console = Console()

class BeastXMLChainManipulator(BeastXML):
    """
    Class of BeastXML to add chain modification methods.
    """

    def get_run_element(self):
        runs = self.search("//run")
        return runs[0] if runs else None

    def update_chain_length(self, new_length: int):
        run = self.get_run_element()
        if run is not None:
            run.set("chainLength", str(new_length))
        else:
            raise ValueError("No <run> element found in the XML.")

    def update_store_every(self, new_store_every: int):
        state = self.search("//state")
        if state:
            state[0].set("storeEvery", str(new_store_every))
        else:
            raise ValueError("No <state> element found in the XML.")

    def update_log_every(self, new_log_every: int):
        logger = self.search("//logger[@id='tracelog']")
        if logger:
            logger[0].set("logEvery", str(new_log_every))
        else:
            raise ValueError("No <logger id='tracelog'> element found in the XML.")
        

def modify_chain(
    xml_path: str,
    new_chain_length: int = None,
    new_store_every: int = None,
    new_log_every: int = None,
    output_path: str = None
):
    """
    Modify chain parameters in the BEAST XML file.
    """
    try:
        beast_xml = BeastXMLChainManipulator(xml_path)

    except XMLLoadError as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    # Update chain parameters
    if new_chain_length is None and new_store_every is None and new_log_every is None:
        console.print("[yellow]No modifications specified. Use options to set new chain parameters.[/yellow]")
        return
    
    if new_chain_length is not None:
        beast_xml.update_chain_length(new_chain_length)
        console.print(f"[green]Updated chain length to {new_chain_length}[/green]")

    if new_store_every is not None:
        beast_xml.update_store_every(new_store_every)
        console.print(f"[green]Updated storeEvery to {new_store_every}[/green]")

    if new_log_every is not None:
        beast_xml.update_log_every(new_log_every)
        console.print(f"[green]Updated logEvery to {new_log_every}[/green]")

    # Save file
    beast_xml.save(output_path)
    console.print(f"[bold green]Chain parameters updated and saved to {output_path}[/bold green]")