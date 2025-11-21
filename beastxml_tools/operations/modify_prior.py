from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from lxml import etree
from beastxml_tools.utils.xml_loader import BeastXML, XMLLoadError

console = Console()

SUPPORTED_DISTS = BeastXML.SUPPORTED_DISTS



class BeastXMLPriorManipulator(BeastXML):

    def find_prior_by_id(self, prior_id: str):
        priors = self.search(f"//distribution[@id='{prior_id}']")
        priors += self.search(f"//prior[@id='{prior_id}']")
        return priors
    
    def summarize_prior(self, prior):
        summary = {}
        for child in prior.xpath("./*"):
            summary['distribution'] = child.tag
            params = {}
            for param in child.xpath("./parameter"):
                params[param.get("name")] = param.text
            summary['parameters'] = params
        return summary
    
    def update_prior(self, prior, new_dist: str, new_params: dict, offset: float = None):
        # Remove old nested distributions
        for child in prior.xpath("./*"):
            prior.remove(child)

        # Create new nested distribution
        all_ids = self.get_all_ids()
        i = 1
        while True:
            new_name = f"{new_dist}DistributionModel." + str(i)
            if new_name not in all_ids:
                break
            i += 1

        new_elem = etree.Element(new_dist)
        new_elem.set("id", new_name)
        new_elem.set("name", "distr")
        if offset:
            new_elem.set("offset", offset)

        for pname, pval in new_params.items():
            p_elem = etree.Element("parameter")
            
            i = 1
            while True:
                candidate_id = f"RealParameter.{pname}." + str(i)
                if candidate_id not in all_ids:
                    break
                i += 1

            p_elem.set("id", candidate_id)
            p_elem.set("spec", "parameter.RealParameter")
            p_elem.set("name", pname)
            p_elem.set("estimate", "false")
            p_elem.text = str(pval)
            new_elem.append(p_elem)

        prior.append(new_elem)

    
def modify_prior(xml_path: str, prior_id: str, output_path: str = None):
    """
    Interactively modify a prior in a BEAST XML file.
    """

    try:
        beast_xml = BeastXMLPriorManipulator(xml_path)

    except XMLLoadError as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    # Find the prior by id
    priors = beast_xml.find_prior_by_id(prior_id)
    if not priors:
        console.print(f"[red]No prior found with id '{prior_id}'[/red]")
        return

    if len(priors) > 1:
        console.print(f"[yellow]Multiple priors found with id '{prior_id}'. Using the first one.[/yellow]")
        return
    
    prior = priors[0]

    # Summary of current prior
    summary = beast_xml.summarize_prior(prior)
    console.print(f"[bold cyan]Current prior '{prior_id}':[/bold cyan]")

    # Show current distribution
    current_dist = summary.get('distribution', None)
    if current_dist:
        console.print(f"  Distribution: [green]{current_dist}[/green]")
    else:
        console.print("  Distribution: [red]None found[/red]")
    
    # parameters
    params = summary.get('parameters', {})

    if params:
        console.print("  Parameters:")
        for pname, pval in params.items():
            console.print(f"    - {pname}: [yellow]{pval}[/yellow]")
    else:
        console.print("  Parameters: [red]None found[/red]")    

    console.print("\n[bold]Modify Prior[/bold]")

    # Show available distributions
    table = Table(title=f"Available distributions")
    table.add_column("Index")
    table.add_column("Distribution")
    table.add_column("Parameters")
    for i, dist in enumerate(SUPPORTED_DISTS.keys(), start=1):
        params = ", ".join(SUPPORTED_DISTS[dist]) if SUPPORTED_DISTS[dist] else "None"
        table.add_row(str(i), dist, params)
    console.print(table)

    # Ask user which distribution to apply
    choice_index = Prompt.ask("Select distribution by index", choices=[str(i) for i in range(1, len(SUPPORTED_DISTS)+1)])
    selected_dist = list(SUPPORTED_DISTS.keys())[int(choice_index)-1]
    console.print(f"You selected: [bold green]{selected_dist}[/bold green]")

    # Prompt for new parameter values
    new_params = {}
    for param in SUPPORTED_DISTS[selected_dist]:
        value = FloatPrompt.ask(f"Enter new value for {param}")
        new_params[param] = value

    # Ask for offset if applicable
    offset = FloatPrompt.ask("Enter offset value (or leave blank for none)", default="")
    offset = offset if offset else None

    # Update prior in XML
    beast_xml.update_prior(prior, selected_dist, new_params)

    # Save file
    output = output_path if output_path else xml_path
    beast_xml.save(output)
    console.print(f"[bold green]Prior '{prior_id}' updated and saved to {output}[/bold green]")