; NSIS script to package the PyInstaller 'dist/QuickBib' output into an installer.
; This script assumes the build step produces a folder 'dist\QuickBib' with QuickBib.exe

!define APP_NAME "QuickBib"
!define COMPANY "Archisman Panigrahi"
!define VERSION "0.3.3"

; Installer display name shown in the window title and installer UI
Name "${APP_NAME}"

; The installer needs to write under Program Files and modify HKLM; require elevation.
RequestExecutionLevel admin

!include nsDialogs.nsh
!include LogicLib.nsh

; Use Modern UI 2 so we can set the installer UI icon to the application icon
!define MUI_ICON "..\\assets\\icon\\64x64\\io.github.archisman_panigrahi.QuickBib.ico"
!include MUI2.nsh

Var RADIO_ALL
Var RADIO_USER
Var INSTALL_SCOPE

; Custom page to select installation scope: All users (Program Files) or Current user (LocalAppData)
Page custom ScopePageCreate ScopePageLeave
SetCompress off

; The NSIS script lives in the `windows_packaging` directory. Paths in this script
; are resolved relative to the script's location, so reference files in the repo root
; using a parent-directory prefix.
Icon "..\\assets\\icon\\64x64\\io.github.archisman_panigrahi.QuickBib.ico"

OutFile "${APP_NAME}-Installer.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"

Page directory
Page instfiles

Function ScopePageCreate
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}

  ${NSD_CreateLabel} 0 0 100% 12u "Install scope"
  Pop $R0

  ${NSD_CreateRadioButton} 0 20u 100% 12u "Install for all users (requires admin)"
  Pop $RADIO_ALL

  ${NSD_CreateRadioButton} 0 36u 100% 12u "Install for current user only"
  Pop $RADIO_USER

  ; Default to All users
  ${NSD_SetState} $RADIO_ALL 1

  nsDialogs::Show
FunctionEnd

Function ScopePageLeave
  ${NSD_GetState} $RADIO_ALL $0
  ${If} $0 == 1
    StrCpy $INSTDIR "$PROGRAMFILES\\${APP_NAME}"
    StrCpy $INSTALL_SCOPE "ALL"
  ${Else}
    StrCpy $INSTDIR "$LOCALAPPDATA\\Programs\\${APP_NAME}"
    StrCpy $INSTALL_SCOPE "USER"
  ${EndIf}
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  ; Copy all files from the PyInstaller output (dist is at repo root, so step up one dir)
  File /r "..\\dist\\QuickBib\\*"

  ; Include repository LICENSE in the installed files so users can view the license
  ; The LICENSE file is located at the repository root (one directory up from this script)
  File "..\\LICENSE"

  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\QuickBib.exe"

  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\QuickBib.exe"

  ; Write install location for uninstaller under HKLM if installing for all users,
  ; otherwise record under HKCU for current-user installs.
  StrCmp $INSTALL_SCOPE "ALL" 0 +3
    WriteRegStr HKLM "Software\\${COMPANY}\\${APP_NAME}" "Install_Dir" "$INSTDIR"
    Goto +2
  WriteRegStr HKCU "Software\\${COMPANY}\\${APP_NAME}" "Install_Dir" "$INSTDIR"

  ; Write Uninstaller
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  ; Read install dir: prefer HKLM (all-users), fall back to HKCU (current-user)
  ReadRegStr $0 HKLM "Software\\${COMPANY}\\${APP_NAME}" "Install_Dir"
  StrCmp $0 "" 0 +3
    ReadRegStr $0 HKCU "Software\\${COMPANY}\\${APP_NAME}" "Install_Dir"
    StrCmp $0 "" 0 +2
      ; No install dir found
      Goto done

  ; Remove shortcuts
  Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\\${APP_NAME}"
  Delete "$DESKTOP\\${APP_NAME}.lnk"

  ; Delete files
  RMDir /r "$0"

  ; Remove registry
  DeleteRegKey HKLM "Software\\${COMPANY}\\${APP_NAME}"
  DeleteRegKey HKCU "Software\\${COMPANY}\\${APP_NAME}"

done:
  ; Remove uninstaller
  Delete "$0\\Uninstall.exe"
SectionEnd
