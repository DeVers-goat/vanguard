Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "Morning Habits"
$form.Size = New-Object System.Drawing.Size(340, 160)
$form.StartPosition = "CenterScreen"
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(18, 18, 28)
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

$label = New-Object System.Windows.Forms.Label
$label.Text = "Good morning! Your habits are waiting."
$label.ForeColor = [System.Drawing.Color]::FromArgb(220, 220, 255)
$label.Font = New-Object System.Drawing.Font("Segoe UI", 11)
$label.Location = New-Object System.Drawing.Point(20, 20)
$label.Size = New-Object System.Drawing.Size(300, 40)
$form.Controls.Add($label)

$btn = New-Object System.Windows.Forms.Button
$btn.Text = "Open App"
$btn.Location = New-Object System.Drawing.Point(20, 75)
$btn.Size = New-Object System.Drawing.Size(130, 36)
$btn.BackColor = [System.Drawing.Color]::FromArgb(124, 110, 248)
$btn.ForeColor = [System.Drawing.Color]::White
$btn.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btn.FlatStyle = "Flat"
$btn.FlatAppearance.BorderSize = 0
$btn.Add_Click({ Start-Process "c:\RanClaude\Main"; $form.Close() })
$form.Controls.Add($btn)

$dismiss = New-Object System.Windows.Forms.Button
$dismiss.Text = "Dismiss"
$dismiss.Location = New-Object System.Drawing.Point(170, 75)
$dismiss.Size = New-Object System.Drawing.Size(130, 36)
$dismiss.BackColor = [System.Drawing.Color]::FromArgb(40, 40, 55)
$dismiss.ForeColor = [System.Drawing.Color]::FromArgb(180, 180, 200)
$dismiss.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$dismiss.FlatStyle = "Flat"
$dismiss.FlatAppearance.BorderSize = 0
$dismiss.Add_Click({ $form.Close() })
$form.Controls.Add($dismiss)

$form.ShowDialog()
