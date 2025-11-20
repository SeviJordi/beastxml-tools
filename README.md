# 🧬 BEAST XML Tools

`beastxml-tools` is a Python command-line tool for analyzing and modifying BEAST XML files.  
It provides easy-to-use commands for **validation, summarization, and prior modification**.

---

## ⚡ Features

- **Validate XML**: Check if a BEAST XML file is well-formed and has the required BEAST elements.  
- **Summarize XML**: Extract key information such as taxa, substitution models, clock models, tree priors, and MCMC chain settings.  
- **Detailed Priors**: Summarize prior distributions and parameters with the `--prior` flag.  
- **Modify Priors**: Interactively update priors in the XML, choosing a distribution and specifying new parameter values.  

---

## 📦 Installation

Requires Python 3.9+.

```bash
# Clone the repository
git clone https://github.com/sevijordi/beastxml-tools.git
cd beastxml-tools

# Install in editable mode with pip
pip install -e .
```
---

## 🛠 Usage

The CLI tool is called `beastxml`. It has three main commands: `validate`, `summarize`, and `modify-prior`.

---

### **1. Validate a BEAST XML file**

Check that the XML is well-formed and has basic BEAST elements.

```bash
beastxml validate <path-to-xml>
```

### **Summarize XML contents**

Extract key information from the BEAST XML, including taxa, substitution models, clock models, and tree priors.

```bash
beastxml summarize <path-to-xml>
```

### **3. Modify a prior**

Interactively update a prior in the XML.

```bash
beastxml modify-prior <path-to-xml> --prior-id <prior_id> --output <output-xml>
```
- `--prior-id`: The ID of the prior to modify.
- `--output`: Path to save the modified XML file.

**Steps performed by the command:**

1. Lists available nested distributions for the prior.  
2. Prompts you to select a distribution.  
3. Prompts you to enter new parameter values.  
4. Saves the modified XML to the specified output file.