"""
pyinfra deploy for the Miserable_Xfce Debian/Xfce build.

Usage example:
    pyinfra inventory.py deploy.py \
        -D desktop_user=alice \
        -D desktop_home=/home/alice

Optional pinned picom animation fork build:
    pyinfra inventory.py deploy.py \
        -D desktop_user=alice \
        -D picom_commit=<full_commit_sha>
"""

from io import StringIO
from pathlib import Path
from shlex import quote

from pyinfra import host
from pyinfra.operations import apt, files, git, server, systemd


REPO_ROOT = Path(__file__).resolve().parent
HOME_SRC = REPO_ROOT / "home"

DESKTOP_USER = host.data.get("desktop_user")
if not DESKTOP_USER:
    raise ValueError("Set -D desktop_user=<target desktop user> when running this deploy.")

DESKTOP_GROUP = host.data.get("desktop_group", DESKTOP_USER)
DESKTOP_HOME = host.data.get("desktop_home", f"/home/{DESKTOP_USER}")

INSTALL_OPTIONAL_PACKAGES = host.data.get("install_optional_packages", False)
MANAGE_DISPLAY_MANAGER = host.data.get("manage_display_manager", True)
INSTALL_EWW = host.data.get("install_eww", True)
EWW_REPO = host.data.get("eww_repo", "https://github.com/elkowar/eww.git")
EWW_REF = host.data.get("eww_ref", "master")
EWW_FEATURES = host.data.get("eww_features", "x11")
EWW_BUILD_DIR = host.data.get("eww_build_dir", f"{DESKTOP_HOME}/.cache/build/eww")
PICOM_COMMIT = host.data.get("picom_commit")
PICOM_REPO = host.data.get("picom_repo", "https://github.com/fdev31/picom.git")
PICOM_BRANCH = host.data.get("picom_branch", "animation-pr")
PICOM_BUILD_DIR = host.data.get("picom_build_dir", f"{DESKTOP_HOME}/.cache/build/picom-animation")
I3LOCK_COLOR_REPO = host.data.get("i3lock_color_repo", "https://github.com/Raymo111/i3lock-color.git")
I3LOCK_COLOR_REF = host.data.get("i3lock_color_ref", "master")
I3LOCK_COLOR_BUILD_DIR = host.data.get("i3lock_color_build_dir", f"{DESKTOP_HOME}/.cache/build/i3lock-color")
FINDEX_REPO = host.data.get("findex_repo", "https://github.com/mdgaziur/findex.git")
FINDEX_REF = host.data.get("findex_ref")
FINDEX_BUILD_DIR = host.data.get("findex_build_dir", f"{DESKTOP_HOME}/.cache/build/findex")
PURE_INSTALL_DIR = "/usr/local/share/zsh/site-functions/pure"
FLUENT_ICON_REPO = host.data.get("fluent_icon_repo", "https://github.com/vinceliuice/Fluent-icon-theme.git")
FLUENT_ICON_REF = host.data.get("fluent_icon_ref", "master")
FLUENT_ICON_BUILD_DIR = host.data.get("fluent_icon_build_dir", f"{DESKTOP_HOME}/.cache/build/Fluent-icon-theme")
ZAFIRO_ICON_REPO = host.data.get("zafiro_icon_repo", "https://github.com/zayronxio/Zafiro-icons.git")
ZAFIRO_ICON_REF = host.data.get("zafiro_icon_ref", "master")
ZAFIRO_ICON_BUILD_DIR = host.data.get("zafiro_icon_build_dir", f"{DESKTOP_HOME}/.cache/build/Zafiro-icons")
OVERPASS_REPO = host.data.get("overpass_repo", "https://github.com/RedHatOfficial/Overpass.git")
OVERPASS_REF = host.data.get("overpass_ref", "v3.0.5")
OVERPASS_BUILD_DIR = host.data.get("overpass_build_dir", f"{DESKTOP_HOME}/.cache/build/overpass")
FEATHER_FONT_REPO = host.data.get("feather_font_repo", "https://github.com/AT-UI/feather-font.git")
FEATHER_FONT_BUILD_DIR = host.data.get("feather_font_build_dir", f"{DESKTOP_HOME}/.cache/build/feather-font")
JETBRAINS_NERD_FONT_VERSION = host.data.get("jetbrains_nerd_font_version", "v3.4.0")
JETBRAINS_NERD_FONT_BUILD_DIR = host.data.get("jetbrains_nerd_font_build_dir", f"{DESKTOP_HOME}/.cache/build/JetBrainsMono-nerd-font")

