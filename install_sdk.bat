@echo off
echo === Accepting All SDK Licenses ===
echo.

set SDKMANAGER=C:\AndroidSDK\cmdline-tools\latest\bin\sdkmanager.bat
set SDK_ROOT=C:\AndroidSDK

echo y
echo y
echo y
echo y
echo y
echo y
echo y
echo y
) | "%SDKMANAGER%" --sdk_root="%SDK_ROOT%" --licenses

echo.
echo === Now Installing Components ===

echo [1/3] Installing platform-tools...
"%SDKMANAGER%" --sdk_root="%SDK_ROOT%" "platform-tools"

echo [2/3] Installing emulator...
"%SDKMANAGER%" --sdk_root="%SDK_ROOT%" "emulator"

echo [3/3] Installing system image...
"%SDKMANAGER%" --sdk_root="%SDK_ROOT%" "platforms;android-35" "system-images;android-35;google_apis_playstore;x86_64"

echo.
echo === DONE ===
