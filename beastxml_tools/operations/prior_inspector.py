from scipy.stats import lognorm, expon, beta, uniform, rv_continuous
import numpy as np
import plotly.graph_objects as go
from rich.console import Console
from rich.prompt import Prompt

console = Console()

SUPPORTED_DISTS = {
   "LogNormal": ["M", "S"],
    "Beta": ["alpha", "beta"],
    "Uniform":[],
    "Exponential": ["mean"]
}


def inspect_prior():
    """
    Interactively inspect a probability distribution.

    Steps:
    1. Show available distributions.
    2. Ask user to choose a distribution.
    3. Prompt for parameters.
    4. Compute mean, median, 2.5% and 97.5% quantiles.
    5. Plot an interactive distribution using Plotly.
    """
    # 1. Show available distributions
    console.print("[bold cyan]Available distributions:[/bold cyan]")
    for i, dist in enumerate(SUPPORTED_DISTS, 1):
        console.print(f"{i}. {dist} ({', '.join(SUPPORTED_DISTS[dist])})")

    # 2. Ask user to select a distribution
    while True:
        try:
            choice_index = int(Prompt.ask("Select distribution by index"))
            if 1 <= choice_index <= len(SUPPORTED_DISTS):
                break
            console.print("[red]Invalid index. Try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")

    dist_name = list(SUPPORTED_DISTS.keys())[choice_index - 1]
    console.print(f"[bold green]You selected:[/bold green] {dist_name}")

    # 3. Prompt for parameters
    params = {}
    for p in SUPPORTED_DISTS[dist_name]:
        while True:
            try:
                val = float(Prompt.ask(f"Enter value for {p}"))
                params[p] = val
                break
            except ValueError:
                console.print("[red]Please enter a numeric value.[/red]")

    # 4. Compute statistics
    if dist_name == "LogNormal":
        s = params["S"]
        scale = np.exp(params["M"])
        dist = lognorm(s=s, scale=scale)
    elif dist_name == "Beta":
        dist = beta(a=params["alpha"], b=params["beta"])
    elif dist_name == "Exponential":
        dist = expon(scale=1.0 / params["mean"])
    elif dist_name == "Uniform":
        dist = uniform()
    else:
        console.print("[red]Distribution not supported for statistics.[/red]")
        return

    mean = dist.mean()
    median = dist.median()
    q025, q975 = dist.ppf([0.025, 0.975])

    console.print("\n[bold cyan]Summary statistics:[/bold cyan]")
    console.print(f"Mean: {mean:.8f}")
    console.print(f"Median: {median:.8f}")
    console.print(f"2.5% quantile: {q025:.8f}")
    console.print(f"97.5% quantile: {q975:.8f}")

    # 5. Plot the distribution with Plotly
    x = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 20000)
    y = dist.pdf(x)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=dist_name))
    fig.update_layout(
        title=f"{dist_name} Distribution",
        xaxis_title="Value",
        yaxis_title="Density",
        template="plotly_white"
    )
    fig.show()


if __name__ == "__main__":
    inspect_prior()