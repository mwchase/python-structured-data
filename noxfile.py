import os.path

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


def modified_files(session):
    for file_ in (
        session.run("hg", "status", "--modified", silent=True, external=True)
        .split("\n")
    ):
        if file_:
            yield file_[2:]


def cache_files(file_list):
    for file_ in file_list:
        dirname, fn = os.path.split(file_)
        cache_dir = os.path.join(dirname, "__pycache__")
        prefix = os.path.splitext(fn)[0] + os.extsep
        try:
            cache_files = os.listdir(cache_dir)
        except FileNotFoundError:
            continue
        for cache_file in cache_files:
            if cache_file.startswith(prefix):
                yield os.path.join(cache_dir, cache_file)


def test_files(file_list):
    for file_ in file_list:
        relpath = os.path.relpath(file_, "src")
        if relpath.startswith(os.pardir):
            continue
        if not os.path.exists(f"{file_}.bak"):
            continue
        dirname, fn = os.path.split(relpath)
        yield os.path.join("tests", dirname, f"test_{fn}")


@nox.session
def mutmut_clean(session):
    for cache_file in cache_files(modified_files(session)):
        os.remove(cache_file)


@nox.session
def mutmut_test(session):
    test_paths = tuple(test_files(modified_files(session)))
    session.install("pytest", ".")
    session.run("pytest", "-vv", *test_paths)


@nox.session
def coveralls(session):
    session.install("coveralls")
    session.run("coveralls", "[]")


@nox.session
def codecov(session):
    session.install(COVERAGE, "codecov")
    session.run("coverage", "xml", "--ignore-errors")
    session.run("codecov", "-f", "coverage.xml")


@nox.session
def bootstrap(session):
    session.install("jinja2", "matrix")
    session.run("python", "-c", """\
import os.path

import jinja2
import matrix

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join("ci", "templates")),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
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
""")
