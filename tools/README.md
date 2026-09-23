# Vendored tools

## `ra-logix-designer-vcs-custom-tools/`

Rockwell Automation's `l5xgit` / `l5xplode` command-line tools, MIT-licensed
(`ra-logix-designer-vcs-custom-tools/LICENSE`). `scripts/batch_l5x_to_acd.ps1`
uses `l5xgit l5x2acd` to convert every generated L5X into an ACD for capture.

The source is copied into this repository rather than referenced, so the capture
pipeline builds from a fresh clone with nothing else to fetch or remember.

| | |
|---|---|
| upstream | https://github.com/RockwellAutomation/ra-logix-designer-vcs-custom-tools |
| commit | `923a9675a53637515c8a5088ff7eed41a9b3eb82` |
| omitted | `e2e_tests/` — upstream's own Pester suite; its L5X fixtures fall under this repository's `*.L5X` ignore rule and nothing here runs it |
| local changes | none |

**Build:** `scripts/build_l5xgit.ps1`. `batch_l5x_to_acd.ps1` calls it on first use
when `-L5xGitPath` is not given, so building by hand is optional. The executable
lands in `ra-logix-designer-vcs-custom-tools/artifacts/bin/Release/l5xgit.exe`,
which upstream's own `.gitignore` keeps out of git.

**Machine prerequisites that cannot be vendored:**

- **.NET 10 SDK.**
- **Studio 5000 Logix Designer and the Logix Designer SDK 2.2+.** The build
  restores `RockwellAutomation.LogixDesigner.CSClient` from the SDK's local NuGet
  folder, `C:\Users\Public\Documents\Studio 5000\Logix Designer SDK\dotnet`
  (see `nuget.config`). That package is proprietary and ships only with the SDK
  install.

**Updating:** replace the folder with a newer upstream tree (`git archive` of the
wanted commit, minus `e2e_tests/`), update the commit above, and rebuild with
`build_l5xgit.ps1 -Force`.
