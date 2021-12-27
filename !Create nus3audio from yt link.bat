@ECHO OFF

:: Link
ECHO Cool yt audio and conversion thing!
IF "%LINK%"=="" SET /p LINK=YT Link: 

:: Final file
:fileOutput
ECHO Final output options:
ECHO 1) BRSTM
ECHO 2) IDSP
ECHO 3) NUS3AUDIO
SET /p output=Option number: 
SET /A output=%output%
SET invalid=FALSE
IF %output% LSS 1 SET invalid=TRUE
IF %output% GTR 3 SET invalid=TRUE
IF %invalid%==TRUE (
    ECHO Please enter a valid choice [1-3]
    GOTO :fileOutput
)

:: Looping Point Option
SET /p loopPoints=Enter a set of loop points (start-end), enter 'n' for no loop, or enter 'a' for automatic detection: 

:: Download music
youtube-dl -x --audio-format wav "%LINK%"

:: Set audio rate to 48000
FOR /f "delims=" %%n IN ('youtube-dl --audio-format wav -x --get-filename "%LINK%"') DO SET fileName=%%~nn
RENAME "%fileName%.wav" "%fileName%.temp"
ffmpeg -i "%fileName%.temp" -ar 48000 -y "%fileName%.wav"

:: Get name without id (replace special characters with _)
FOR /f "delims=" %%t IN ('youtube-dl -e "%LINK%"') DO (
    FOR /f "delims=" %%s IN ('python RemoveIllegalCharacters.py "%%t"') DO (
        SET title=%%s
    )
)

MKDIR Output

:: Get loop points
IF %loopPoints%=a (
    FOR /f "delims=" %%p IN ('python GetLoopingPoint.py "%filename%.wav") DO (
        SET loopPoints=0-%%p
    )
)

:: Set loop flag
SET loopFlag=-l %loopPoints%
IF %loopPoints%=n SET loopFlag=--no-loop

:: Convert to BRSTM
IF %output% == 1 (
    ECHO Creating brstm file
    VGAudioCli -i "%fileName%.wav" %loopFlag% -o "Output/%title%.brstm"
    GOTO :Cleanup
)

:: Convert to IDSP
ECHO Creating idsp file
VGAudioCli -i "%fileName%.wav" %loopFlag% -o "%fileName%.idsp"
:: Move IDSP file
IF %output% == 2 (
    COPY "%fileName%.idsp" "Output/%title%.idsp"
    GOTO :Cleanup
)

:: Convert to nus3audio
IF %output% == 3 (
    ECHO Creating nus3audio file
    nus3audio.exe -n -A "%title%" "%fileName%.idsp" -w "Output/%title%.nus3audio"
)

:: Cleanup
:Cleanup
ECHO Cleaning up!
DEL "%fileName%.temp"
DEL "%fileName%.wav"
IF %output% NEQ 1 DEL "%fileName%.idsp"
ECHO Done!
PAUSE