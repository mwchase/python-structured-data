import os.path

import jinja2
import matrix
import nox

nox.options.reuse_existing_virtualenvs = True

DEFAULTS = []
VERSIONS = ["3.8"]

nox.options.sessions = DEFAULTS


COVERAGE = "coverage==5.0a8"
BUILD = None


def default(session):
    DEFAULTS.append(session.__name__)
    return session


def install_from_requirements(session, filename):
    session.install("-r", f"requirements/{filename}.txt")


def _build(session):
    global BUILD
    if BUILD is None:
        install_from_requirements(session, "wheel")
        session.run("python", "setup.py", "bdist_wheel")
        version = session.run("python", "setup.py", "--version", silent=True).strip()
        for filename in os.listdir("dist"):
            if filename.endswith(".whl") and f"-{version}-" in filename:
                BUILD = os.path.join("dist", filename)
                break


@default
@nox.session
def clean(session):
    install_from_requirements(session, "coverage")
    session.run("coverage", "erase")


@default
@nox.session
def check(session):
    install_from_requirements(session, "check")
    session.run("python", "setup.py", "sdist")
    session.run("python", "setup.py", "bdist_wheel")
    session.run("twine", "check", "dist/*")
    session.run("check-manifest", ".")
    session.run("flake8", "src", "tests", "setup.py")
    session.run(
        "isort",
        "--verbose",
        "--check-only",
        "--diff",
        "--recursive",
        "src",
        "tests",
        "setup.py",
    )


@default
@nox.session
def mypy(session):
    install_from_requirements(session, "mypy")
    session.run("mypy", "src/structured_data")


@default
@nox.session
def build(session):
    _build(session)


@default
@nox.session(python=VERSIONS)
def nocov(session):
    _build(session)
    session.install("--upgrade", BUILD)
    install_from_requirements(session, "pytest")
    session.run("pytest", "-vv")


@default
@nox.session(python=VERSIONS)
def cover(session):
    _build(session)
    session.install("--upgrade", BUILD)
    install_from_requirements(session, "cover")
    session.run("coverage", "run", "--append", "-m", "pytest", "-vv")


@default
@nox.session
def report(session):
    install_from_requirements(session, "report")
    session.run("limit-coverage")
    session.run("coverage", "html", "--show-contexts")
    session.run("coverage", "report", "--skip-covered", "-m", "--fail-under=100")


@default
@nox.session
def docs(session):
    session.install("-r", "docs/requirements.txt")
    session.run("sphinx-build", "-E", "-b", "html", "docs", "dist-docs")
    session.run("sphinx-build", "-b", "linkcheck", "docs", "dist-docs")


@nox.session
def mutmut_install(session):
    install_from_requirements(session, "mutmut_install")
    session.install("-e", ".")


@nox.session
def coveralls(session):
    install_from_requirements(session, "coveralls")
    session.run("coveralls", "[]")


@nox.session
def codecov(session):
    install_from_requirements(session, "codecov")
    session.run("coverage", "xml", "--ignore-errors")
    session.run("codecov", "-f", "coverage.xml")


@nox.session(python=False)
def bootstrap(session):
    del session  # Unused
    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join("ci", "templates")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    nox_environments = {}

    for (alias, conf) in matrix.from_file("setup.cfg").items():
        python = conf["python_versions"]
        deps = conf["dependencies"]
        nox_environments[alias] = {
            "python": "python" + python if "py" not in python else python,
            "deps": deps.split(),
        }
        if "coverage_flags" in conf:
            cover = {"false": False, "true": True}[conf["coverage_flags"].lower()]
            nox_environments[alias].update(cover=cover)
        if "environment_variables" in conf:
            env_vars = conf["environment_variables"]
            nox_environments[alias].update(env_vars=env_vars.split())

    for name in os.listdir(os.path.join("ci", "templates")):
        with open(name, "w") as fh:
            fh.write(jinja.get_template(name).render(nox_environments=nox_environments))
        print("Wrote {}".format(name))
    print("DONE.")
