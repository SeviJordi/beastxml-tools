
class distribution:

    SUPPORTED_DISTS = {
        "LogNormal": ["M", "S"],
        "Beta": ["alpha", "beta"],
        "Uniform": [],
        "Exponential": ["mean"],
        "OneOnX": [],
    }

    def __init__(self, name):
        self._name = name
        self._required_params = None
    
    @property
    def name(self):
        return self._name
    
    
class LogNormal(distribution):
    def __init__(self):
        super().__init__("LogNormal")
        self.required_params = {"M", "S"}


class Beta(distribution):
    def __init__(self):
        super().__init__("Beta")
        self.required_params = {"alpha", "beta"}


class Uniform(distribution):
    def __init__(self):
        super().__init__("Uniform")
        self.required_params = {}

class Exponential(distribution):
    def __init__(self):
        super().__init__("Exponential")
        self.required_params = {"mean"}

class OneOnX(distribution):
    def __init__(self):
        super().__init__("OneOnX")
        self.required_params = {}


class DistributionManager:
    def __init__(self, *distributions):
        self.distros = distributions

    def find_distro_by_name(self, name):
        for distro in self.distros:
            if distro.name == name:
                return distro
        
        return None
    
    def summarise_distros(self):
        return {dist.name: list(dist.required_params) for dist in self._distros}
    


