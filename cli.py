import typer
from sdk.client import DataStoryClient
from rich.console import Console
from rich.table import Table
import json

app = typer.Typer()
console = Console()
client = DataStoryClient()

@app.command()
def upload(file_path: str):
    """Upload a CSV dataset."""
    try:
        with console.status("Uploading..."):
            ds = client.upload_dataset(file_path)
        console.print(f"[green]Success![/green] Dataset uploaded with ID: [bold]{ds['id']}[/bold]")
        rows = ds['meta_info'].get('row_count', 'N/A')
        console.print(f"Stats: {rows} rows")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

@app.command()
def list():
    """List all datasets."""
    datasets = client.list_datasets()
    table = Table(title="My Datasets")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Created At", style="green")
    
    for d in datasets:
        table.add_row(d["id"], d["name"], d["created_at"])
    
    console.print(table)

@app.command()
def insights(dataset_id: str):
    """Generate insights for a dataset."""
    with console.status("Generating Insights..."):
        insights = client.generate_insights(dataset_id)
    
    for i in insights:
        console.print(f"[bold]{i['title']}[/bold]")
        console.print(f"{i['description']}")
        console.print(f"[dim]Confidence: {i['confidence']}[/dim]")
        console.print("-" * 20)

@app.command()
def chat(dataset_id: str, message: str):
    """Ask a question about the dataset."""
    with console.status("Thinking..."):
        res = client.chat(dataset_id, message)
    console.print(f"[bold blue]AI:[/bold blue] {res['response']}")

@app.command()
def story(dataset_id: str):
    """Generate a story for the dataset."""
    with console.status("Writing Story..."):
        res = client.generate_story(dataset_id)
    console.print(res['story'])

if __name__ == "__main__":
    app()
