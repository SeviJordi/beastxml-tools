import typer
from beastxml_tools.operations.validate import validate_xml
from beastxml_tools.operations.summarize import summarize_xml
from beastxml_tools.operations.modify_prior import modify_prior as modify_prior_func
from beastxml_tools.operations.prior_inspector import inspect_prior as inspect_prior_func
from beastxml_tools.operations.modify_chain import modify_chain as modify_chain_func

# default output is stdout

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
    summarize_xml(path)

@app.command()
def modify_prior(
    path: str = typer.Argument(..., help="Path to the BEAST XML file."),
    prior_id: str = typer.Option(..., "--prior-id", "-id", help="ID of the prior to modify in the XML file."),
    output: str = typer.Option(
        ..., "--output", "-o",
        help="Output file path. If not provided, the input file is overwritten."
    )
):
    """
    Interactively modify a prior in a BEAST XML file.
    """
    modify_prior_func(path, prior_id, output)

@app.command()
def inspect_prior():
    """
    Interactively inspect a probability distribution.

    Lists available distributions, prompts for parameters,
    then outputs summary statistics and a plot of the distribution.
    """
    inspect_prior_func()

@app.command()
def modify_chain(
    xml_path: str = typer.Argument(..., help="Path to the BEAST XML file."),
    new_chain_length: int = typer.Option(None, "--chain-length", "-cl", help="New chain length."),
    new_store_every: int = typer.Option(None, "--store-every", "-se", help="New store every value."),
    new_log_every: int = typer.Option(None, "--log-every", "-le", help="New log every value."),
    output_path: str = typer.Option(
        ..., "--output", "-o",
        help="Output file path. If not provided, the input file is overwritten."
    )
):
    """
    Modify chain parameters in a BEAST XML file.
    """
    modify_chain_func(
        xml_path,
        new_chain_length,
        new_store_every,
        new_log_every,
        output_path
    )

if __name__ == "__main__":
    app()