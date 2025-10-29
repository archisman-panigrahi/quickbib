; NSIS script to package the PyInstaller 'dist/QuickBib' output into an installer.
; This script assumes the build step produces a folder 'dist\QuickBib' with QuickBib.exe

!define APP_NAME "QuickBib"
!define COMPANY "Archisman Panigrahi"
!define VERSION "0.2"

RequestExecutionLevel user
SetCompress off

; Use the repository-provided ICO as the installer icon. The path is relative to the repo root
; since makensis is invoked from the workflow's working directory (repo root), use a relative path
Icon "assets\\icon\\64x64\\io.github.archisman_panigrahi.quickbib.ico"

OutFile "${APP_NAME}-Installer.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  ; Copy all files from the PyInstaller output
  File /r "dist\\QuickBib\\*"

  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\QuickBib.exe"

  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\QuickBib.exe"

  ; Write install location for uninstaller
  WriteRegStr HKLM "Software\\${COMPANY}\\${APP_NAME}" "Install_Dir" "$INSTDIR"

  ; Write Uninstaller
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  ; Read install dir
  ReadRegStr $0 HKLM "Software\\${COMPANY}\\${APP_NAME}" "Install_Dir"
  StrCmp $0 "" 0 done

  ; Remove shortcuts
  Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\\${APP_NAME}"
  Delete "$DESKTOP\\${APP_NAME}.lnk"

  ; Delete files
  RMDir /r "$0"

  ; Remove registry
  DeleteRegKey HKLM "Software\\${COMPANY}\\${APP_NAME}"

done:
  ; Remove uninstaller
  Delete "$INSTDIR\\Uninstall.exe"
SectionEnd
