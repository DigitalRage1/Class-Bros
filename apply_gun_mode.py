#!/usr/bin/env python3
"""
Adds the "Gun Smash" game mode (its own menu, same maps) to Super-Class-Bros.

Usage:   python apply_gun_mode.py [path/to/index.html]     (default: ./index.html)

- Makes index.html.bak first.
- Every edit anchors on exact existing text and aborts (changing nothing) if an
  anchor is missing, so it can never half-patch the file.
- Also adds a short "Gun Smash" section to README.md if it sits next to index.html.
"""
import os
import sys

# --------------------------------------------------------------------------
# HTML pieces
# --------------------------------------------------------------------------
HUD_BUTTON = r"""<button id="open-gun-menu-btn" title="Open the Gun Smash menu" class="px-2 py-0.5 rounded-full bg-white hover:bg-[#e8e8e8] border border-[#c7cdd1] text-[11px] font-bold text-canvas-text transition cursor-pointer">
                    🔫 Gun Smash
                </button>
                """

MENU_HTML = r"""<!-- GUN SMASH MENU POPOVER -->
    <div id="gun-menu-popover" class="hidden fixed bottom-16 left-1/2 -translate-x-1/2 z-[10000] w-[340px] max-w-[94vw] max-h-[72vh] overflow-y-auto p-3.5 rounded-xl bg-white/98 text-canvas-text shadow-[0_8px_30px_rgba(45,59,69,0.22)] border border-[#c7cdd1] backdrop-blur-md text-xs">
        <div class="flex items-center justify-between pb-2 mb-2.5 border-b border-[#e2e6ea]">
            <div>
                <span class="font-bold text-canvas-text text-[13px]">Gun Smash</span>
                <span class="block text-[10px] text-canvas-muted">Smash Bros. rules, but everyone has a gun</span>
            </div>
            <button id="close-gun-menu-btn" type="button" class="text-canvas-muted hover:text-canvas-text font-bold text-base px-1.5 cursor-pointer">×</button>
        </div>
        <div class="space-y-3">
            <div>
                <span class="block text-[11px] font-bold mb-1">Stage</span>
                <div class="grid grid-cols-3 gap-1.5">
                    <button type="button" data-gun-map="canvas" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">Canvas LMS</button>
                    <button type="button" data-gun-map="myuvu" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">myUVU</button>
                    <button type="button" data-gun-map="training" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">Training</button>
                </div>
            </div>
            <div>
                <span class="block text-[11px] font-bold mb-1">Your gun</span>
                <div class="grid grid-cols-3 gap-1.5">
                    <button type="button" data-gun-weapon="pistol" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">Pistol<span class="block text-[9px] font-normal text-canvas-muted">12 rds · accurate</span></button>
                    <button type="button" data-gun-weapon="rifle" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">Rifle<span class="block text-[9px] font-normal text-canvas-muted">30 rds · auto</span></button>
                    <button type="button" data-gun-weapon="shotgun" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">Shotgun<span class="block text-[9px] font-normal text-canvas-muted">6 rds · spread</span></button>
                </div>
            </div>
            <div>
                <span class="block text-[11px] font-bold mb-1">CPU opponents</span>
                <div class="grid grid-cols-4 gap-1.5">
                    <button type="button" data-gun-cpus="0" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">0</button>
                    <button type="button" data-gun-cpus="1" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">1</button>
                    <button type="button" data-gun-cpus="2" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">2</button>
                    <button type="button" data-gun-cpus="3" class="rounded border border-[#c7cdd1] bg-white px-1.5 py-1.5 font-semibold cursor-pointer">3</button>
                </div>
                <p class="mt-1 text-[9.5px] text-canvas-muted">Training stage uses stationary dummies instead of CPUs.</p>
            </div>
            <div class="p-2 rounded-lg bg-[#f4f6f8] border border-[#e2e6ea] text-[10px] leading-relaxed">
                <b>Left Arrow / Pad A</b> shoot (hold for rifle) · <b>WASD</b> aim (up/down/diagonal) · <b>Down Arrow / L3</b> reload · <b>Right Arrow</b> melee smash · <b>Up Arrow</b> recovery · <b>Q</b> shield. Hits add damage %, and higher % means bigger knockback. Knock opponents off-screen for a KO.
            </div>
            <p id="gun-host-note" class="text-[9.5px] text-canvas-muted"></p>
            <div class="flex gap-1.5">
                <button id="start-gun-btn" type="button" class="flex-1 px-3 py-1.5 rounded bg-[#1c5c43] hover:bg-[#123e2d] text-white font-bold transition cursor-pointer">Start Gun Smash</button>
                <button id="stop-gun-btn" type="button" class="hidden px-3 py-1.5 rounded bg-white hover:bg-[#f5f5f5] border border-[#c7cdd1] font-bold transition cursor-pointer">Stop</button>
            </div>
        </div>
    </div>

    """

