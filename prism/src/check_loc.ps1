$files = Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    $path = $_.FullName
    if (Test-Path $path) {
        $all        = Get-Content -LiteralPath $path
        $code       = $all | Where-Object { $_.Trim() -and -not ($_.Trim().StartsWith("#")) }
        $comments   = $all | Where-Object { $_.Trim().StartsWith("#") }
        $whitespace = $all | Where-Object { -not $_.Trim() }
        
        $sections = $comments | Where-Object { $_.Trim() -match '^#( )?(-|#)+' }

        [PSCustomObject]@{
            File         = $_.Name
            TotalLines   = $all.Count
            CodeLines    = $code.Count
            CommentLines = $comments.Count
            Whitespace   = $whitespace.Count
            Sections     = $sections.Count
        }
    }
}

$totals = [PSCustomObject]@{
    File         = 'TOTAL'
    TotalLines   = ($files.TotalLines   | Measure-Object -Sum).Sum
    CodeLines    = ($files.CodeLines    | Measure-Object -Sum).Sum
    CommentLines = ($files.CommentLines | Measure-Object -Sum).Sum
    Whitespace   = ($files.Whitespace   | Measure-Object -Sum).Sum
    Sections     = ($files.Sections     | Measure-Object -Sum).Sum
}

$allRows = @($files | Sort-Object TotalLines -Descending) + "" + ($totals)
$allRows | Format-Table -AutoSize
