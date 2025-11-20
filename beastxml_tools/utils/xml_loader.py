from lxml import etree
from pathlib import Path

class XMLLoadError(Exception):
    """Custom exception for XML loading issues."""
    pass


def load_xml(path: str):
    """
    Load and parse a BEAST XML file.

    Returns:
        tree: the parsed XML tree
        root: the root XML element
    """

    path = Path(path)

    if not path.exists():
        raise XMLLoadError(f"File does not exist: {path}")

    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(str(path), parser)
        root = tree.getroot()
        return tree, root

    except etree.XMLSyntaxError as e:
        raise XMLLoadError(f"XML syntax error in {path}: {e}") from e


def save_xml(tree, path: str):
    """
    Save the XML tree back to file with pretty formatting.
    """
    path = Path(path)

    tree.write(
        str(path),
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )