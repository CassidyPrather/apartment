#!/usr/bin/env bash
# Runs the SDK-free tests with plain dotnet + NUnit -- no Unity license, no
# editor, no VRChat SDK. The same test sources run in the editor's Test Runner;
# SKILL.md has the boundary rules.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

scripts/gen-testproj.sh
if [ ! -f dist/testproj/PackageTests.csproj ]; then
    # A gutted, package-less repo must stay green; silence would read as a bug.
    echo "test: no CI-testable sources under Packages/*/Runtime/Core or Packages/*/Tests; nothing to do"
    exit 0
fi

dotnet test dist/testproj/PackageTests.csproj
