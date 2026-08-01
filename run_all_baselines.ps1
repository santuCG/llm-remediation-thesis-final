$scenarios = @("AF-01","AF-02","AF-03","AF-04","AF-05","AF-06","AF-07","AF-08","AF-09",
               "JS-02","JS-03","JS-04","JS-05","JS-06","JS-07")
foreach ($s in $scenarios) {
    gh_cli\bin\gh.exe workflow run "baseline-$($s.ToLower()).yml" --ref feature/reproducible-platform
}
