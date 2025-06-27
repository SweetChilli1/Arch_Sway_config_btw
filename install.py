# You must install typing_extension $ sudo pacman -S python-typing_extensions

import subprocess as sub
import shutil
from pathlib import Path
from typing_extensions import Union


paru_paketes = [
    "fastfetch",
    "sway",
    "xwayland",
    "waybar",
    "rofi",
    "firefox",
    "mullvad-vpn-bin",
    "yazi",
    "ytop",
    "bat",
    "zsh",
    "exa",
    "fzf",
    "vim",
    "neovim",
    "wget",
    "ghostty",
    "swaybg",
    "swaycli",
]

pacman_pakets = ["git", "figlet", "--needed base_devel", "curl"]

error_list = []


def install_paru():
    target_dir = Path.home()
    repo_url = "https://aur.archlinux.org/paru.git"
    clone_dir = target_dir / "paru"

    if not clone_dir.exists():
        sub.run(
            [
                "git",
                "clone",
                repo_url,
                str(clone_dir),
            ],
            check=True,
        )
    else:
        print(f"{clone_dir} already exists -> is sikipped")

    try:
        sub.run(["makepkg", "-si"], cwd=clone_dir)
        print("✅ paru has been successfully installed")
    except Exception as e:
        print(f"❌ ERROR: Installation failed: {e}")
        print("exit script")
        exit()


def install_paketes(paket_list, paketmanager):
    for paket in paket_list:
        try:
            sub.run(["sudo", paketmanager, "-S", paket, "--noconfirm"], check=True)
        except sub.CalledProcessError as e:
            print(f"ERROR: fail to install {paket}: error: {e.returncode}")
        except FileNotFoundError:
            print(f"'{paketmanager}' not found")
            exit()
        except Exception as e:
            print(
                f"❌ ERROR: an unexpected error has occurred during the installation of: {paket}. error: {e}"
            )
            error_list.append(f"fail: {paket}")

    if error_list:
        print(error_list)
    else:
        print("🎉 every paket installed successfully")


def install_configs():
    current_dir = Path(__file__).resolve().parent
    dotfiles_dir = current_dir / "dotfiles"
    target_config_dir = Path.home() / ".config"
    run_sub_try_expeckt(f"chmod +x {dotfiles_dir}/waybar/scripts/toggle-rofi.sh")
    for config_dir in dotfiles_dir.iterdir():
        if config_dir.is_dir():
            target_dir = target_config_dir / config_dir.name
            backup_dir = target_config_dir / f"{config_dir}.bak"
            check_if_target_exist(target_dir, backup_dir)

            print(f"✅ copy {config_dir} -> ~/.config/{target_dir}")
            shutil.copytree(str(config_dir), target_dir)

    zsh_configs = [".zshrc", ".p10k.zsh"]
    home_dir = Path.home()

    for filename in zsh_configs:
        source = dotfiles_dir / filename
        target = home_dir / filename
        backup = home_dir / f"{filename}.bak"

        if source.exists():
            check_if_target_exist(Path(target), Path(backup))
            print(f"✅ copy {source} -> ~/.config/{target}")
            shutil.copytree(str(source), target)


def check_if_target_exist(target: Path, backup: Path):
    if target.exists():
        print(f"⚠️ {target} already exist -> will be renamed to {backup}")
        if backup.exists():
            print(f"🗑️ remove existing backup: {backup}")
            if backup.is_dir:
                shutil.rmtree(backup)
            else:
                backup.unlink()

        target.rename(backup)


def run_sub_try_expeckt(command: Union[str, list[str]], *, use_shell=False):
    try:
        sub.run(command, shell=use_shell, check=True)
    except sub.CalledProcessError as e:
        print(f"❌ ERROR: error durin executing of {command}: {e.returncode}")
    except FileNotFoundError:
        print(f"❌ ERROR: {command} not found!")
    except Exception as e:
        print(f"❌ ERROR: An unexpected error has occurred: {e} ")


def main():
    print("installiere Abhängigkeiten")
    install_paketes(pacman_pakets, "pacman")
    sub.run(["figlet", "Install your system"])

    # install Rust and rustup
    try:
        run_sub_try_expeckt(
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            use_shell=True,
        )
        run_sub_try_expeckt("source .cargo/env", use_shell=True)
    except Exception as e:
        print(f"❌ ERROR: unexpected fail: {e} ")
        print("❌ exit script ❌")
        exit()

    install_paru()

    install_configs()

    install_paketes(paru_paketes, "paru")

    run_sub_try_expeckt("chsh -s $(which zsh)", use_shell=True)

    run_sub_try_expeckt("fastfetch")

    print(f"Fail lis: {error_list}")
    print("🎉 Your system is installed 🎉")

    while True:
        user_input = input("reboot system now? (y/n): ").lower()
        if user_input == "y":
            print("reboot system")
            run_sub_try_expeckt("sudo reboot", use_shell=True)
        elif user_input == "n":
            print("script exit")
            exit()
        else:
            print("❌ ERROR: invalid input")


if __name__ == "__main__":
    while True:
        user_input = input("Start the script? (y/n): ").lower()
        if user_input == "y" or "j":
            main()
        elif user_input == "n":
            print("exit script")
        else:
            print("❌ ERROR: invalid input")
