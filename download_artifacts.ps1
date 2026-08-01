$runs = gh_cli\bin\gh.exe run list --limit 100 --json name,databaseId,status,conclusion -q ".[]" | ConvertFrom-Json
foreach ($run in $runs) {
    if ($run.name -match "^Baseline (AF-\d\d|JS-\d\d)$" -and $run.conclusion -eq "success") {
        $scenario = $Matches[1].ToUpper()
        $out_dir = "results/execution_evidence_v2/$scenario"
        if (-not (Test-Path $out_dir)) {
            New-Item -ItemType Directory -Force -Path $out_dir | Out-Null
        }
        gh_cli\bin\gh.exe run download $run.databaseId --dir $out_dir
    }
}
