$ErrorActionPreference = "Stop"

Write-Host "LINE test message" -ForegroundColor Cyan
Write-Host "The access token will not be displayed or saved."
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

    $body = @{
        to = $lineUserId
        messages = @(
            @{
                type = "text"
                text = "Kayochin weather: Test message. Daily weather images will arrive here."
            }
        )
    } | ConvertTo-Json -Depth 5

    Invoke-RestMethod `
        -Uri "https://api.line.me/v2/bot/message/push" `
        -Method Post `
        -Headers @{ Authorization = "Bearer $channelAccessToken" } `
        -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($body)) | Out-Null

    Write-Host ""
    Write-Host "LINE API accepted the message. Check LINE now." -ForegroundColor Green
    Write-Host "If it did not arrive, add the official account as a friend and run this again."
}
catch {
    Write-Host ""
    Write-Host "Send failed." -ForegroundColor Red
    Write-Host $_.Exception.Message
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
