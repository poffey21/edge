
# to run just type:
# . scripts\local_enable.ps1

try {
    . $HOME\.venvs\{{ project_name }}\Scripts\activate.ps1
}
catch {
    . ..\..\.venvs\{{ project_name }}\Scripts\activate.ps1
}

cd src
