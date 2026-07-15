$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$secretDirectory = Join-Path $projectRoot ".secrets"
$tokenPath = Join-Path $secretDirectory "line_token.dpapi"
$userIdPath = Join-Path $secretDirectory "line_user_id.txt"
$completePath = Join-Path $secretDirectory "setup_complete"

Write-Host "Save LINE settings securely" -ForegroundColor Cyan
Write-Host "The token is encrypted for your Windows account and is not shown or saved as plain text."
Write-Host ""

$secureToken = Read-Host "Paste Channel access token, then press Enter" -AsSecureString
$lineUserId = (Read-Host "Paste Your user ID (starts with U), then press Enter").Trim()

if ($lineUserId -notmatch '^U[0-9a-fA-F]{32}$') {
    throw "Invalid user ID. Enter the 33-character Your user ID that starts with U."
}

$tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
try {
    $channelAccessToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
    if ([string]::IsNullOrWhiteSpace($channelAccessToken)) {
        throw "Channel access token is empty."
    }

    Invoke-RestMethod `
        -Uri "https://api.line.me/v2/bot/info" `
        -Method Get `
        -Headers @{ Authorization = "Bearer $channelAccessToken" } | Out-Null

    New-Item -ItemType Directory -Path $secretDirectory -Force | Out-Null
    $secureToken | ConvertFrom-SecureString | Set-Content -LiteralPath $tokenPath -Encoding ASCII
    Set-Content -LiteralPath $userIdPath -Value $lineUserId -Encoding ASCII
    Set-Content -LiteralPath $completePath -Value ([DateTime]::UtcNow.ToString("O")) -Encoding ASCII

    Write-Host ""
    Write-Host "LINE settings were validated and saved." -ForegroundColor Green
}
finally {
    if ($tokenPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
    }
    Remove-Variable channelAccessToken -ErrorAction SilentlyContinue
    Remove-Variable secureToken -ErrorAction SilentlyContinue
}

Write-Host ""
Read-Host "Press Enter to close"
