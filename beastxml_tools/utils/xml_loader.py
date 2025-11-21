from lxml import etree
from pathlib import Path
from sys import stdout
from io import StringIO


class XMLLoadError(Exception):
    """Custom exception for XML loading issues."""

    pass


class PrivateAttributeError(Exception):
    """Custom exception for private attribute access issues."""

    pass


class NoOutputPathError(Exception):
    """Custom exception for missing output path."""

    pass


class BeastXML:

    SUPPORTED_DISTS = {
        "LogNormal": ["M", "S"],
        "Beta": ["alpha", "beta"],
        "Uniform": [],
        "Exponential": ["mean"],
        "OneOnX": [],
    }

    def __init__(self, path: str):
        self.path = Path(path)
        self._tree = None
        self._root = None
        self._beast_version = None
        self._packages = []
        self.load()

    # Getters and setters
    @property
    def tree(self):
        return self._tree

    @property
    def root(self):
        return self._root

    @property
    def beast_version(self):
        return self._beast_version

    @property
    def packages(self):
        return self._packages

    @root.setter
    def root(self, value):
        raise PrivateAttributeError("Direct modification of 'root' is not allowed.")

    @tree.setter
    def tree(self, value):
        raise PrivateAttributeError("Direct modification of 'tree' is not allowed.")

    @beast_version.setter
    def root(self, value):
        raise PrivateAttributeError(
            "Direct modification of 'beast_version' is not allowed."
        )

    @packages.setter
    def tree(self, value):
        raise PrivateAttributeError("Direct modification of 'packages' is not allowed.")

    def load(self):
        """
        Load and parse the BEAST XML file.
        """
        if not self.path.exists():
            raise XMLLoadError(f"File does not exist: {self.path}")

        try:
            parser = etree.XMLParser(remove_blank_text=True)
            self._tree = etree.parse(str(self.path), parser)
            self._root = self._tree.getroot()
            self._beast_version = self.search("//beast")[0].get("version")
            self._packages = self.search("//beast")[0].get("required").split(":")

        except etree.XMLSyntaxError as e:
            raise XMLLoadError(f"XML syntax error in {self.path}: {e}") from e

    def save(self, output_path: str = None):
        """
        Save the XML tree back to file with pretty formatting.
        """
        try:
            assert output_path is not None
        except AssertionError:
            raise NoOutputPathError("Output path must be specified to save the XML.")

        self._tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )

    def search(self, xpath: str):
        """
        Search the XML tree using an XPath expression.
        """
        return self._root.xpath(xpath)

    def get_all_ids(self):
        ids = []
        for elem in self.search("//*[@id]"):
            eid = elem.get("id")
            if eid:
                ids.append(eid)
        return ids
