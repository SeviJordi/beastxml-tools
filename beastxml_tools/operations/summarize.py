from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from beastxml_tools.utils.xml_loader import BeastXML, XMLLoadError

console = Console()


class BeastXMLSummarizer:
    """
    Class of BeastXML to add summarization methods.
    """

    def __init__(self, xml: BeastXML):
        self.xml = xml
        self.chain = {"length": 0, "storeEvery": 0, "logEvery": 0}

        self.sequences = {"ntaxa": 0, "states": 0, "aln_len": 0}
        self.clock_models = []
        self.substitution_models = []
        self.parameters = []
        self.priors = []
        self.summarize()

    def summarize(self):
        """
        Summarize important components of the BEAST XML file.
        """

        # Taxa
        taxa = self.xml.search("//sequence")
        self.sequences["ntaxa"] = len(taxa)
        self.sequences["states"] = taxa[0].get("totalcount") if taxa else "Unknown"
        self.sequences["aln_len"] = len(taxa[0].get("value")) if taxa else "Unknown"
        filtered = self.xml.search("//data[@spec='FilteredAlignment']")
        if filtered:
            constant_sites = map(int, filtered[0].get("constantSiteWeights").split())
            self.sequences["aln_len"] += sum(constant_sites)

        # Chain length in <run> element(s)
        runs = self.xml.search("//run")
        self.chain["length"] = runs[0].get("chainLength") if runs else "Unknown"
        self.chain["storeEvery"] = (
            self.xml.search("//state")[0].get("storeEvery") if runs else "Unknown"
        )
        self.chain["logEvery"] = (
            self.xml.search("//logger[@id='tracelog']")[0].get("logEvery")
            if self.xml.search("//logger[@id='tracelog']")
            else "Unknown"
        )

        # Clock models
        self.clock_models = self.get_clock_models()

        # Substitution models
        self.substitution_models = self.get_substitution_models()

        # Parameters
        self.parameters = self.extract_params()

        # Priors
        self.priors = self.extract_priors()

    def get_clock_models(self):
        models = []
        branch_rate_model = self.xml.search("//branchRateModel")
        clock_model = (
            branch_rate_model[0].get("spec").split(".")[-1]
            if branch_rate_model
            else "Unknown"
        )
        if branch_rate_model:
            models.append(f"{clock_model} (id={branch_rate_model[0].get('id')})")
        else:
            models.append("None found")
        return models

    def get_substitution_models(self):
        models = []
        subt_model = (
            self.xml.search("//substModel")[0].get("spec")
            if self.xml.search("//substModel")
            else "Unknown"
        )
        has_gamma = bool(self.xml.search("//siteModel")[0].get("shape"))
        has_invariants = bool(
            self.xml.search("//siteModel")[0].get("proportionInvariant")
        )
        if has_gamma and has_invariants:
            subt_model += "+G+I"
        elif has_gamma:
            subt_model += "+G"
        elif has_invariants:
            subt_model += "+I"
        models.append(
            f"{subt_model} (id={self.xml.search('//substModel')[0].get('id')})"
            if self.xml.search("//substModel")
            else "None found"
        )
        return models

    def extract_params(self):
        params = []

        for p in self.xml.search("//parameter[@name='stateNode']"):
            upper = p.get("upper", "Undefined")
            lower = p.get("lower", "Undefined")
            param_info = {
                "name": p.get("id", "unknown"),
                "value": p.text.strip() if p.text else "None",
                "upper": upper,
                "lower": lower,
            }
            params.append(param_info)

        return params

    def extract_priors(self):
        prior_block = self.xml.search("//distribution[@id='prior']")

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
                    "parameters": [],
                }

                # parameters inside this distribution
                for p in dist.xpath(".//parameter"):
                    pname = p.get("name", p.tag)
                    value = p.text.strip() if p.text else "None"

                    prior_info["parameters"].append({"name": pname, "value": value})

                priors.append(prior_info)

        for dist in self.xml.search("//prior"):
            if dist.get("x") is not None:
                prior_info = {
                    "id": dist.get("id", "unknown"),
                    "x": dist.get("x", "unknown"),
                    "type": dist.xpath("./*[not(self::parameter)][1]")[0].tag,
                    "parameters": [],
                }

                # parameters inside this distribution
                for p in dist.xpath(".//parameter"):
                    pname = p.get("name", p.tag)
                    value = p.text.strip() if p.text else "None"

                    prior_info["parameters"].append({"name": pname, "value": value})

                priors.append(prior_info)

        return priors


def summarize_xml(path: str):
    """
    Summarize important components of a BEAST XML file.
    """
    console.print(f"[bold cyan]Summarizing:[/bold cyan] {path}")

    try:
        beast_xml = BeastXML(path)
        summarizer = BeastXMLSummarizer(beast_xml)
    except XMLLoadError as e:
        console.print(Panel.fit(str(e), title="❌ XML Error", style="bold red"))
        return

    # ================
    # Display results
    # ================
    # title="📌 Overview"
    beast_overview = f"[bold green]Beast version:[/bold green] [bold cyan]{beast_xml.beast_version}[bold cyan]"

    beast_overview += f"\n[bold green]Packages:[/bold green]"

    for package in beast_xml.packages:
        beast_overview += f"\n[bold cyan]  -{package}[bold cyan]"

    console.print(
        Panel.fit(beast_overview, title="📌 BEAST Overview", style="bold purple"),
        justify="center",
    )
    console.print("\n")

    # chain info

    chain = Table(title="📊 Chain Overview", show_header=False)
    chain.add_row("Chain length:", str(summarizer.chain["length"]))
    chain.add_row("Store every:", str(summarizer.chain["storeEvery"]))
    chain.add_row("Log every:", str(summarizer.chain["logEvery"]))

    console.print(chain, justify="center")

    # sequences
    seq_table = Table(title="🧬 Sequence Data", show_header=False)
    seq_table.add_row("Number of taxa:", str(summarizer.sequences["ntaxa"]))
    seq_table.add_row("Number of states:", str(summarizer.sequences["states"]))
    seq_table.add_row("Alignment length:", str(summarizer.sequences["aln_len"]))
    console.print(seq_table, justify="center")

    # Clock models
    table_clock = Table(title="⏱ Clock Models")
    table_clock.add_column("Models")

    for cm in summarizer.clock_models:
        table_clock.add_row(cm)

    console.print(table_clock, justify="center")

    # Substitution models
    table_sub = Table(title="🧬 Substitution Models")
    table_sub.add_column("Models")

    for sm in summarizer.substitution_models:
        table_sub.add_row(sm)

    console.print(table_sub, justify="center")

    # Parameters
    params = summarizer.parameters

    if not params:
        console.print(
            Panel("No model parameters found", title="❌ Parameters", style="red"),
            justify="center",
        )
        return

    table_params = Table(title="⚙️ Model Parameters")
    table_params.add_column("Parameter ID")
    table_params.add_column("Initial Value")
    table_params.add_column("Lower Bound")
    table_params.add_column("Upper Bound")
    for p in params:
        table_params.add_row(p["name"], p["value"], p["lower"], p["upper"])

    console.print(table_params, justify="center")

    # priors
    priors = summarizer.priors

    if not priors:
        console.print(Panel("No priors found", title="❌ Priors", style="red"))
        return

    table = Table(title="📘 Priors (Detailed)")
    table.add_column("Prior ID")
    table.add_column("Parameter")
    table.add_column("Distribution")

    for pr in priors:
        param_text = ", ".join(
            f"[bold]{p['name']}[/bold] = {p['value']}" for p in pr["parameters"]
        )

        distr_def = pr["type"] + f" ({param_text})" if param_text else pr["type"]
        table.add_row(pr["id"], pr["x"], distr_def)

    console.print(table, justify="center")
    return
