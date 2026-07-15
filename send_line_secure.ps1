param(
    [Parameter(Mandatory = $true, ParameterSetName = "Image")]
    [string]$ImageUrl,

    [Parameter(Mandatory = $true, ParameterSetName = "Text")]
    [string]$Text
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$tokenPath = Join-Path $projectRoot ".secrets\line_token.dpapi"
$userIdPath = Join-Path $projectRoot ".secrets\line_user_id.txt"

if (-not (Test-Path -LiteralPath $tokenPath) -or -not (Test-Path -LiteralPath $userIdPath)) {
    throw "LINE settings are missing. Run setup_line_secrets.ps1 first."
}

$secureToken = Get-Content -LiteralPath $tokenPath -Raw | ConvertTo-SecureString
$lineUserId = (Get-Content -LiteralPath $userIdPath -Raw).Trim()
$tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)

try {
    $channelAccessToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
    if ($PSCmdlet.ParameterSetName -eq "Image") {
        $messages = @(
            @{
                type = "image"
                originalContentUrl = $ImageUrl
                previewImageUrl = $ImageUrl
            }
        )
    }
    else {
        $messages = @(@{ type = "text"; text = $Text })
    }

    $body = @{ to = $lineUserId; messages = $messages } | ConvertTo-Json -Depth 5
    Invoke-RestMethod `
        -Uri "https://api.line.me/v2/bot/message/push" `
        -Method Post `
        -Headers @{ Authorization = "Bearer $channelAccessToken" } `
        -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($body)) | Out-Null
}
finally {
    if ($tokenPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
    }
    Remove-Variable channelAccessToken -ErrorAction SilentlyContinue
    Remove-Variable secureToken -ErrorAction SilentlyContinue
}
