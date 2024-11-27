from rich.table import Table
from rich.console import Console

def print_song_details(title, user, link):
    """
    Print a song's title, artist, and URLs in a visually appealing way.

    Args:
        title (str): The title of the song.
        artist (str): The name of the artist.
        urls (list): A list of URLs associated with the song.
    """
    console = Console()
    
    # Create a rich table
    table = Table(title="Song Details", title_style="bold cyan")
    
    # Add columns
    table.add_column("Attribute", style="bold magenta", justify="right")
    table.add_column("Details", style="bold white")
    
    # Add rows for title and artist
    table.add_row("Title", title)
    table.add_row("User", user)
    table.add_row("Link", link)
    
    # Print the table
    console.print(table)

def print_urls(urls):
    """
    Print a list of URLs in a visually appealing way.

    Args:
        urls (list): A list of URLs to print.
    """
    console = Console()
    
    # Create a rich table
    table = Table(title="URLs", title_style="bold cyan")
    
    # Add columns
    table.add_column("URL", style="bold white")
    
    # Add rows for each URL
    for url in urls:
        table.add_row(url)
    
    # Print the table
    console.print(table)