import re
import sys
from enum import Enum
from pathlib import Path
from semver import VersionInfo

class BumpType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE = "pre"
    POST = "post"

TO_REPLACE = (
    'version="',
    "composio_core==",
    "composio_langchain==",
    "composio_crewai==",
    "composio_autogen==",
    "composio_lyzr==",
    "composio_openai==",
    "composio_claude==",
    "composio_griptape==",
    "composio_langgraph==",
    "composio_praisonai==",
    "composio_camel==",
    "composio_google==",
)

def _get_bumped_version(current: VersionInfo, btype: BumpType) -> VersionInfo:
    return {
        BumpType.MAJOR: current.bump_major,
        BumpType.MINOR: current.bump_minor,
        BumpType.PATCH: current.bump_patch,
        BumpType.PRE: current.bump_prerelease,
        BumpType.POST: lambda: current.bump_build(token="post"),
    }[btype]()

def _bump_version_in_file(file: Path, bump_type: BumpType, pattern: str, to_replace: str) -> None:
    content = file.read_text(encoding="utf-8")
    version_str = re.search(pattern, content).group(1)
    version = VersionInfo.parse(version=version_str)
    updated_version = _get_bumped_version(current=version, btype=bump_type)
    content = content.replace(f"{to_replace}{version}", f"{to_replace}{updated_version}")
    file.write_text(content, encoding="utf-8")
    print(f"Bumped {file} to {updated_version}")

def _bump_files(bump_type: BumpType, file_patterns: list, pattern: str, to_replace: str) -> None:
    cwd = Path.cwd()
    for file_pattern in file_patterns:
        for file in cwd.glob(file_pattern):
            _bump_version_in_file(file, bump_type, pattern, to_replace)

def bump(bump_type: BumpType) -> None:
    file_patterns = [
        "setup.py", "swe/setup.py", "plugins/**/setup.py", "dockerfiles/**/Dockerfile*"
    ]
    for pattern, to_replace in zip([r'version="(.*)",', r"composio-core\[all\]==(\d+.\d+.\d+)"], TO_REPLACE):
        _bump_files(bump_type, file_patterns, pattern, to_replace)

if __name__ == "__main__":
    bump_type = BumpType(sys.argv[1].replace("--", ""))
    bump(bump_type)
