@echo off

set file=%1
if "%file%"=="" (
    echo Please provide a Manim script file to run.
    exit /b 1
)

set classname=%2
if "%classname%"=="" (
    echo Please provide the class name to render.
    exit /b 1
)

manimgl %file% %classname%
