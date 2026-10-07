Add-Type -AssemblyName System.Drawing
$iconsDir = "C:\Users\liem.vu\Liem.vuOD\ExtensionChorme\icons"
if (-not (Test-Path $iconsDir)) { 
    New-Item -ItemType Directory -Path $iconsDir -Force | Out-Null 
}

$sizes = @(16, 32, 48, 128)

foreach ($size in $sizes) {
    $bmp = New-Object System.Drawing.Bitmap $size, $size
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

    # Background circle
    $rect = New-Object System.Drawing.Rectangle 1, 1, ($size - 2), ($size - 2)
    $bgColor = [System.Drawing.Color]::FromArgb(30, 41, 59)
    $bgBrush = New-Object System.Drawing.SolidBrush $bgColor
    $g.FillEllipse($bgBrush, $rect)

    # Border
    $borderColor = [System.Drawing.Color]::FromArgb(99, 102, 241)
    $penWidth = [float][Math]::Max(1.0, ($size / 16.0))
    $borderPen = New-Object System.Drawing.Pen $borderColor, $penWidth
    $g.DrawEllipse($borderPen, $rect)

    # Ghost shape (White / lavender)
    $ghostColor = [System.Drawing.Color]::FromArgb(224, 231, 255)
    $ghostBrush = New-Object System.Drawing.SolidBrush $ghostColor
    $cx = [float]($size / 2.0)
    $cy = [float]($size / 2.0)
    $rw = [float]($size * 0.28)
    $rh = [float]($size * 0.20)

    # Eye shape
    $g.FillEllipse($ghostBrush, ($cx - $rw), ($cy - $rh), ($rw * 2), ($rh * 2))

    # Pupil
    $pupilColor = [System.Drawing.Color]::FromArgb(15, 23, 42)
    $pupilBrush = New-Object System.Drawing.SolidBrush $pupilColor
    $pr = [float][Math]::Max(1.5, $rw * 0.5)
    $g.FillEllipse($pupilBrush, ($cx - $pr), ($cy - $pr), ($pr * 2), ($pr * 2))

    # Pupil highlight
    $hiColor = [System.Drawing.Color]::FromArgb(255, 255, 255)
    $hiBrush = New-Object System.Drawing.SolidBrush $hiColor
    $hr = [float][Math]::Max(0.8, $pr * 0.35)
    $g.FillEllipse($hiBrush, ($cx - $pr * 0.4), ($cy - $pr * 0.4), ($hr * 2), ($hr * 2))

    # Slash line across eye (Stealth icon)
    $slashColor = [System.Drawing.Color]::FromArgb(239, 68, 68)
    $slashWidth = [float][Math]::Max(1.5, ($size / 10.0))
    $slashPen = New-Object System.Drawing.Pen $slashColor, $slashWidth
    $g.DrawLine($slashPen, [float]($size * 0.2), [float]($size * 0.8), [float]($size * 0.8), [float]($size * 0.2))

    $path = Join-Path $iconsDir "icon$size.png"
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Host "Generated icon: $path"
}
