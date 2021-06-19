@cls
@WHERE /Q python

#ECHO CTRL installer

@IF %ERRORLEVEL% NEQ 0 (
    @ECHO Python 3 is required
    @EXIT /B 0
)

@WHERE /Q pip

@IF %ERRORLEVEL% NEQ 0 (
    @ECHO PIP is required
    @EXIT /B 0
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

    @IF exist storage\recipes (
        echo storage\recipes exists
    ) ELSE (
        mkdir storage\recipes && echo storage\recipes created
    )

    @IF exist storage\templates (
        echo storage\templates exists
    ) ELSE (
        mkdir storage\templates && echo storage\templates created
    )

    @IF exist json\app.json (
        echo json\app.json exists
    ) ELSE (
        copy json\sample.app.json json\app.json && echo json\app.json created
    )

    @IF exist json\smtp.json (
        echo storage\recipes exists
    ) ELSE (
        copy json\sample.smtp.json json\smtp.json && echo json\smtp.json created
    )
)
