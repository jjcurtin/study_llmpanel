$files = Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $path = $_.FullName
    if (Test-Path $path) {
        $all  = Get-Content -LiteralPath $path
        $code = $all | Where-Object { $_.Trim() -and -not ($_.Trim().StartsWith("#")) }
        $bloat = $all.Count - $code.Count

        [PSCustomObject]@{
            File       = $_.Name
            TotalLines = $all.Count
            CodeLines  = $code.Count
            Bloat      = $bloat
        }
    }
}

$totals = [PSCustomObject]@{
    File       = 'TOTAL'
    TotalLines = ($files.TotalLines | Measure-Object -Sum).Sum
    CodeLines  = ($files.CodeLines  | Measure-Object -Sum).Sum
    Bloat      = ($files.Bloat      | Measure-Object -Sum).Sum
}

$files | Sort-Object TotalLines -Descending
""
$totals