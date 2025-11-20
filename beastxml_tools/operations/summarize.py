from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from beastxml_tools.utils.xml_loader import load_xml, XMLLoadError

console = Console()


def summarize_xml(path: str):
    """
    Summarize important components of a BEAST XML file.
    """
    console.print(f"[bold cyan]Summarizing:[/bold cyan] {path}")

    try:
        tree, root = load_xml(path)
    except XMLLoadError as e:
        console.print(Panel.fit(str(e), title="❌ XML Error", style="bold red"))
        return

    # ================
    # Collect summaries
    # ================

    ## Taxa
    taxa = root.xpath("//sequence")
    ntaxa = len(taxa)

    ## Chain length in <run> element(s)
    runs = root.xpath("//run")
    chain_length = runs[0].get("chainLength") if runs else "Unknown"

    ## Clock models
    clock_models = []
    branch_rate_model = root.xpath("//branchRateModel")
    clock_model = branch_rate_model[0].get("spec").split(".")[-1] if branch_rate_model else "Unknown"
    clock_models.append(f"{clock_model} (id={branch_rate_model[0].get('id')})" if branch_rate_model else "None found")

    if not clock_models:
        clock_models.append("None found")

    ## Substitution models
    submodels = []
    subt_model = root.xpath("//substModel")[0].get("spec") if root.xpath("//substModel") else "Unknown"
    has_gamma = bool(root.xpath("//siteModel")[0].get("shape"))
    has_invariants = bool(root.xpath("//siteModel")[0].get("proportionInvariant"))
    if has_gamma and has_invariants:
        subt_model += "+G+I"
    elif has_gamma:
        subt_model += "+G"
    elif has_invariants:
        subt_model += "+I"

    submodels.append(f"{subt_model} (id={root.xpath('//substModel')[0].get('id')})" if root.xpath("//substModel") else "None found")


    if not submodels:
        submodels.append("None found")

    ## Tree prior
    priors = extract_priors(root)

    # ================
    # Display results
    # ================

    # Overview
    overview = Table(show_header=False)
    overview.add_row("Taxa:", str(ntaxa))
    overview.add_row("Chain length:", str(chain_length))

    console.print(Panel(overview, title="📌 Overview", expand=False))


    # Clock models
    table_clock = Table(title="⏱ Clock Models")
    table_clock.add_column("Models")

    for cm in clock_models:
        table_clock.add_row(cm)

    console.print(table_clock)

    # Substitution models
    table_sub = Table(title="🧬 Substitution Models")
    table_sub.add_column("Models")

    for sm in submodels:
        table_sub.add_row(sm)

    console.print(table_sub)

    # Parameters
    params = extract_params(root)

    if not params:
        console.print(Panel("No model parameters found", title="❌ Parameters", style="red"))
        return
    
    table_params = Table(title="⚙️ Model Parameters")
    table_params.add_column("Parameter ID")
    table_params.add_column("Initial Value")
    table_params.add_column("Lower Bound")
    table_params.add_column("Upper Bound")
    for p in params:
        table_params.add_row(
            p["name"],
            p["value"],
            p["lower"],
            p["upper"]
        )

    console.print(table_params)
    
    # priors
    priors = extract_priors(root)

    if not priors:
        console.print(Panel("No priors found", title="❌ Priors", style="red"))
        return

    table = Table(title="📘 Priors (Detailed)")
    table.add_column("Prior ID")
    table.add_column("Parameter")
    table.add_column("Distribution")


    for pr in priors:
        param_text = ", ".join(
            f"[bold]{p['name']}[/bold] = {p['value']}"
            for p in pr["parameters"]
        )

        distr_def = pr["type"] + f" ({param_text})" if param_text else pr["type"]
        table.add_row(pr["id"], pr["x"], distr_def)

    console.print(table)
    return

def extract_priors(root):
    """
    Extract priors, their distributions, and parameter values.
    Returns a list of dicts.
    """
    prior_block = root.xpath("//distribution[@id='prior']")

    if not prior_block:
        return []

    prior_block = prior_block[0]

    priors = []

    # each nested distribution inside <distribution id="prior">
    for dist in prior_block.xpath(".//distribution"):
        if dist.get("x") is not None:
            prior_info = {
                "id": dist.get("id", "unknown"),
                "x": dist.get("x", "unknown"),
                "type": dist.xpath("./*[not(self::parameter)][1]")[0].tag,
                "parameters": []
            }

            # parameters inside this distribution
            for p in dist.xpath(".//parameter"):
                pname = p.get("name", p.tag)
                value = p.text.strip() if p.text else "None"

                prior_info["parameters"].append(
                    {"name": pname, "value": value}
                )

            priors.append(prior_info)

# each nested distribution inside <distribution id="prior">
    for dist in root.xpath("//prior"):
        if dist.get("x") is not None:
            prior_info = {
                "id": dist.get("id", "unknown"),
                "x": dist.get("x", "unknown"),
                "type": dist.xpath("./*[not(self::parameter)][1]")[0].tag,
                "parameters": []
            }

            # parameters inside this distribution
            for p in dist.xpath(".//parameter"):
                pname = p.get("name", p.tag)
                value = p.text.strip() if p.text else "None"

                prior_info["parameters"].append(
                    {"name": pname, "value": value}
                )

            priors.append(prior_info)

    return priors


def extract_params(root):
    """
    Extract model parameters and their initial values.
    Returns a list of dicts.
    """
    params = []

    for p in root.xpath("//parameter[@name='stateNode']"):
        upper = p.get("upper", "Undefined")
        lower = p.get("lower", "Undefined")
        param_info = {
            "name": p.get("id", "unknown"),
            "value": p.text.strip() if p.text else "None",
            "upper": upper,
            "lower": lower
        }
        params.append(param_info)

    return params