import os
import random

class EliminationReasons:
    def __init__(self, file_path='system/elimination_reasons.txt'):
        self.file_path = file_path
        self.reasons = self.load_reasons()

    def load_reasons(self):
        """Load elimination reasons from a text file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                reasons = file.readlines()
            return [reason.strip() for reason in reasons]  # Remove newline characters
        return []  # Return an empty list if the file doesn't exist

    def get_random_reason(self, winner, loser):
        """Get a random elimination reason."""
        if self.reasons:
            reason_template = random.choice(self.reasons)
            return reason_template.format(winner=winner.mention, loser=loser.mention)
       
        return f"{winner.mention} eliminated {loser.mention} in an unknown way!" # RETURNING THIS DIRECTLY 
