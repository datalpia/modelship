import shutil
from pathlib import Path

from invoke import task
from invoke.context import Context

app_path = "modelship"
tests_path = "tests"


@task
def format(ctx: Context) -> None:
    ctx.run("ruff format .", echo=True, pty=True)


@task
def audit(ctx: Context) -> None:
    ignored_vulns = [
        "GHSA-4xh5-x5gv-qwph",  # pip<=25.2 affected, no resolution yet
    ]
    options = [f"--ignore-vuln {vuln}" for vuln in ignored_vulns]
    ctx.run(f"pip-audit {' '.join(options)}", echo=True, pty=True)


@task
def vuln(ctx: Context) -> None:
    ctx.run(f"bandit -r {app_path}", echo=True, pty=True)


@task
def lint(ctx: Context) -> None:
    ctx.run("ruff check .", echo=True, pty=True)


@task
def typing(ctx: Context) -> None:
    ctx.run(f"mypy --strict {app_path} {tests_path}", echo=True, pty=True)


@task
def test(ctx: Context) -> None:
    ctx.run(
        f"py.test -v --cov={app_path} --cov={tests_path} --cov-branch --cov-report=term-missing {tests_path}",
        echo=True,
        pty=True,
    )


@task(audit, vuln, lint, typing, test)
def qa(ctx: Context):
    pass


@task
def vendor_static_assets(ctx: Context) -> None:
    base_path = (Path(__file__).parent / "modelship" / "static" / "vendor").absolute()

    node_packages = {
        "bootstrap": [Path("dist") / "js" / "bootstrap.esm.min.js"],
        "bootstrap-icons": [
            Path("font") / "bootstrap-icons.min.css",
            Path("font") / "fonts",
        ],
        "halfmoon": [
            Path("css") / "halfmoon.min.css",
            Path("css") / "cores" / "halfmoon.modern.css",
        ],
        "onnxruntime-web": [
            Path("dist") / "ort.bundle.min.mjs",
            Path("dist") / "ort-wasm-simd-threaded.jsep.wasm",
        ],
    }

    ctx.run("npm install", echo=True, pty=True)

    for package_name, package_files in node_packages.items():
        print("vendoring package:", package_name)
        dst = base_path / package_name
        shutil.rmtree(dst, ignore_errors=True)
        dst.mkdir(parents=True, exist_ok=True)

        for package_file in package_files:
            src = Path("node_modules") / package_name / package_file
            if package_file.suffix in [".js", ".mjs"]:
                print(f"build {package_name} module: {package_file}")
                ctx.run(
                    f"node_modules/.bin/rollup {src} \
                        -o modelship/static/vendor/{package_name}/{src.with_suffix('.js').name} \
                        -f es \
                        -p @rollup/plugin-node-resolve \
                        -p @rollup/plugin-terser"
                )
            else:
                src = Path("node_modules") / package_name / package_file
                if src.is_dir():
                    print(f"copying: {src} → {dst / src.name}")
                    shutil.copytree(src, dst / src.name, dirs_exist_ok=True)
                else:
                    print(f"copying: {src} → {dst}")
                    shutil.copy(src, dst)
