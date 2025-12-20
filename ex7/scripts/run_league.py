#!/usr/bin/env python3
"""
League Orchestrator - Start all agents and run a complete league.

This script:
1. Starts the League Manager
2. Starts the Referee
3. Starts multiple Player agents
4. Creates the schedule
5. Runs all matches
6. Displays final standings
"""

import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path

import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from SHARED.league_sdk.http_client import MCPClient


class LeagueOrchestrator:
    """Orchestrates the entire league."""

    def __init__(
        self,
        num_players: int = 4,
        league_manager_port: int = 8000,
        referee_port: int = 8001,
        player_base_port: int = 8101,
    ):
        """Initialize orchestrator."""
        self.num_players = num_players
        self.league_manager_port = league_manager_port
        self.referee_port = referee_port
        self.player_base_port = player_base_port

        self.processes: list[subprocess.Popen] = []
        self.client = MCPClient()

        # Endpoints
        self.league_endpoint = f"http://localhost:{league_manager_port}"
        self.referee_endpoint = f"http://localhost:{referee_port}"

    def start_league_manager(self) -> bool:
        """Start the league manager."""
        print("\n[1/4] Starting League Manager...")

        cmd = [
            sys.executable, "-m", "agents.league_manager.main",
            "--port", str(self.league_manager_port),
        ]

        process = subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).parent.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.processes.append(process)

        # Wait for server to be ready
        return self._wait_for_server(f"{self.league_endpoint}/health", "League Manager")

    def start_referee(self) -> bool:
        """Start the referee."""
        print("[2/4] Starting Referee...")

        cmd = [
            sys.executable, "-m", "agents.referee.main",
            "--port", str(self.referee_port),
            "--league-endpoint", f"{self.league_endpoint}/mcp",
        ]

        process = subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).parent.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.processes.append(process)

        return self._wait_for_server(f"{self.referee_endpoint}/health", "Referee")

    def start_players(self) -> bool:
        """Start all player agents."""
        print(f"[3/4] Starting {self.num_players} Players...")

        player_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"]

        for i in range(self.num_players):
            port = self.player_base_port + i
            name = player_names[i] if i < len(player_names) else f"Player{i+1}"

            cmd = [
                sys.executable, "-m", "agents.player.main",
                "--port", str(port),
                "--league-endpoint", f"{self.league_endpoint}/mcp",
                "--display-name", f"Agent {name}",
                "--strategy", "random",
            ]

            process = subprocess.Popen(
                cmd,
                cwd=str(Path(__file__).parent.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.processes.append(process)

            if not self._wait_for_server(f"http://localhost:{port}/health", f"Player {name}"):
                return False

        return True

    def create_schedule(self) -> list:
        """Create the tournament schedule."""
        print("[4/4] Creating schedule...")

        response = requests.post(f"{self.league_endpoint}/create_schedule")
        data = response.json()

        schedule = data.get("schedule", [])
        print(f"      Created schedule with {len(schedule)} matches")

        return schedule

    def run_matches(self, schedule: list) -> None:
        """Run all matches in the schedule."""
        print("\n" + "=" * 60)
        print("RUNNING MATCHES")
        print("=" * 60)

        # Get player endpoints
        status = requests.get(f"{self.league_endpoint}/status").json()
        standings_response = requests.get(f"{self.league_endpoint}/standings").json()

        for i, match in enumerate(schedule, 1):
            match_id = match["match_id"]
            player_a_id = match["player_A_id"]
            player_b_id = match["player_B_id"]
            round_id = match["round_id"]

            # Derive ports from player IDs
            player_a_port = self.player_base_port + int(player_a_id[1:]) - 1
            player_b_port = self.player_base_port + int(player_b_id[1:]) - 1

            print(f"\nMatch {i}/{len(schedule)}: {match_id}")
            print(f"  {player_a_id} vs {player_b_id}")

            # Run match via referee
            try:
                result = requests.post(
                    f"{self.referee_endpoint}/run_match",
                    json={
                        "match_id": match_id,
                        "round_id": round_id,
                        "player_a_id": player_a_id,
                        "player_b_id": player_b_id,
                        "player_a_endpoint": f"http://localhost:{player_a_port}/mcp",
                        "player_b_endpoint": f"http://localhost:{player_b_port}/mcp",
                    },
                    timeout=60,
                )
                data = result.json()

                winner = data.get("winner")
                game_result = data.get("result", {})

                if winner:
                    print(f"  Winner: {winner}")
                else:
                    print(f"  Draw!")

                if game_result:
                    print(f"  Number: {game_result.get('drawn_number')} ({game_result.get('number_parity')})")
                    choices = game_result.get("choices", {})
                    for pid, choice in choices.items():
                        print(f"    {pid} chose: {choice}")

            except Exception as e:
                print(f"  ERROR: {e}")

            # Small delay between matches
            time.sleep(0.5)

    def show_standings(self) -> None:
        """Display final standings."""
        print("\n" + "=" * 60)
        print("FINAL STANDINGS")
        print("=" * 60)

        response = requests.get(f"{self.league_endpoint}/standings")
        data = response.json()
        standings = data.get("standings", [])

        print(f"\n{'Rank':<6}{'Player':<20}{'Played':<8}{'W':<4}{'D':<4}{'L':<4}{'Points':<8}")
        print("-" * 54)

        for s in standings:
            print(
                f"{s['rank']:<6}"
                f"{s['display_name']:<20}"
                f"{s['played']:<8}"
                f"{s['wins']:<4}"
                f"{s['draws']:<4}"
                f"{s['losses']:<4}"
                f"{s['points']:<8}"
            )

        if standings:
            champion = standings[0]
            print(f"\n{'=' * 54}")
            print(f"CHAMPION: {champion['display_name']} with {champion['points']} points!")
            print(f"{'=' * 54}")

    def cleanup(self) -> None:
        """Stop all processes."""
        print("\nStopping all agents...")

        for process in self.processes:
            process.terminate()

        for process in self.processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        print("All agents stopped.")

    def _wait_for_server(self, url: str, name: str, timeout: int = 30) -> bool:
        """Wait for a server to become ready."""
        start = time.time()

        while time.time() - start < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"      {name} is ready")
                    return True
            except requests.RequestException:
                pass
            time.sleep(0.5)

        print(f"      ERROR: {name} failed to start")
        return False

    def run(self) -> None:
        """Run the complete league."""
        try:
            print("=" * 60)
            print("AI AGENT LEAGUE - EVEN/ODD TOURNAMENT")
            print("=" * 60)

            # Start all components
            if not self.start_league_manager():
                return

            if not self.start_referee():
                return

            if not self.start_players():
                return

            # Wait for all registrations
            time.sleep(3)

            # Create schedule
            schedule = self.create_schedule()

            if not schedule:
                print("ERROR: No schedule created")
                return

            # Run matches
            self.run_matches(schedule)

            # Show final standings
            self.show_standings()

        finally:
            self.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run AI Agent League")
    parser.add_argument(
        "--players",
        type=int,
        default=4,
        help="Number of players (default: 4)",
    )
    parser.add_argument(
        "--league-port",
        type=int,
        default=8000,
        help="League manager port (default: 8000)",
    )
    parser.add_argument(
        "--referee-port",
        type=int,
        default=8001,
        help="Referee port (default: 8001)",
    )
    parser.add_argument(
        "--player-base-port",
        type=int,
        default=8101,
        help="Base port for players (default: 8101)",
    )
    args = parser.parse_args()

    orchestrator = LeagueOrchestrator(
        num_players=args.players,
        league_manager_port=args.league_port,
        referee_port=args.referee_port,
        player_base_port=args.player_base_port,
    )

    orchestrator.run()


if __name__ == "__main__":
    main()