# --------------------------------------------------------------------------
# JS module code (inserted before the init lines at the bottom of the module)
# --------------------------------------------------------------------------
JS_BLOCK = r"""/**
         * =========================================================================
         * 8. GUN SMASH MODE (Smash Battle rules + guns, started from its own menu)
         * =========================================================================
         */
        let gunMode = false;
        let gunType = 'pistol';
        let gunMenuMap = 'canvas';
        let gunMenuCpus = 2;
        let gunPrevFire = false;
        let gunPrevReload = false;

        const GUN_TYPES = {
            pistol:  { name: 'Pistol',  mag: 12, cd: 0.26,  reload: 1.0, pellets: 1, spread: 0.02, speed: 780, dmg: 5,   kb: 130, life: 0.9, auto: false, radius: 2.6, color: '#f59e0b' },
            rifle:   { name: 'Rifle',   mag: 30, cd: 0.095, reload: 1.5, pellets: 1, spread: 0.05, speed: 860, dmg: 2.5, kb: 70,  life: 1.0, auto: true,  radius: 2.4, color: '#fbbf24' },
            shotgun: { name: 'Shotgun', mag: 6,  cd: 0.70,  reload: 1.7, pellets: 6, spread: 0.26, speed: 660, dmg: 3.2, kb: 110, life: 0.4, auto: false, radius: 2.4, color: '#ef4444' }
        };
        const BOT_GUNS = { 'cpu-1': 'rifle', 'cpu-2': 'shotgun', 'cpu-3': 'pistol' };

        const gunMenuPopover = document.getElementById('gun-menu-popover');
        const openGunMenuBtn = document.getElementById('open-gun-menu-btn');
        const closeGunMenuBtn = document.getElementById('close-gun-menu-btn');
        const startGunBtn = document.getElementById('start-gun-btn');
        const stopGunBtn = document.getElementById('stop-gun-btn');
        const gunHostNote = document.getElementById('gun-host-note');

        function gunActive() {
            return gunMode && matchMode === 'battle';
        }

        function ensureGun(r) {
            if (r === localRunner) r.gunType = gunType;
            else if (!r.gunType) r.gunType = BOT_GUNS[r.id] || 'pistol';
            const spec = GUN_TYPES[r.gunType] || GUN_TYPES.pistol;
            if (r.gunAmmo === undefined) {
                r.gunAmmo = spec.mag;
                r.gunCd = 0;
                r.gunReload = 0;
            }
            return spec;
        }

        function getFirstPad() {
            if (!navigator.getGamepads) return null;
            for (const p of navigator.getGamepads()) {
                if (p && p.connected) return p;
            }
            return null;
        }

        function startReload(r) {
            const spec = ensureGun(r);
            if (r.gunReload > 0 || r.gunAmmo >= spec.mag) return;
            r.gunReload = spec.reload;
            if (r === localRunner) addFloatingCallout(r.x + r.w / 2, r.y - 18, 'RELOADING', '#64748b');
        }

        function spawnGunBullet(owner, x, y, vx, vy, spec, launchAngle) {
            spawnProjectile(owner, x, y, vx, vy, spec.dmg, launchAngle, spec.kb, spec.color, spec.radius);
            const p = projectiles[projectiles.length - 1];
            p.life = spec.life;
            p.gun = true;
            return p;
        }

        function fireGun(r, aimX, aimY) {
            if (!gunActive() || r.hitstunTimer > 0 || r.rollTimer > 0 || r.shielding) return false;
            const spec = ensureGun(r);
            if (r.gunReload > 0 || r.gunCd > 0) return false;
            if (r.gunAmmo <= 0) {
                startReload(r);
                return false;
            }

            let ax = aimX;
            let ay = aimY;
            if (!ax && !ay) ax = r.facing;
            if (ax) r.facing = ax > 0 ? 1 : -1;
            const len = Math.hypot(ax, ay) || 1;
            ax /= len;
            ay /= len;
            const baseAng = Math.atan2(ay, ax);
            r.gunAim = baseAng;
            r.gunAimUntil = performance.now() + 300;

            const launchAngle = ay < -0.5 ? -1.1 : (ay > 0.5 ? 0.8 : -0.3);
            const px = r.x + r.w / 2 + ax * 10;
            const py = r.y + r.h / 2 - 1 + ay * 8;
            const shots = [];
            for (let i = 0; i < spec.pellets; i++) {
                const a = baseAng + (Math.random() - 0.5) * 2 * spec.spread;
                const vx = Math.cos(a) * spec.speed;
                const vy = Math.sin(a) * spec.speed;
                spawnGunBullet(r, px, py, vx, vy, spec, launchAngle);
                const n = toNormalizedCoords(px, py);
                shots.push({ nx: n.nx, ny: n.ny, vx: Math.round(vx), vy: Math.round(vy), life: spec.life, color: spec.color, radius: spec.radius });
            }

            r.gunAmmo -= 1;
            r.gunCd = spec.cd;
            r.vx -= ax * (spec.pellets > 1 ? 170 : 35);
            spawnParticles(px, py, spec.color, spec.pellets > 1 ? 7 : 3);

            if (r === localRunner) {
                const msg = { type: 'gun-shot', room: currentRoom, ownerId: localPlayerId, shots };
                publishWssMessage(msg);
                broadcastToPeers(msg);
                if (localChannel) localChannel.postMessage(msg);
            }
            if (r.gunAmmo <= 0) startReload(r);
            return true;
        }

        // Visual-only bullets fired by other players (damage is sent by the shooter as 'smash-hit').
        function handleRemoteGunShot(msg) {
            if (!msg || msg.room !== currentRoom || msg.ownerId === localPlayerId || !gunActive()) return;
            for (const s of (msg.shots || [])) {
                const pos = fromNormalizedCoords(s.nx, s.ny);
                projectiles.push({
                    ownerId: msg.ownerId,
                    x: pos.px,
                    y: pos.py,
                    vx: s.vx || 0,
                    vy: s.vy || 0,
                    damage: 0,
                    angle: 0,
                    baseKb: 0,
                    color: s.color || '#f59e0b',
                    radius: s.radius || 2.5,
                    life: s.life || 0.8,
                    visual: true,
                    gun: true
                });
            }
        }

        function gunBotAi(bot, target, dist, dx, dy) {
            const spec = ensureGun(bot);
            if (bot.gunAmmo <= 0 && bot.gunReload <= 0) startReload(bot);
            if (bot.aiActionTimer > 0) return;
            if (dist < 34 && Math.abs(dy) < 26) {
                bot.facing = dx >= 0 ? 1 : -1;
                triggerSmashMove(bot, 'fsmash');
                bot.aiActionTimer = 0.7 + Math.random() * 0.4;
                return;
            }
            if (dist > 520 || Math.abs(dy) > 220) {
                bot.aiActionTimer = 0.2;
                return;
            }
            const aimX = Math.abs(dx) > 18 ? Math.sign(dx) : 0;
            const aimY = Math.abs(dy) > 45 ? Math.sign(dy) : 0;
            const fired = fireGun(bot, aimX, aimY);
            bot.aiActionTimer = fired
                ? (spec.auto ? 0.1 + Math.random() * 0.1 : spec.cd + 0.15 + Math.random() * 0.4)
                : 0.15;
        }

        function drawGunSprite(r) {
            const spec = GUN_TYPES[r.gunType || 'pistol'] || GUN_TYPES.pistol;
            const useAim = r === localRunner || performance.now() < (r.gunAimUntil || 0);
            const ang = useAim && r.gunAim !== undefined ? r.gunAim : (r.facing >= 0 ? 0 : Math.PI);
            ctx.save();
            ctx.translate(r.x + r.w / 2, r.y + r.h * 0.55);
            ctx.rotate(ang);
            if (Math.cos(ang) < 0) ctx.scale(1, -1);
            ctx.fillStyle = '#1e293b';
            if (r.gunType === 'rifle') {
                ctx.fillRect(1, -1.5, 19, 3);
                ctx.fillRect(-3, -1, 5, 3);
                ctx.fillRect(7, 1.5, 2.5, 4);
            } else if (r.gunType === 'shotgun') {
                ctx.fillRect(1, -2, 16, 4);
                ctx.fillStyle = '#92400e';
                ctx.fillRect(-3, -1.5, 5, 3);
                ctx.fillRect(7, 1.5, 6, 2);
            } else {
                ctx.fillRect(2, -1.5, 11, 3);
                ctx.fillRect(3, 1, 3, 4);
            }
            ctx.fillStyle = spec.color;
            ctx.fillRect(1, -0.5, 2, 1);
            ctx.restore();
        }

        // Runs every frame in Gun Smash: reads fire/reload input, ticks timers, draws guns, bullets and ammo HUD.
        function gunFrame(dt) {
            if (!gunActive()) {
                gunPrevFire = false;
                gunPrevReload = false;
                return;
            }

            const fighters = [localRunner, ...getActiveBots()];
            for (const r of fighters) {
                const spec = ensureGun(r);
                if (r.gunCd > 0) r.gunCd -= dt;
                if (r.gunReload > 0) {
                    r.gunReload -= dt;
                    if (r.gunReload <= 0) {
                        r.gunReload = 0;
                        r.gunAmmo = spec.mag;
                    }
                }
            }

            const pad = getFirstPad();
            const left = isActionDown('moveLeft') || padVirtualLeft;
            const right = isActionDown('moveRight') || padVirtualRight;
            const up = isActionDown('moveUp') || padVirtualUp;
            const down = isActionDown('moveDown') || padVirtualDown;
            let aimX = left ? -1 : (right ? 1 : 0);
            const aimY = up ? -1 : (down ? 1 : 0);
            if (!aimX && !aimY) aimX = localRunner.facing;
            const aimLen = Math.hypot(aimX, aimY) || 1;
            localRunner.gunAim = Math.atan2(aimY / aimLen, aimX / aimLen);
            localRunner.gunAimUntil = performance.now() + 1000;

            const localSpec = ensureGun(localRunner);
            const fireDown = isActionDown('standardAttack') || !!(pad && pad.buttons[0] && pad.buttons[0].pressed);
            const reloadDown = isActionDown('rangedSpecial') || !!(pad && pad.buttons[10] && pad.buttons[10].pressed);
            if (fireDown && (localSpec.auto || !gunPrevFire)) {
                localRunner.shielding = false;
                fireGun(localRunner, left ? -1 : (right ? 1 : 0), aimY);
            }
            if (reloadDown && !gunPrevReload) startReload(localRunner);
            gunPrevFire = fireDown;
            gunPrevReload = reloadDown;

            ctx.save();
            for (const p of projectiles) {
                if (!p.gun) continue;
                ctx.strokeStyle = p.color;
                ctx.globalAlpha = 0.55;
                ctx.lineWidth = Math.max(1.2, p.radius * 0.8);
                ctx.beginPath();
                ctx.moveTo(p.x - p.vx * 0.018, p.y - p.vy * 0.018);
                ctx.lineTo(p.x, p.y);
                ctx.stroke();
            }
            ctx.restore();

            for (const r of [localRunner, ...getActiveBots(), ...remotePlayers.values()]) {
                drawGunSprite(r);
            }

            const label = localRunner.gunReload > 0
                ? `RELOADING ${Math.round((1 - localRunner.gunReload / localSpec.reload) * 100)}%`
                : `${localRunner.gunAmmo}/${localSpec.mag}`;
            ctx.save();
            ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
            ctx.strokeStyle = '#c7cdd1';
            ctx.beginPath();
            ctx.roundRect(canvas.width / 2 - 120, 6, 240, 20, 10);
            ctx.fill();
            ctx.stroke();
            ctx.font = '800 11px Lato, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillStyle = (localRunner.gunAmmo === 0 || localRunner.gunReload > 0) ? '#dc2626' : '#1c5c43';
            ctx.fillText(`GUN SMASH · ${localSpec.name} · ${label}`, canvas.width / 2, 20);
            ctx.restore();
        }

        function refreshGunButton() {
            const on = gunActive();
            openGunMenuBtn.classList.toggle('ring-2', on);
            openGunMenuBtn.classList.toggle('ring-[#1c5c43]', on);
            openGunMenuBtn.classList.toggle('text-canvas-ucasGreen', on);
        }

        function setGunMode(on, fromSync = false) {
            on = !!on;
            const changed = gunMode !== on;
            gunMode = on;
            projectiles = [];
            if (changed) {
                localRunner.damage = 0;
                localRunner.hitstunTimer = 0;
                localRunner.gunAmmo = undefined;
                cpuBots.forEach(b => { b.damage = 0; b.hitstunTimer = 0; b.gunAmmo = undefined; });
                trainingDummies.forEach(d => { d.damage = d.dummyBaseDmg; d.hitstunTimer = 0; });
                gunPrevFire = false;
                gunPrevReload = false;
                showCanvasToast(on ? 'Gun Smash on: shoot with Left Arrow, reload with Down Arrow' : 'Gun Smash off');
            }
            updateHostControlsUI();
            updateHud();
            renderGunMenu();
            if (amIHost && !fromSync) pushLocalStateToNetwork();
        }

        function setGunType(type) {
            if (!GUN_TYPES[type]) return;
            gunType = type;
            localRunner.gunAmmo = undefined;
            renderGunMenu();
        }

        function startGunSmash() {
            if (!amIHost) {
                showCanvasToast('Only the Room Host can start Gun Smash');
                return;
            }
            if (matchMode !== 'battle') setMatchMode('battle', false);
            if (arenaMap !== gunMenuMap) setArenaMap(gunMenuMap, false);
            setBotCount(gunMenuCpus, false);
            if (gunMode) {
                // Restart: fresh damage, ammo and bullets.
                gunMode = false;
            }
            setGunMode(true, false);
            gunMenuPopover.classList.add('hidden');
            respawnRunners();
        }

        function renderGunMenu() {
            const mark = (btn, on) => {
                btn.classList.toggle('ring-2', on);
                btn.classList.toggle('ring-[#1c5c43]', on);
                btn.classList.toggle('bg-[#f4f6f8]', on);
                btn.classList.toggle('bg-white', !on);
            };
            gunMenuPopover.querySelectorAll('[data-gun-map]').forEach(b => mark(b, b.dataset.gunMap === gunMenuMap));
            gunMenuPopover.querySelectorAll('[data-gun-weapon]').forEach(b => mark(b, b.dataset.gunWeapon === gunType));
            gunMenuPopover.querySelectorAll('[data-gun-cpus]').forEach(b => mark(b, Number(b.dataset.gunCpus) === gunMenuCpus));
            startGunBtn.textContent = gunActive() ? 'Restart Gun Smash' : 'Start Gun Smash';
            stopGunBtn.classList.toggle('hidden', !gunMode);
            gunHostNote.textContent = amIHost
                ? 'You are the room host: starting applies the stage and CPU count to everyone.'
                : 'Only the room host can start or stop Gun Smash. You can still pick your own gun.';
            refreshGunButton();
        }

        openGunMenuBtn.addEventListener('click', () => {
            const wasHidden = gunMenuPopover.classList.contains('hidden');
            closeAllPopovers();
            if (wasHidden) {
                gunMenuMap = arenaMap;
                gunMenuCpus = botCount;
                renderGunMenu();
                gunMenuPopover.classList.remove('hidden');
            }
        });
        closeGunMenuBtn.addEventListener('click', () => gunMenuPopover.classList.add('hidden'));
        gunMenuPopover.addEventListener('click', (event) => {
            const mapBtn = event.target.closest('[data-gun-map]');
            const weaponBtn = event.target.closest('[data-gun-weapon]');
            const cpuBtn = event.target.closest('[data-gun-cpus]');
            if (mapBtn) { gunMenuMap = mapBtn.dataset.gunMap; renderGunMenu(); }
            if (weaponBtn) setGunType(weaponBtn.dataset.gunWeapon);
            if (cpuBtn) { gunMenuCpus = Number(cpuBtn.dataset.gunCpus); renderGunMenu(); }
        });
        startGunBtn.addEventListener('click', startGunSmash);
        stopGunBtn.addEventListener('click', () => {
            if (!amIHost) {
                showCanvasToast('Only the Room Host can stop Gun Smash');
                return;
            }
            setGunMode(false, false);
        });
        // Switching the normal Mode button away from Smash Battle turns Gun Smash off.
        toggleMatchModeBtn.addEventListener('click', () => {
            if (gunMode && matchMode !== 'battle') setGunMode(false, true);
            refreshGunButton();
        });

        """

