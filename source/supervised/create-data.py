import subprocess
import os
import time
import h5py  # For storing trajectories
from civrealm import parse_freeciv_log  # Assuming you implement this parser


def run_freeciv_game(game_id, num_players=2, ai_level="hard", map_size="small"):
    """Run a headless FreeCiv game and harvest logs."""
    log_dir = f"logs/game_{game_id}"
    os.makedirs(log_dir, exist_ok=True)

    # Start server
    server_cmd = [
        "freeciv-server",
        "--file",
        "civ2civ3",  # Ruleset
        "-p",
        "5556",  # Port
        "-s",
        f"{log_dir}/save",  # Save dir
        "-l",
        f"{log_dir}/server.log",  # Log file
        "--Newusers",  # Allow AI connections
        f"--ai={ai_level}",  # Set AI level
        f"--size={map_size}",  # Map size
        f"--players={num_players}",  # Num players
    ]
    server_proc = subprocess.Popen(server_cmd)
    time.sleep(5)  # Wait for server start

    # Connect AI clients (built-in AI auto-plays)
    clients = []
    for i in range(num_players):
        client_cmd = [
            "freeciv-server",  # Client connects to server
            "-a",  # Autoconnect
            "-P",
            "5556",  # Port
            "-l",
            f"{log_dir}/client_{i}.log",
        ]
        clients.append(subprocess.Popen(client_cmd))

    # Wait for game to finish (poll logs or set timeout)
    while not game_ended(log_dir):  # Implement checker
        time.sleep(60)

    # Kill processes
    server_proc.terminate()
    for c in clients:
        c.terminate()

    # Parse logs into state-action pairs
    trajectories = parse_freeciv_log(
        log_dir
    )  # You need to write this: extract turns, states (e.g., map, units), actions (e.g., move, build)
    save_trajectories(trajectories, f"data/game_{game_id}.h5")


def save_trajectories(trajs, file_path):
    with h5py.File(file_path, "w") as f:
        for i, traj in enumerate(trajs):
            grp = f.create_group(f"traj_{i}")
            grp.create_dataset("states", data=traj["states"])
            grp.create_dataset("actions", data=traj["actions"])
            grp.create_dataset("rewards", data=traj["rewards"])  # If logged


# Run 100 games
for gid in range(100):
    run_freeciv_game(gid)
