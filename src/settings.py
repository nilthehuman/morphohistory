"""Global settings controlling GUI appearance and simulation behavior."""

#TODO: use observer pattern to spread changes

from enum import Enum

class _Settings:
    """A plain struct holding all relevant constants and parameters."""

    class DistanceMetric(Enum):
        CONSTANT = 1
        MANHATTAN = 2
        EUCLIDEAN = 3

    def __init__(self):
        self.color_A = (1.0, 1.0, 0.0)
        self.color_B = (1.0, 0.0, 1.0)
        self.color_broadcaster = (0.2, 0.9, 0.1)
        self.color_arrow_tip = (0.2, 0.0, 0.8)
        self.arrow_width = 2
        self.grid_color = (0.2, 0.2, 0.2)
        self.grid_resolution = 10

        self.speakerdot_size = (20, 20)
        self.popup_size_load = (400, 430)
        self.popup_size_fail = (250, 200)
        self.popup_size_progress = (500, 250)

        self.bias_threshold = 0.9
        self.experience_start = 1
        self.experience_threshold = 10

        self.sim_distance_metric = self.DistanceMetric.EUCLIDEAN
        self.sim_influence_self = False
        self.sim_batch_size = 100
        self.sim_max_iteration = 10000

SETTINGS = _Settings()
