from __future__ import annotations

import argparse

import abmforge


def main() -> None:
    parser = argparse.ArgumentParser(prog="abmforge")
    parser.add_argument("command", nargs="?", choices=["info"], help="Command to run")
    parser.add_argument("--version", action="store_true", help="Show package version")
    args = parser.parse_args()

    if args.version:
        print(abmforge.__version__)
        return

    if args.command == "info":
        print(f"ABMForge {abmforge.__version__}")
        print("Core objects: Model, Agent, AgentCollection, GridWorld, Scenario")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
