# Super-Class-Bros

Open the secret UCAS button to launch the game. Choose a fighter, stage, and match mode in the HUD; the game includes Canvas, myUVU, and training maps, Smash-style combat, UI Tag, local CPUs/dummies, and multiplayer rooms.

## Default controls

- A / D: move left / right
- W / S: aim up / crouch, fast-fall, or drop through a platform
- Space: jump
- Q: shield / dodge
- Shift: fighter class movement
- Left Arrow: light / tilt attack
- Right Arrow: smash attack
- Down Arrow: ranged special
- Up Arrow: recovery special
- Backquote key: enter or leave the game

Open **Settings** to rebind controls. Bindings are saved on this device. Touch controls are shown on mobile and coarse-pointer screens, and gamepads are supported.

## Music

The optional music player is available in **Settings → Music player**. It supports track selection, play/pause, previous/next, seek, volume, mute, shuffle, playlist/track/off loop modes, and an optional top-left mini player. Music can be played on either stage.

Tracks are read from `assets/music/`. The game attempts to discover MP3s from a server directory listing; GitHub Pages does not expose directory listings, so its known tracks use explicit relative paths in `MUSIC_TRACK_PATHS` in `index.html`. When adding a track for GitHub Pages, add its path there as well as the MP3 file. Browsers block playback when the page is opened with `file://`; use GitHub Pages or a local web server.

## Gameplay and multiplayer

- Fighters have distinct movement abilities, specials, shields, dodges, and Smash-style combat.
- Solid surfaces, walls, and slopes have collision; semisolid platforms can be dropped through.
- The myUVU portal stage scrolls vertically to keep the player near the center of the view.
- Remote player positions are interpolated, and Tag/Fight modes use separate room channels.
- The HUD includes fighter selection, host stage/mode controls, rooms, player customization, and training dummy reset.
