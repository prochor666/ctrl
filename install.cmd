@ECHO OFF
cls
WHERE /Q python

ECHO CTRL installer

IF %ERRORLEVEL% NEQ 0 (
    ECHO Python 3 is required
    EXIT /B 0
)

FOR /F "tokens=2" %%G IN ('python -V') do (SET version_raw=%%G)

SET modified=%version_raw:.=%
SET /A num=%modified%+0

IF %num% LSS 373 (
    ECHO Python 3.7.3 or newer is required
    EXIT /B 0
) ELSE (
    ECHO Python %version_raw% found
)

WHERE /Q pip

IF %ERRORLEVEL% NEQ 0 (
    ECHO PIP is required
    EXIT /B 0
) ELSE (
    pip install pymongo
    pip install Flask
    pip install pyopenssl
    pip install pyIsEmail
    pip install psutil
    pip install websocket
    pip install websocket-client
    pip install -U python-digitalocean
    pip install pyarubacloud
    pip install dnspython
    pip install python-slugify
    pip install asyncssh
    pip install fakturoid

    IF exist storage\recipes (
        echo storage\recipes exists
    ) ELSE (
        mkdir storage\recipes && echo storage\recipes created
    )

    IF exist storage\templates (
        echo storage\templates exists
    ) ELSE (
        mkdir storage\templates && echo storage\templates created
    )

    IF exist storage\logs (
        echo storage\logs exists
    ) ELSE (
        mkdir storage\logs && echo storage\logs created
    )

    IF exist json\app.json (
        echo json\app.json exists
    ) ELSE (
        copy json\sample.app.json json\app.json && echo json\app.json created
    )

    IF exist json\smtp.json (
        echo storage\recipes exists
    ) ELSE (
        copy json\sample.smtp.json json\smtp.json && echo json\smtp.json created
    )
)
