import os.path

import jinja2
import matrix
import nox

nox.options.reuse_existing_virtualenvs = True

DEFAULTS = []

nox.options.sessions = DEFAULTS


COVERAGE = "coverage==5.0a8"


def default(session):
    DEFAULTS.append(session.__name__)
    return session


@default
@nox.session
def clean(session):
    session.install(COVERAGE)
    session.run("coverage", "erase")


@default
@nox.session
def check(session):
    session.install(
        "docutils",
        "check-manifest",
        "flake8",
        "readme-renderer",
        "pygments",
        "isort",
        "twine",
        # "wemake-python-styleguide",
    )
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
    session.install("mypy")
    session.run("mypy", "src/structured_data")


@default
@nox.session(python=["3.7"])
def nocov(session):
    session.install("pytest", ".")
    session.run("pytest", "-vv")


@default
@nox.session(python=["3.7"])
def cover(session):
    session.install(COVERAGE, "limit-coverage", "pytest", ".")
    session.run("coverage", "run", "-m", "pytest", "-vv")
    session.run("limit-coverage")


@default
@nox.session
def report(session):
    session.install(COVERAGE)
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
    session.install("pytest", ".", "mypy")


@nox.session
def coveralls(session):
    session.install("coveralls")
    session.run("coveralls", "[]")


@nox.session
def codecov(session):
    session.install(COVERAGE, "codecov")
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