PICOM_BUILD_DIR_Q = quote(PICOM_BUILD_DIR)
PICOM_COMMIT_Q = quote(PICOM_COMMIT) if PICOM_COMMIT else None
EWW_BUILD_DIR_Q = quote(EWW_BUILD_DIR)
EWW_REF_Q = quote(EWW_REF)
I3LOCK_COLOR_BUILD_DIR_Q = quote(I3LOCK_COLOR_BUILD_DIR)
I3LOCK_COLOR_REF_Q = quote(I3LOCK_COLOR_REF)
FINDEX_BUILD_DIR_Q = quote(FINDEX_BUILD_DIR)
FLUENT_ICON_BUILD_DIR_Q = quote(FLUENT_ICON_BUILD_DIR)
ZAFIRO_ICON_BUILD_DIR_Q = quote(ZAFIRO_ICON_BUILD_DIR)
OVERPASS_BUILD_DIR_Q = quote(OVERPASS_BUILD_DIR)
FEATHER_FONT_BUILD_DIR_Q = quote(FEATHER_FONT_BUILD_DIR)
JETBRAINS_NERD_FONT_BUILD_DIR_Q = quote(JETBRAINS_NERD_FONT_BUILD_DIR)


def read_repo_text(relative_path):
    return (HOME_SRC / relative_path).read_text()


def upload_sanitized_text(name, relative_path, dest, replacements, mode="644"):
    content = read_repo_text(relative_path)
    for old, new in replacements:
        if old not in content:
            raise ValueError(f"Expected patch target not found in {relative_path!r}: {old!r}")
        content = content.replace(old, new)

    files.put(
        name=name,
        src=StringIO(content),
        dest=dest,
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
        mode=mode,
        add_deploy_dir=False,
    )


apt.packages(
    name="Install Debian Xfce desktop packages",
    packages=[
        "xfce4",
        "xfce4-goodies",
        "lightdm",
        "lightdm-gtk-greeter",
        "fonts-noto",
        "papirus-icon-theme",
        "numix-icon-theme",
        "numix-icon-theme-circle",
        "thunar",
        "xfce4-panel",
        "xfce4-panel-profiles",
        "xfce4-docklike-plugin",
        "bat",
        "rofi",
        "onboard",
        "picom",
        "i3lock",
        "rsync",
        "zsh",
        "zsh-syntax-highlighting",
        "git",
        "curl",
        "wget",
        "unzip",
        "jq",
        "imagemagick",
        "playerctl",
        "python3",
        "python3-gi",
        "python3-requests",
        "gir1.2-playerctl-2.0",
        "autoconf",
        "build-essential",
        "rustc",
        "cargo",
        "meson",
        "ninja-build",
        "pkg-config",
        "libgtk-3-dev",
        "libkeybinder-3.0-dev",
        "libpango1.0-dev",
        "libgdk-pixbuf-2.0-dev",
        "libdbusmenu-gtk3-dev",
        "libcairo2-dev",
        "libglib2.0-dev",
        "libxext-dev",
        "libxcb1-dev",
        "libxcb-damage0-dev",
        "libxcb-dpms0-dev",
        "libxcb-xfixes0-dev",
        "libxcb-shape0-dev",
        "libxcb-render-util0-dev",
        "libxcb-render0-dev",
        "libxcb-randr0-dev",
        "libxcb-composite0-dev",
        "libxcb-image0-dev",
        "libxcb-present-dev",
        "libxcb-glx0-dev",
        "libxcb-xkb-dev",
        "libxcb-xinerama0-dev",
        "libxcb-util0-dev",
        "libxcb-xrm-dev",
        "libpixman-1-dev",
        "libdbus-1-dev",
        "libconfig-dev",
        "libgl-dev",
        "libegl-dev",
        "libpcre2-dev",
        "libevdev-dev",
        "libev-dev",
        "libx11-xcb-dev",
        "libpam0g-dev",
        "libfontconfig1-dev",
        "libxkbcommon-dev",
        "libxkbcommon-x11-dev",
        "libjpeg-dev",
        "libgif-dev",
        "uthash-dev",
    ],
    update=True,
    cache_time=3600,
    _sudo=True,
)

