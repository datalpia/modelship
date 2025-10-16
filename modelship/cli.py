import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import jinja2
import onnxruntime as ort
import pydantic
import yaml

from modelship import __about__


ModelIOType = Literal["float32", "string"]


class ModelInputMetadata(pydantic.BaseModel):
    name: str
    type: ModelIOType
    shape: list[int | None]
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: str | float | None = None


class ModelOutputMetadata(pydantic.BaseModel):
    name: str
    type: ModelIOType
    shape: list[int | None]


class ModelMetadata(pydantic.BaseModel):
    name: str
    description: str | None = None
    inputs: dict[str, ModelInputMetadata]
    outputs: dict[str, ModelOutputMetadata]


@dataclass(frozen=True)
class AppMetadata:
    app_name: str
    app_version: str
    github_repo_url: str


def inspect_model(model_path: Path) -> None:
    import onnx
    from google.protobuf.json_format import MessageToDict

    model_proto = onnx.load(model_path)
    model_metadata = MessageToDict(model_proto)

    print(model_metadata)

    session = ort.InferenceSession(str(model_path))
    metadata = session.get_modelmeta()

    print("Model file:", model_path)

    print("Metadata:")
    print("  description:", metadata.description)
    print("  domain:", metadata.domain)
    print("  version:", metadata.version)
    print("  producer name:", metadata.producer_name)
    print("  graph name:", metadata.graph_name)
    print("  graph description:", metadata.graph_description)

    print("Inputs:")
    for input_meta in session.get_inputs():
        print(f"  {input_meta.name}: type={input_meta.type}, shape={input_meta.shape}")

    print("Outputs:")
    for output_meta in session.get_outputs():
        print(f"  {output_meta.name}: type={output_meta.type}, shape={output_meta.shape}")


def generate_static_app(
    model_path: Path, metadata_path: Path, output_path: Path
) -> None:
    output_model_name = "model.onnx"

    metadata_yaml = yaml.safe_load(metadata_path.read_text())
    model_metadata = ModelMetadata.model_validate(metadata_yaml)

    # session = ort.InferenceSession(str(model_path))
    # inputs = [
    #     {"name": input_meta.name, "type": input_meta.type, "shape": input_meta.shape}
    #     for input_meta in session.get_inputs()
    # ]
    # outputs = [
    #     {"name": output_meta.name, "type": output_meta.type, "shape": output_meta.shape}
    #     for output_meta in session.get_outputs()
    # ]

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=jinja2.select_autoescape(),
    )
    template = jinja_env.get_template("onnx_runtime_web.html")
    rendered_template = template.render(
        app_metadata=AppMetadata(
            app_name="🚢 Modelship",
            app_version=__about__.__version__,
            github_repo_url="https://github.com/datalpia/modelship",
        ),
        model_path=output_model_name,
        model_metadata=model_metadata,
        model_metadata_json=model_metadata.model_dump_json(),
    )

    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "index.html").write_text(rendered_template)
    shutil.copytree(
        Path(__file__).parent / "static" / "vendor",
        output_path / "vendor",
        dirs_exist_ok=True,
    )
    shutil.copyfile(model_path, output_path / output_model_name)


def cli() -> None:
    parser = argparse.ArgumentParser(
        "modelship", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--version", action="version", version=__about__.__version__)
    subparsers = parser.add_subparsers(title="commands", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect a model for metadata and I/O", add_help=True
    )
    inspect_parser.add_argument("model", help="Path to the model", type=Path)
    inspect_parser.set_defaults(
        func=lambda x: inspect_model(x.model)
    )

    static_parser = subparsers.add_parser(
        "static", help="Generate a static web application", add_help=True
    )
    static_parser.add_argument(
        "--output",
        help="Output path for the static web application",
        type=Path,
        required=True,
    )
    static_parser.add_argument(
        "--metadata",
        help="Model metadata path (YAML)",
        type=Path,
        required=True,
    )
    static_parser.add_argument("model", help="Path to the model", type=Path)
    static_parser.set_defaults(
        func=lambda x: generate_static_app(x.model, x.metadata, x.output)
    )

    args = parser.parse_args()
    args.func(args)
