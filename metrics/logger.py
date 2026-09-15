import csv
import os


class EpisodeLogger:
    def __init__(self, filename="episode_metrics.csv"):

        self.filename = filename

        # Create file with headers if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, mode="w", newline="") as file:
                writer = csv.writer(file)

                writer.writerow(["episode", "success", "steps", "total_distance", "targets_collected"])

    def log_episode(self, episode, success, steps, total_distance, targets_collected):

        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([episode, success, steps, total_distance, targets_collected])
