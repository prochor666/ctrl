@cls
@WHERE /Q python
@IF %ERRORLEVEL% NEQ 0 (
@ECHO Python 3 is required
@EXIT /B 0
) ELSE (
pip install pymongo
@python install.py %*
)