if INSTALL_OPTIONAL_PACKAGES:
    apt.packages(
        name="Install optional packages that may require extra Debian repositories",
        packages=host.data.get("optional_packages", ["neofetch", "skippy-xd"]),
        update=True,
        cache_time=3600,
        _sudo=True,
    )

if MANAGE_DISPLAY_MANAGER:
    for service in ["gdm3", "sddm"]:
        systemd.service(
            name=f"Disable competing display manager {service}",
            service=service,
            enabled=False,
            running=False,
            _sudo=True,
            _ignore_errors=True,
        )

    systemd.service(
        name="Enable LightDM",
        service="lightdm",
        enabled=True,
        _sudo=True,
    )

for path in [
    ".assets",
    ".config",
    ".local/bin",
    ".local/share/backgrounds",
    ".local/share/icons",
    ".local/share/onboard",
    ".themes",
]:
    files.rsync(
        name=f"Sync {path}",
        src=str(HOME_SRC / path) + "/",
        dest=f"{DESKTOP_HOME}/{path}/",
        flags=["-a", "--no-perms", "--chmod=F644,D755", f"--chown={DESKTOP_USER}:{DESKTOP_GROUP}"],
        _sudo=True,
    )

if INSTALL_EWW:
    files.directory(
        name="Ensure EWW build directory exists",
        path=EWW_BUILD_DIR,
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
        mode="755",
    )

    git.repo(
        name="Clone EWW source",
        src=EWW_REPO,
        dest=EWW_BUILD_DIR,
        branch=EWW_REF,
        pull=True,
        update_submodules=True,
        recursive_submodules=True,
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
    )

    server.shell(
        name="Check out requested EWW ref",
        commands=f"git -C {EWW_BUILD_DIR_Q} checkout {EWW_REF_Q}",
        _sudo=True,
        _sudo_user=DESKTOP_USER,
    )

    server.shell(
        name="Build EWW for X11",
        commands=(
            f"cd {EWW_BUILD_DIR_Q} && "
            f"cargo build --release --no-default-features --features {quote(EWW_FEATURES)}"
        ),
        _sudo=True,
        _sudo_user=DESKTOP_USER,
    )

    server.shell(
        name="Install EWW binary",
        commands=(
            f"if ! cmp -s {quote(f'{EWW_BUILD_DIR}/target/release/eww')} /usr/local/bin/eww; then "
            f"install -m 0755 {quote(f'{EWW_BUILD_DIR}/target/release/eww')} /usr/local/bin/eww; "
            "fi"
        ),
        _sudo=True,
    )

