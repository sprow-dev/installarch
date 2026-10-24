# >=run this to do=----------------------------------------------------------------------------------===>v
# ^  curl -fsSL https://raw.githubusercontent.com/sprow-dev/installarch/refs/heads/main/begin.sh | bash  v
# ^=--------------------------------------------------------------------------------------------------===>>>>>

from dataclasses import dataclass, field
import shutil
import subprocess
import json
import pathlib
from rich import print as rprint
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Note: Who cares about error checking?

@dataclass
class DiskManager:
    """A streamlined tool to format and configure existing disk partitions."""
    selected_disk: str = ""
    available_partitions: list = field(default_factory=list)
    configured_partitions: list = field(default_factory=list)

    def run(self) -> None:
        """Main execution flow for the disk manager."""
        rprint("[bold yellow]I vibecoded this so don't judge[/bold yellow]")
        rprint(Panel("[bold cyan]fdisk on fent[/bold cyan]", expand=False))
        self.select_disk()

        if self.selected_disk and self.available_partitions:
            self.configure_partitions()
            self.summary()
        elif self.selected_disk:
            rprint("[bold red]error: You clearly did not partition your disk and listen so please go back and do that.[/bold red]")

    def select_disk(self) -> None:
        """Lists available disks, prompts for selection, and reads existing partitions."""
        try:
            # Query block devices including child partitions and labels in JSON format
            result = subprocess.run(
                ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,LABEL"],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            disks = [dev for dev in data.get("blockdevices", []) if dev.get("type") == "disk"]
        except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
            rprint("[red]error: lsblk did not lsblk[/red]")
            return

        rprint("\n[bold yellow]Available Disks:[/bold yellow]")
        disk_choices = []
        for i, d in enumerate(disks, 1):
            name = d.get("name")
            size = d.get("size", "Unknown")
            rprint(f"  [green]{i}[/green]. /dev/{name} ([bold]{size}[/bold])")
            disk_choices.append(str(i))

        choice = Prompt.ask("Select a disk number", choices=disk_choices)
        selected = disks[int(choice) - 1]
        self.selected_disk = f"/dev/{selected['name']}"

        # Capture existing child partitions belonging to this disk
        self.available_partitions = selected.get("children", [])
        rprint(f"[bold blue]Target Disk Set:[/bold blue] {self.selected_disk}\n")

    def configure_partitions(self) -> None:
        """Interactive loop to select existing partitions and assign filesystems and labels."""
        rprint(f"[bold yellow]Existing Partitions on {self.selected_disk}:[/bold yellow]")

        part_choices = []
        for i, p in enumerate(self.available_partitions, 1):
            name = p.get("name")
            size = p.get("size", "Unknown")
            label = p.get("label") or "no label"
            rprint(f"  [green]{i}[/green]. /dev/{name} (Size: [bold]{size}[/bold], Label: [dim]{label}[/dim])")
            part_choices.append(str(i))

        rprint("\n[dim]Do the thing. (format and select partition type) (enter or 'done' when complete).[/dim]\n")

        while True:
            action = Prompt.ask(
                "Select partition number (enter or 'done' when complete)",
                choices=part_choices + ["done"],
                default="done"
            )

            # Exiting the loop returns flow back to run() -> summary() naturally
            if action == "done":
                break

            selected_part = self.available_partitions[int(action) - 1]
            part_name = f"/dev/{selected_part['name']}"

            # Ask for partition type
            part_type = Prompt.ask(
                f"Select partition type for [bold]{part_name}[/bold]",
                choices=["root", "home", "efi"],
                default="root"
            )

            # Determine default filesystem (efi defaults to fat32, others to ext4)
            default_fs = "fat32" if part_type == "efi" else "ext4"

            # When home is selected, provide option not to reformat
            format_partition = True
            if part_type == "home":
                format_partition = Confirm.ask(f"Do you want to reformat [bold]{part_name}[/bold]?", default=True)

            fs_type = None
            part_label = ""

            if format_partition:
                # Choose filesystem type
                fs_type = Prompt.ask(
                    f"Select filesystem for [bold]{part_name}[/bold]",
                    choices=["ext4", "fat32"],
                    default=default_fs
                )

                # Mandate that the user provides a partition label
                while True:
                    part_label = Prompt.ask(f"Enter a mandatory label for [bold]{part_name}[/bold]")
                    if part_label.strip():
                        break
                    rprint("[red]A label is required. Please enter a valid partition label.[/red]")
            else:
                rprint(f"[yellow]Skipping formatting for {part_name}[/yellow]")

            # Assign mount point based on partition type
            mount_point = {
                "root": "/mnt",
                "home": "/mnt/home",
                "efi": "/mnt/efi"
            }[part_type]

            # Prevent duplicate configuration of the same partition
            self.configured_partitions = [p for p in self.configured_partitions if p["partition"] != part_name]
            self.configured_partitions.append({
                "partition": part_name,
                "type": part_type,
                "fs": fs_type,
                "label": part_label.strip() if format_partition else selected_part.get("label", ""),
                "format": format_partition,
                "mount": mount_point
            })
            rprint(f"[green]✔ Configured {part_name} as {part_type} (Mount: {mount_point})[/green]\n")

    def summary(self) -> None:
        """Displays the configuration summary and executes mkfs safely."""
        if not self.configured_partitions:
            rprint("[bold yellow]No partitions were selected for formatting. This may cause erratic behavior.[/bold yellow]")
            return

        summary_text = f"[bold]Target Disk:[/bold] {self.selected_disk}\n[bold]Formatting Actions:[/bold]\n"
        for p in self.configured_partitions:
            fmt_info = f"Filesystem: [green]{p['fs'].upper()}[/green] | Label: [yellow]{p['label']}[/yellow]" if p["format"] else "[dim]Format Skipped[/dim]"
            summary_text += f"  • Partition: [cyan]{p['partition']}[/cyan] | Type: [magenta]{p['type']}[/magenta] | Mount: [blue]{p['mount']}[/blue] | {fmt_info}\n"

        rprint(Panel(summary_text, title="[bold green]Formatting Summary[/bold green]", expand=False))

        if Confirm.ask("[bold red]Proceed to execute filesystem formatting commands?[/bold red]", default=False):
            rprint("[yellow]Executing formatting commands...[/yellow]")
            for p in self.configured_partitions:
                part = p["partition"]
                fs = p["fs"]
                label = p["label"]
                should_format = p["format"]
                mount_dir = p["mount"]

                if should_format:
                    # fat32 uses -n for label, while ext4/others use -L
                    flag = "-n" if fs == "fat32" else "-L"
                    rprint(f"building: [dim]{label}[/dim]")
                    subprocess.run(["sudo", f"mkfs.{fs}", flag, label, part], check=True)

                rprint(f"mounting {part} to {mount_dir}")
                subprocess.run(["sudo", "mount", "--mkdir", part, mount_dir], check=True)

            rprint("[bold green]Formatting completed successfully![/bold green]")
        else:
            rprint("[bold yellow]Operation cancelled safely. No changes were made.[/bold yellow]")

def main():
    rprint("[blue]Have you partitioned your disk already?[/blue]")
    if not input("(y/n) ") in ("y", "yes"):
        rprint("[red]Script unable to continue: User has not provided partition table.[/red]")
        return

    mgr = DiskManager()
    mgr.run()

    rprint("[bold blue]you have done disk things probably. if not, please press ctrl+c and start over[/bold blue]")

    script_path = pathlib.Path(__file__).parent

    subprocess.run(["bash", str(script_path / "strapper.sh")], check=True)

    with open(str(script_path / "deploy.sh"), "r") as f:
        subprocess.run(["arch-chroot", "/mnt"], stdin=f, check=True)

    desktop_dir = pathlib.Path("/mnt/home/Sprow/Desktop")
    desktop_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(script_path / "post_provision.sh", desktop_dir / "post_provision.sh")

if __name__ == "__main__":
    main()
