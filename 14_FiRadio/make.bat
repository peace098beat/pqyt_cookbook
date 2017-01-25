@ECHO OFF
pushd %~dp0


if "%1" == "test" (
    cls
    python -m unittest discover tests "test_*.py"
)

if "%1" == "run" (
    cls
    python ./src/appmain.py
)


if "%1" == "exe" (
	set APPNAME=_FiRadio
    pyinstaller --onefile ./src/appmain.py -n %APPNAME% --noconsole
    cd dist
    %APPNAME%.exe
    cd ..

)