# USF4 Trial Editor

A Windows application for creating and editing character trials in Ultra Street Fighter IV.

Build your own combos, time yourself and challenge your friends.


## Features

- Uses original USF4 trial system
- Edit all 24 Evil Ryu trials.
- Create custom combo sequences using a built-in move library.
- Add, remove, replace and reorder moves.
- Configure Ultra selection and opponent stance.
- Expanded trial interface supporting up to 16 displayed moves.
- Save and load custom trial projects (includes all 24)
- Send the file to your friends and challenge them.
- Install custom trials directly into the game.
- Automatically back up original game files.
- Restore original trials and interface files.


## Supported Characters

| Character | Status |
|---|---|
| Evil Ryu | Supported |
| Remaining roster | Unsupported |

## Installation

1. Download `USF4-TrialEditor.exe` from GitHub Releases.
2. Launch the application.
3. Select your installation directory. 
4. (*steam folder*/steamapps/common/Super Street Fighter IV - Arcade Edition)
5. Allow the editor to back up the original game files.

## Usage

1. Select a trial to edit.
2. Build your custom combo using the move library.
3. Configure the trial settings.
4. Save your project if you wish to edit it later.
5. Close Ultra Street Fighter IV before installing custom trials.
6. Select **Install Custom Trials**.
7. For trials containing more than eight moves, select **Install Expanded UI**.
8. Launch the game and enter Trial Mode.

## Restoring the Original Game

Close the game and use the editor's restoration options:

- **Restore Original Trials**
- **Restore Original UI**

The editor uses locally stored backups to restore the original files.

## Compatibility and Limitations

- Designed for the Steam version of Ultra Street Fighter IV on Windows.
- Version 1.0.0 currently supports Evil Ryu only.
- The expanded trial HUD and selection interface display up to 16 moves.
- Pause menu does not expand.

## Future versions

- Support for the entire character roster.
- Additional trial configuration options.
- Expanded pause menu.
- Further UI improvements.

## Technical Overview


The editor modifies the game's CLG trial data and applies compact binary patches to the trial interface using the user's existing game files.

Built with Python, Tkinter and PyInstaller.

## Disclaimer

This is an unofficial, community-developed modding tool and is not affiliated with or endorsed by Capcom.

Street Fighter and its characters belong to their respective copyright holders.

Use this tool at your own discretion.

## Version

**v1.0.0 — Initial release**