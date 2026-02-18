param(
    [string]$ProjectRoot = "."
)

$ErrorActionPreference = "Stop"

$gradlePath = Join-Path $ProjectRoot "build/mobile_app/android/gradle/app/build.gradle"
if (-not (Test-Path $gradlePath)) {
    throw "build.gradle not found at $gradlePath"
}

$content = Get-Content -Path $gradlePath -Raw
$content = $content.TrimStart([char]0xFEFF)

# Keep only appcompat as explicit dependency to avoid pulling conflicting transitive sets.
$content = $content -replace '(?s)dependencies\s*\{.*?\}', @'
dependencies {
    implementation fileTree(dir: 'libs', include: ['*.jar'])
    implementation "androidx.appcompat:appcompat:1.7.0"
}
'@

$excludeBlock = @'
configurations.configureEach {
    exclude group: "org.jetbrains.kotlin", module: "kotlin-stdlib-jdk7"
    exclude group: "org.jetbrains.kotlin", module: "kotlin-stdlib-jdk8"
}
'@

if ($content -notmatch 'kotlin-stdlib-jdk7') {
    $content = $content.TrimEnd() + "`r`n`r`n" + $excludeBlock + "`r`n"
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($gradlePath, $content, $utf8NoBom)
Write-Host "Applied Android Gradle Kotlin workaround to $gradlePath"