files.directory(
    name="Ensure i3lock-color build directory exists",
    path=I3LOCK_COLOR_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

git.repo(
    name="Clone i3lock-color source",
    src=I3LOCK_COLOR_REPO,
    dest=I3LOCK_COLOR_BUILD_DIR,
    branch=I3LOCK_COLOR_REF,
    pull=True,
    _sudo=True,
)

server.shell(
    name="Build and install i3lock-color",
    commands=(
        f"cd {I3LOCK_COLOR_BUILD_DIR_Q} && "
        'git tag -f "git-$(git rev-parse --short HEAD)" && '
        "./install-i3lock-color.sh"
    ),
    _sudo=True,
)

files.directory(
    name="Ensure findex build directory exists",
    path=FINDEX_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

files.directory(
    name="Ensure /opt/findex exists",
    path="/opt/findex",
    mode="755",
    _sudo=True,
)

git.repo(
    name="Clone findex source",
    src=FINDEX_REPO,
    dest=FINDEX_BUILD_DIR,
    branch=FINDEX_REF,
    pull=True,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
)

server.shell(
    name="Build findex",
    commands=f"cd {FINDEX_BUILD_DIR_Q} && cargo build --release",
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

server.shell(
    name="Install findex CSS",
    commands=(
        f"if ! diff -q {quote(f'{FINDEX_BUILD_DIR}/css/style.css')} /opt/findex/style.css >/dev/null 2>&1; then "
        f"cp {quote(f'{FINDEX_BUILD_DIR}/css/style.css')} /opt/findex/style.css; "
        "fi"
    ),
    _sudo=True,
)

server.shell(
    name="Install findex binaries",
    commands=[
        f"if ! cmp -s {quote(f'{FINDEX_BUILD_DIR}/target/release/findex')} /usr/bin/findex; then "
        f"install -m 0755 {quote(f'{FINDEX_BUILD_DIR}/target/release/findex')} /usr/bin/findex; fi",
        f"if ! cmp -s {quote(f'{FINDEX_BUILD_DIR}/target/release/findex-daemon')} /usr/bin/findex-daemon; then "
        f"install -m 0755 {quote(f'{FINDEX_BUILD_DIR}/target/release/findex-daemon')} /usr/bin/findex-daemon; fi",
    ],
    _sudo=True,
)

server.shell(
    name="Enable and start findex-daemon user service",
    commands=(
        f"uid=$(id -u {quote(DESKTOP_USER)}) && "
        f"bus=unix:path=/run/user/$uid/bus && "
        f"sudo -u {quote(DESKTOP_USER)} XDG_RUNTIME_DIR=/run/user/$uid DBUS_SESSION_BUS_ADDRESS=$bus "
        "systemctl --user enable findex-daemon.service && "
        f"sudo -u {quote(DESKTOP_USER)} XDG_RUNTIME_DIR=/run/user/$uid DBUS_SESSION_BUS_ADDRESS=$bus "
        "systemctl --user start findex-daemon.service || true"
    ),
    _sudo=True,
)

files.directory(
    name="Ensure user cache directory exists",
    path=f"{DESKTOP_HOME}/.cache",
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="700",
)

files.block(
    name="Merge Miserable_Xfce profile environment",
    path=f"{DESKTOP_HOME}/.profile",
    content=[
        'export QT_QPA_PLATFORMTHEME="qt5ct"',
        "export QT_AUTO_SCREEN_SCALE_FACTOR=0",
        'export GTK2_RC_FILES="$HOME/.gtkrc-2.0"',
        'case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) export PATH="$PATH:$HOME/.local/bin" ;; esac',
    ],
    marker="# {mark} PYINFRA MANAGED MISERABLE_XFCE PROFILE",
)

files.block(
    name="Merge Miserable_Xfce Xresources colors",
    path=f"{DESKTOP_HOME}/.Xresources",
    content=read_repo_text(".Xresources"),
    marker="! {mark} PYINFRA MANAGED MISERABLE_XFCE XRESOURCES",
)

files.block(
    name="Merge Miserable_Xfce zsh configuration",
    path=f"{DESKTOP_HOME}/.zshrc",
    content=read_repo_text(".zshrc").replace(
        "autoload -U promptinit; promptinit",
        f"fpath+={PURE_INSTALL_DIR}\nautoload -U promptinit; promptinit",
    ),
    marker="# {mark} PYINFRA MANAGED MISERABLE_XFCE ZSH",
)

files.directory(
    name="Ensure user environment.d directory exists",
    path=f"{DESKTOP_HOME}/.config/environment.d",
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

files.put(
    name="Document optional Gmail environment variables for EWW",
    src=StringIO(
        "# Optional Gmail widget credentials for EWW user sessions.\n"
        "# Prefer setting these outside git-managed files, for example here:\n"
        "# MISERABLE_GMAIL_USER=username@gmail.com\n"
        "# MISERABLE_GMAIL_APP_PASSWORD=app_password\n"
        "# Log out and back in after changing this file.\n"
    ),
    dest=f"{DESKTOP_HOME}/.config/environment.d/miserable-xfce-gmail.conf.example",
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="600",
    add_deploy_dir=False,
)

for dotfile in [".profile", ".Xresources"]:
    files.file(
        name=f"Set ownership and mode on {dotfile}",
        path=f"{DESKTOP_HOME}/{dotfile}",
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
        mode="644",
    )

upload_sanitized_text(
    name="Fix hardcoded icon path in sidebar launcher",
    relative_path=".config/xfce4/panel/launcher-1/16790342511.desktop",
    dest=f"{DESKTOP_HOME}/.config/xfce4/panel/launcher-1/16790342511.desktop",
    replacements=[
        (
            "Icon=/home/mehedirm6244/Dots/dotfile/components/windows-color.svg",
            f"Icon={DESKTOP_HOME}/.assets/Menu.svg",
        ),
    ],
)

upload_sanitized_text(
    name="Fix hardcoded icon path in expose launcher",
    relative_path=".config/xfce4/panel/launcher-12/16844757053.desktop",
    dest=f"{DESKTOP_HOME}/.config/xfce4/panel/launcher-12/16844757053.desktop",
    replacements=[
        (
            "Icon=/home/mehedirm6244/.assets/icons/stack.svg",
            f"Icon={DESKTOP_HOME}/.assets/stack.svg",
        ),
    ],
)

upload_sanitized_text(
    name="Fix hardcoded icon path in system stats launcher",
    relative_path=".config/xfce4/panel/launcher-17/16825992421.desktop",
    dest=f"{DESKTOP_HOME}/.config/xfce4/panel/launcher-17/16825992421.desktop",
    replacements=[
        (
            "Icon=/home/mehedirm6244/.assets/icons/activity.svg",
            f"Icon={DESKTOP_HOME}/.assets/activity.svg",
        ),
    ],
)

for script in [
    ".config/eww/scripts/battery",
    ".config/eww/scripts/cpu",
    ".config/eww/scripts/disk",
    ".config/eww/scripts/gmail.sh",
    ".config/eww/scripts/launch.sh",
    ".config/eww/scripts/mem",
    ".config/eww/scripts/playerctl.py",
    ".config/eww/scripts/processes",
    ".config/eww/scripts/spotify_helper",
    ".config/eww/scripts/swap",
    ".config/eww/scripts/updates",
    ".config/eww/scripts/uptime",
    ".config/eww/scripts/weather",
    ".config/eww/scripts/weather_reload",
    ".config/eww/scripts/wifi",
    ".local/bin/lock.sh",
    ".local/bin/skippy.sh",
]:
    files.file(
        name=f"Ensure {script} is executable",
        path=f"{DESKTOP_HOME}/{script}",
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
        mode="755",
    )

BG_PATH = quote(f"{DESKTOP_HOME}/.local/share/backgrounds/nomanssky.png")

files.directory(
    name="Ensure xfce4 xfconf perchannel-xml directory exists",
    path=f"{DESKTOP_HOME}/.config/xfce4/xfconf/xfce-perchannel-xml",
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

files.template(
    name="Set desktop wallpaper via xfconf config",
    src="templates/xfce4-desktop.xml.j2",
    dest=f"{DESKTOP_HOME}/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml",
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="644",
    bg_path=f"{DESKTOP_HOME}/.local/share/backgrounds/nomanssky.png",
)

server.shell(
    name="Pre-cache lockscreen background",
    commands=(
        f"convert {BG_PATH} "
        f"-resize 1920x1080^ -gravity center -extent 1920x1080 "
        f"-brightness-contrast -15x0 -filter Gaussian -blur 0x5 "
        f"{quote(f'{DESKTOP_HOME}/lockscreen.png')}"
    ),
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

server.shell(
    name="Install pure zsh prompt from GitHub",
    commands=(
        f"if [ ! -f {quote(PURE_INSTALL_DIR + '/pure.zsh')} ]; then "
        f"git clone --depth=1 https://github.com/sindresorhus/pure.git {quote(PURE_INSTALL_DIR)}; "
        "fi"
    ),
    _sudo=True,
)

files.directory(
    name="Ensure Fluent icon theme build directory exists",
    path=FLUENT_ICON_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

git.repo(
    name="Clone Fluent icon theme",
    src=FLUENT_ICON_REPO,
    dest=FLUENT_ICON_BUILD_DIR,
    branch=FLUENT_ICON_REF,
    pull=True,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
)

server.shell(
    name="Install Fluent icon themes (light and dark)",
    commands=(
        f"cd {FLUENT_ICON_BUILD_DIR_Q} && "
        f"./install.sh -n Fluent -a -d {quote(f'{DESKTOP_HOME}/.local/share/icons')}"
    ),
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

files.directory(
    name="Ensure Zafiro icon theme build directory exists",
    path=ZAFIRO_ICON_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

git.repo(
    name="Clone Zafiro icon theme",
    src=ZAFIRO_ICON_REPO,
    dest=ZAFIRO_ICON_BUILD_DIR,
    branch=ZAFIRO_ICON_REF,
    pull=True,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
)

files.rsync(
    name="Install Zafiro icon theme",
    src=ZAFIRO_ICON_BUILD_DIR_Q + "/",
    dest=f"{DESKTOP_HOME}/.local/share/icons/Zafiro/",
    flags=["-a", "--no-perms", "--chmod=F644,D755", f"--chown={DESKTOP_USER}:{DESKTOP_GROUP}", "--exclude=.git"],
    _sudo=True,
)

files.directory(
    name="Ensure Overpass font build directory exists",
    path=OVERPASS_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

git.repo(
    name="Clone Overpass font",
    src=OVERPASS_REPO,
    dest=OVERPASS_BUILD_DIR,
    branch=OVERPASS_REF,
    pull=False,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
)

server.shell(
    name="Install Overpass font files",
    commands=(
        f"find {OVERPASS_BUILD_DIR_Q} -name '*.ttf' -exec cp {{}} "
        f"{quote(f'{DESKTOP_HOME}/.local/share/fonts/')} \\;"
    ),
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

files.directory(
    name="Ensure Feather font build directory exists",
    path=FEATHER_FONT_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

git.repo(
    name="Clone Feather font",
    src=FEATHER_FONT_REPO,
    dest=FEATHER_FONT_BUILD_DIR,
    pull=True,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
)

server.shell(
    name="Install Feather font file",
    commands=(
        f"cp {FEATHER_FONT_BUILD_DIR_Q}/src/fonts/feather.ttf "
        f"{quote(f'{DESKTOP_HOME}/.local/share/fonts/')}"
    ),
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

files.directory(
    name="Ensure JetBrainsMono Nerd Font build directory exists",
    path=JETBRAINS_NERD_FONT_BUILD_DIR,
    user=DESKTOP_USER,
    group=DESKTOP_GROUP,
    mode="755",
)

server.shell(
    name="Download and install JetBrainsMono Nerd Font",
    commands=(
        f"wget -q -O {JETBRAINS_NERD_FONT_BUILD_DIR_Q}/JetBrainsMono.zip "
        f"https://github.com/ryanoasis/nerd-fonts/releases/download/{JETBRAINS_NERD_FONT_VERSION}/JetBrainsMono.zip && "
        f"unzip -o -j {JETBRAINS_NERD_FONT_BUILD_DIR_Q}/JetBrainsMono.zip '*.ttf' "
        f"-d {quote(f'{DESKTOP_HOME}/.local/share/fonts/')}"
    ),
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

server.shell(
    name="Rebuild user font cache",
    commands="fc-cache -f",
    _sudo=True,
    _sudo_user=DESKTOP_USER,
)

if PICOM_COMMIT:
    files.directory(
        name="Ensure pinned picom build directory exists",
        path=PICOM_BUILD_DIR,
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
        mode="755",
    )

    git.repo(
        name="Clone pinned picom animation fork source",
        src=PICOM_REPO,
        dest=PICOM_BUILD_DIR,
        branch=PICOM_BRANCH,
        pull=False,
        update_submodules=True,
        recursive_submodules=True,
        user=DESKTOP_USER,
        group=DESKTOP_GROUP,
    )

    server.shell(
        name="Check out requested picom commit",
        commands=f"git -C {PICOM_BUILD_DIR_Q} checkout --detach {PICOM_COMMIT_Q}",
        _sudo=True,
        _sudo_user=DESKTOP_USER,
    )

    server.shell(
        name="Configure pinned picom build",
        commands=(
            f"if [ -d {quote(f'{PICOM_BUILD_DIR}/build/meson-private')} ]; then "
            f"meson setup --reconfigure {quote(f'{PICOM_BUILD_DIR}/build')}; "
            f"else meson setup --buildtype=release --prefix=/usr/local "
            f"{quote(f'{PICOM_BUILD_DIR}/build')} {PICOM_BUILD_DIR_Q}; fi"
        ),
        _sudo=True,
        _sudo_user=DESKTOP_USER,
    )

    server.shell(
        name="Build pinned picom",
        commands=f"ninja -C {quote(f'{PICOM_BUILD_DIR}/build')}",
        _sudo=True,
        _sudo_user=DESKTOP_USER,
    )

    server.shell(
        name="Install pinned picom",
        commands=f"ninja -C {quote(f'{PICOM_BUILD_DIR}/build')} install",
        _sudo=True,
    )
