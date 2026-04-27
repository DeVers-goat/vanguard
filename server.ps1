$port = 8000
$path = "."

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")

try {
    $listener.Start()
    Write-Host "Server started on http://localhost:$port/"
    Write-Host "Press Ctrl+C to stop"

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        $localPath = $request.Url.LocalPath
        if ($localPath -eq "/") { $localPath = "/index.html" }
        $filePath = Join-Path $path $localPath.TrimStart("/")

        if (Test-Path $filePath -PathType Leaf) {
            $content = Get-Content $filePath -Raw -Encoding UTF8
            $response.ContentType = if ($filePath.EndsWith(".html")) { "text/html" } elseif ($filePath.EndsWith(".js")) { "application/javascript" } elseif ($filePath.EndsWith(".css")) { "text/css" } else { "text/plain" }
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        } else {
            $response.StatusCode = 404
            $notFound = "<h1>404 Not Found</h1>"
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($notFound)
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }

        $response.OutputStream.Close()
    }
} catch {
    Write-Host "Error: $_"
} finally {
    $listener.Stop()
}