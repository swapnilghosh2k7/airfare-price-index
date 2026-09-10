$uPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
if ($uPath -notlike "*Git\cmd*") {
    [System.Environment]::SetEnvironmentVariable('Path', "$uPath;C:\Program Files\Git\cmd", 'User')
    Write-Output "Successfully added Git to User PATH"
} else {
    Write-Output "Git is already in User PATH"
}
