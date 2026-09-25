#!/usr/bin/env bash
# Synthesizes dist/testproj/PackageTests.csproj from every committed package's
# SDK-free core (Runtime/Core/) and test sources (Tests/), so plain dotnet can
# compile and run them without Unity. Regenerated on every run; dist/ never
# gets committed.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

sources=$(git ls-files -- '*.cs' | grep -E '^Packages/[^/]+/(Runtime/Core|Tests)/' || true)

rm -rf dist/testproj
if [ -z "$sources" ]; then
    exit 0
fi

mkdir -p dist/testproj
{
    cat <<'EOF'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <!-- Unity 2022.3 compiles C# 9; CI must reject syntax the editor would. -->
    <LangVersion>9.0</LangVersion>
    <IsPackable>false</IsPackable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <!-- NUnit 3 to match the Unity Test Framework; 4.x drops the classic asserts. -->
    <PackageReference Include="NUnit" Version="3.14.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
  </ItemGroup>
  <ItemGroup>
EOF
    printf '%s\n' "$sources" | sed 's|.*|    <Compile Include="../../&" />|'
    cat <<'EOF'
  </ItemGroup>
</Project>
EOF
} > dist/testproj/PackageTests.csproj
