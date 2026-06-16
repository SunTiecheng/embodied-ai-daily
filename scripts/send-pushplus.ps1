param(
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [Parameter(Mandatory = $true)]
    [string]$Content,
    [string]$Token = $env:PUSHPLUS_TOKEN
)

if (-not $Token) {
    Write-Error "Set PUSHPLUS_TOKEN env var or pass -Token"
    exit 1
}

$body = @{
    token    = $Token
    title    = $Title
    content  = $Content
    template = "html"
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod -Uri "https://www.pushplus.plus/send" -Method Post -Body $body -ContentType "application/json; charset=utf-8"
$response | ConvertTo-Json
