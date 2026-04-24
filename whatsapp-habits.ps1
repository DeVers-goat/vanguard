# Morning Habit Reminder via Twilio SMS
$accountSid  = "ACd12ffcd61942046f4c322a90c0e6f7c6"
$authToken   = "35547649bfe760078ce94720f86a6b9f"
$fromNumber  = "whatsapp:+14155238886"
$toNumber    = "whatsapp:+972549715522"

$habitsFile = "c:\RanClaude\habits.json"

if (-not (Test-Path $habitsFile)) {
    Write-Output "habits.json not found"
    exit 1
}

$habits = Get-Content $habitsFile -Raw -Encoding UTF8 | ConvertFrom-Json
$nn     = $habits | Where-Object { $_.isNN -eq $true }
$reg    = $habits | Where-Object { $_.isNN -ne $true }

$today = (Get-Date).ToString("dddd, MMMM d")

$lines = @()
$lines += "Good morning! Plan for $today"
$lines += ""
$lines += "Non-Negotiables:"
foreach ($h in $nn)  { $lines += "  - $($h.name)" }
$lines += ""
$lines += "Daily Habits:"
foreach ($h in $reg) { $lines += "  - $($h.name)" }
$lines += ""
$lines += "Make today count!"

$msg  = $lines -join "`n"
$url  = "https://api.twilio.com/2010-04-01/Accounts/$accountSid/Messages.json"
$cred = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${accountSid}:${authToken}"))
$body = "From=$([System.Uri]::EscapeDataString($fromNumber))&To=$([System.Uri]::EscapeDataString($toNumber))&Body=$([System.Uri]::EscapeDataString($msg))"

try {
    $res = Invoke-RestMethod -Uri $url -Method Post -Headers @{Authorization="Basic $cred"} -ContentType "application/x-www-form-urlencoded" -Body $body
    Write-Output "Sent! SID: $($res.sid)"
} catch {
    Write-Output "Failed: $_"
}
