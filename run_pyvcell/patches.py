import pyvcell._internal.simdata.simdata_models as sdm
import re
import traceback
import html
import ast
import pyvcell.vcml as vc
from lxml.etree import _Element
import pyvcell.vcml as vc
from lxml import etree
from pathlib import Path


def load_vcml_file_patched(vcml_file: str | Path) -> vc.Biomodel:
    """
    Load a VCML file using PatchedBiomodelVisitor.
    Logs skipped parameters in the visitor.
    """
    vcml_file = Path(vcml_file)
    with open(vcml_file, "r", encoding="utf-8") as f:
        vcml_str = f.read()

    document = vc.VCMLDocument()
    visitor = PatchedBiomodelVisitor(document)

    root = etree.fromstring(vcml_str.encode("utf-8"))
    visitor.visit(root, document)

    if visitor.skipped_parameters:
        print("Skipped parameters:", visitor.skipped_parameters)

    if visitor.document.biomodel is None:
        raise ValueError("No biomodel found in VCML file.")

    return visitor.document.biomodel


class PatchedBiomodelVisitor(vc.vcml_reader.BiomodelVisitor):
    def __init__(self, document):
        super().__init__(document)
        self.skipped_parameters = []  # store skipped parameters

    def visit_Parameter(self, element: _Element, node: vc.Model | vc.Kinetics | vc.Application) -> None:
        parent: _Element | None = element.getparent()
        if parent is None:
            raise ValueError("Parameter element has no parent")
        text: str = element.text or ""
        value: str | float = vc.vcml_reader.float_or_formula(text)
        name: str = element.get("Name", default="unnamed")
        role = element.get("Role", default="user defined")
        unit = element.get("Unit", default="tbd")

        parameter = None

        parent_tag = vc.vcml_reader.strip_namespace(parent.tag)
        if parent_tag == "ModelParameters":
            model: vc.Model = node  # type: ignore
            model_parameter = vc.ModelParameter(
                name=name, value=value, role=role, unit=unit)
            model.model_parameters.append(model_parameter)
            parameter = model_parameter
        elif parent_tag == "Kinetics":
            kinetics: vc.Kinetics = node  # type: ignore
            reaction_node = parent.getparent()
            if reaction_node is None:
                raise ValueError("Kinetics element has no parent")
            reaction_name = reaction_node.get("Name", default="unknown")
            kinetics_parameter = vc.KineticsParameter(
                name=name, value=value, role=role, unit=unit, reaction_name=reaction_name
            )
            kinetics.kinetics_parameters.append(kinetics_parameter)
            parameter = kinetics_parameter
        else:
            # Log skipped parameters
            self.skipped_parameters.append({
                "name": name,
                "parent_tag": parent_tag,
                "text": text
            })
            # Do not raise an error; just skip
            return

        self.generic_visit(element, parameter)


# keep original so you can restore if needed
_original_NamedFunction_init = getattr(sdm.NamedFunction, "__init__", None)


def _translate_vcell_to_python(expr: str) -> str:
    if expr is None:
        return ""
    s = html.unescape(expr)
    s = s.replace("^", "**")
    s = s.replace("&&", " and ")
    s = s.replace("||", " or ")
    # replace standalone '!' not followed by '='
    s = re.sub(r'!(?!=)', ' not ', s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _patched_NamedFunction_init(self, name: str, vcell_expression: str, variable_type=None):
    # store raw inputs for debugging
    self.name = name
    self.vcell_expression = vcell_expression

    python_expr = _translate_vcell_to_python(vcell_expression)
    try:
        ast.parse(python_expr)
        self.python_expression = python_expr
        self.variable_type = variable_type
    except SyntaxError:
        print("\n[patches] failed to parse expression after translation.")
        print(f"  NamedFunction name: {name!r}")
        print(f"  original vcell_expression: {vcell_expression!r}")
        print(f"  translated python_expression: {python_expr!r}")
        print("  Traceback from ast.parse:")
        traceback.print_exc()
        # fallback: set a safe default (or re-raise if you prefer)
        # I'll set a harmless default so simulation can continue:
        self.python_expression = "0"
        self.variable_type = variable_type


# Apply the patch immediately on module import
sdm.NamedFunction.__init__ = _patched_NamedFunction_init

# convenience loader using PatchedBiomodelVisitor if you created one earlier:


def load_vcml_file_patched(vcml_path):
    """
    Simple wrapper that parses the VCML and returns a Biomodel using
    the patched NamedFunction behavior. If you also created a PatchedBiomodelVisitor,
    call that instead. This uses lxml to parse and the regular BiomodelVisitor logic,
    so it behaves similarly to original load_vcml_file.
    """
    vcml_path = Path(vcml_path)
    with open(vcml_path, "r", encoding="utf-8") as f:
        vcml_str = f.read()
    document = vc.VCMLDocument()
    # Use the original VcmlReader's visitor machinery:
    from pyvcell.vcml.vcml_reader import BiomodelVisitor  # still fine to use
    root = etree.fromstring(vcml_str.encode("utf-8"))
    visitor = BiomodelVisitor(document)
    visitor.visit(root, document)
    if visitor.document.biomodel is None:
        raise ValueError("No biomodel found")
    return visitor.document.biomodel


def verify_patch():
    """Return True if the patch is installed (i.e., NamedFunction.__init__ is patched)."""
    return getattr(sdm.NamedFunction, "__init__", None) is _patched_NamedFunction_init


# print a tiny confirmation so importing patches is visible
print("[patches] applied: NamedFunction.__init__ patched")
