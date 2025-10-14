import sys
from pathlib import Path

import pytest

from modelship import cli


CLI_NAME = "modelship"


@pytest.fixture
def onnx_model() -> Path:
    return Path(__file__).parent / "fixtures" / "model.onnx"


@pytest.fixture
def metadata() -> Path:
    return Path(__file__).parent / "fixtures" / "metadata.yml"


def test_version(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from modelship.__about__ import __version__

    monkeypatch.setattr(
        sys,
        "argv",
        [CLI_NAME, "--version"],
    )

    with pytest.raises(SystemExit):
        cli.cli()

    captured = capsys.readouterr()
    output = captured.out
    assert __version__ in output


def test_static(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    onnx_model: Path,
    metadata: Path,
) -> None:
    output_path = tmp_path / "output"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            CLI_NAME,
            "static",
            "--output",
            str(output_path.absolute()),
            "--metadata",
            str(metadata.absolute()),
            str(onnx_model.absolute()),
        ],
    )

    cli.cli()

    expected_assets = [
        Path("index.html"),
        Path("model.onnx"),
        Path("vendor") / "bootstrap" / "bootstrap.esm.min.js",
        Path("vendor") / "bootstrap-icons" / "bootstrap-icons.min.css",
        Path("vendor") / "bootstrap-icons" / "fonts" / "bootstrap-icons.woff",
        Path("vendor") / "bootstrap-icons" / "fonts" / "bootstrap-icons.woff2",
        Path("vendor") / "halfmoon" / "halfmoon.min.css",
        Path("vendor") / "halfmoon" / "halfmoon.modern.css",
        Path("vendor") / "onnxruntime-web" / "ort-wasm-simd-threaded.jsep.wasm",
        Path("vendor") / "onnxruntime-web" / "ort.bundle.min.js",
    ]
    for asset_path in expected_assets:
        assert (output_path / asset_path).exists()
