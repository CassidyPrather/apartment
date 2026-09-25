#!/usr/bin/env bash
# Formats (or, with --check, verifies) the CI-visible C# via dotnet-format over
# the same synthesized project scripts/test.sh uses. Editor-only code is out of
# scope here the same way it is out of scope for the headless tests.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

scripts/gen-testproj.sh
if [ ! -f dist/testproj/PackageTests.csproj ]; then
    echo "format: no CI-visible sources; nothing to do"
    exit 0
fi

if [ "${1:-}" = "--check" ]; then
    dotnet format whitespace dist/testproj/PackageTests.csproj --verify-no-changes
else
    dotnet format whitespace dist/testproj/PackageTests.csproj
fi
