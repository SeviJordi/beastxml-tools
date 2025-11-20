from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from beastxml_tools.utils.xml_loader import load_xml, save_xml, XMLLoadError

console = Console()


SUPPORTED_DISTS = {
    "LogNormal": ["M", "S"],
    "Beta": ["alpha", "beta"],
    "Uniform":[],
    "Exponential": ["mean"],
    "OneOnX": []
}

def modify_prior(xml_path: str, prior_id: str, output_path: str = None):
    """
    Interactively modify a prior in a BEAST XML file.
    """

    try:
        tree, root = load_xml(xml_path)
    except XMLLoadError as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    # Find the prior by id
    priors = []
    priors_dist = [ x for x in root.xpath(f"//distribution[@id='{prior_id}']") if x.get("x") is not None ]
    priors_pri  = [ x for x in root.xpath(f"//prior[@id='{prior_id}']") if x.get("x") is None ]
    priors.extend(priors_dist)
    priors.extend(priors_pri)
    if not priors:
        console.print(f"[red]No prior found with id '{prior_id}'[/red]")
        return

    if len(priors) > 1:
        console.print(f"[yellow]Multiple priors found with id '{prior_id}'. Using the first one.[/yellow]")
        return
    
    prior = priors[0]
    # Summary of current prior
    console.print(f"[bold cyan]Current prior '{prior_id}':[/bold cyan]")
    # Show current distribution
    current_dist = None
    for child in prior.xpath("./*"):
        current_dist = child.tag
        break
    if current_dist:
        console.print(f"  Distribution: [green]{current_dist}[/green]")
    else:
        console.print("  Distribution: [red]None found[/red]")
    
    # parameters
    params = {}
    for child in prior.xpath("./*"):
        for param in child.xpath("./parameter"):
            params[param.get("name")] = param.text
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
        value = Prompt.ask(f"Enter new value for {param}")
        new_params[param] = value

    # Replace the nested distribution with new parameters
    # Remove old nested distributions
    for child in prior.xpath("./*"):
        prior.remove(child)

    # Create new nested distribution
    from lxml import etree
    new_elem = etree.Element(selected_dist)
    new_elem.set("id", f"{selected_dist}DistributionModel.1")
    new_elem.set("name", "distr")
    # ask for an optional offset
    offset = Prompt.ask("Enter offset value (or leave blank for none)", default="")
    if offset:
        new_elem.set("offset", offset)


    for pname, pval in new_params.items():
        p_elem = etree.Element("parameter")
        p_elem.set("id", f"RealParameter.{pname}")
        p_elem.set("spec", "parameter.RealParameter")
        p_elem.set("name", pname)
        p_elem.set("estimate", "false")
        p_elem.text = pval
        new_elem.append(p_elem)

    prior.append(new_elem)

    # Save file
    output_file = output_path or xml_path
    save_xml(tree, output_file)
    console.print(f"[bold green]Prior '{prior_id}' updated and saved to {output_file}[/bold green]")