# --------------------------------------------------------------------------
# README addition
# --------------------------------------------------------------------------
README_SECTION = r"""## Gun Smash

Click **Gun Smash** in the HUD to open its menu: pick a stage (Canvas, myUVU or Training), your gun (pistol, rifle or shotgun) and the number of CPUs, then start. It uses normal Smash damage % and knockback, but you fight with a gun.

- Left Arrow (gamepad A): shoot (hold for the rifle)
- W / A / S / D while shooting: aim up, down or diagonally
- Down Arrow (gamepad L3): reload (also automatic when empty)
- Right Arrow: melee smash, Up Arrow: recovery, Q: shield
- Only the room host can start or stop it; everyone in the room follows.

"""


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    with open(path, encoding='utf-8', newline='') as fh:
        raw = fh.read()
    crlf = '\r\n' in raw
    src = raw.replace('\r\n', '\n')

    if 'id="gun-menu-popover"' in src:
        sys.exit('index.html already contains Gun Smash; nothing to do.')

    edits = []

    def rep(old, new, count=1):
        edits.append((old, new, count))

    # 1. HUD button + menu markup
    rep('<button id="reset-dummies-btn"', HUD_BUTTON + '<button id="reset-dummies-btn"')
    rep('<div id="settings-popover"', MENU_HTML + '<div id="settings-popover"')

    # 2. Popover close + mode label
    rep('function closeAllPopovers() {',
        'function closeAllPopovers() {\n            gunMenuPopover.classList.add(\'hidden\');')
    rep('toggleMatchModeBtn.textContent = `${prefix} Mode: ${modeLabel}`;',
        "toggleMatchModeBtn.textContent = `${prefix} Mode: ${gunActive() ? 'Gun Smash' : modeLabel}`;\n"
        '            refreshGunButton();')

    # 3. Network sync (state payload, host-driven gunMode, shot visuals)
    rep('grappleActive: localRunner.grapple.active,',
        'grappleActive: localRunner.grapple.active,\n                gunMode: gunMode,\n                gunType: gunType,')
    rep('rp.lastSeen = Date.now();',
        'rp.lastSeen = Date.now();\n'
        "            rp.gunType = data.gunType || 'pistol';\n"
        '            if (data.isHost && !amIHost && data.room === currentRoom && gunMode !== !!data.gunMode) {\n'
        '                setGunMode(!!data.gunMode, true);\n'
        '            }')
    rep("} else if (msg.type === 'smash-hit') {",
        "} else if (msg.type === 'gun-shot') {\n"
        '                handleRemoteGunShot(msg);\n'
        "            } else if (msg.type === 'smash-hit') {")
    rep('if (!target || target.id === p.ownerId) continue;',
        'if (!target || target.id === p.ownerId || p.visual) continue;')

    # 4. Replace melee/specials with the gun while Gun Smash is active
    rep("if (matchMode === 'battle' && bot.aiActionTimer <= 0) {",
        "if (gunActive()) {\n"
        '                gunBotAi(bot, target, dist, dx, dy);\n'
        "            } else if (matchMode === 'battle' && bot.aiActionTimer <= 0) {")
    rep("if (action === 'standardAttack') performStandardAttackInput(localRunner, aimX, aimY);",
        "if (action === 'standardAttack' && !gunActive()) performStandardAttackInput(localRunner, aimX, aimY);", 2)
    rep("if (action === 'rangedSpecial') triggerClassRangedSpecial(localRunner);",
        "if (action === 'rangedSpecial' && !gunActive()) triggerClassRangedSpecial(localRunner);", 2)
    rep('if (justPressed(0)) {', 'if (justPressed(0) && !gunActive()) {')

    # 5. Game loop: no hitstop / heavy shake from rapid bullet hits, draw guns
    rep('hitstopTimer -= dt;', 'hitstopTimer -= dt;\n                if (gunActive()) hitstopTimer = 0;')
    rep('screenShakeTimer -= dt;',
        'screenShakeTimer -= dt;\n                if (gunActive()) screenShakeIntensity = Math.min(screenShakeIntensity, 1.5);')
    rep('drawRunner(localRunner, getEffectivePlayerName(), true);',
        'drawRunner(localRunner, getEffectivePlayerName(), true);\n            gunFrame(dt);')

    # 6. Module code
    marker = '// Initialize customizer swatches, fighter roster, and multiplayer network'
    rep(marker, JS_BLOCK + marker)

    # Validate every anchor before touching anything.
    for old, _new, count in edits:
        found = src.count(old)
        if found != count:
            sys.exit(f'Aborted, nothing changed. Expected {count} match(es) but found {found} for:\n  {old[:90]!r}\n'
                     'This script is written for the current index.html; the file has changed since.')
    for old, new, _count in edits:
        src = src.replace(old, new)

    with open(path + '.bak', 'w', encoding='utf-8', newline='') as fh:
        fh.write(raw)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(src.replace('\n', '\r\n') if crlf else src)
    print(f'Patched {path} (backup: {path}.bak)')

    readme = os.path.join(os.path.dirname(os.path.abspath(path)), 'README.md')
    if os.path.exists(readme):
        with open(readme, encoding='utf-8', newline='') as fh:
            text = fh.read()
        anchor = '## Gameplay and multiplayer'
        if '## Gun Smash' not in text and anchor in text:
            nl = '\r\n' if '\r\n' in text else '\n'
            section = README_SECTION.replace('\n', nl)
            with open(readme, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text.replace(anchor, section + anchor, 1))
            print('Updated README.md')


if __name__ == '__main__':
    main()
