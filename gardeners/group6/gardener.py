"""
Group 6 Gardener: Force-directed layout with nutrient-aware optimization.

Strategy:
1. Random seed initial positions
2. Force layout (feasibility): Remove overlaps
3. Force layout (nutrient): Pull cross-species plants into interaction range
4. Multi-start: Try multiple seeds, pick best by simple graph score
"""

import numpy as np
from core.garden import Garden
from core.gardener import Gardener
from core.plants.plant_variety import PlantVariety
from core.point import Position

from gardeners.group6.force_layout import (
    scatter_seeds,
    separate_overlapping_plants,
    create_beneficial_interactions,
    measure_garden_quality
)


class Gardener6(Gardener):
    def __init__(self, garden: Garden, varieties: list[PlantVariety]):
        super().__init__(garden, varieties)
        
        # Configuration parameters
        self.num_seeds = 12  # Multi-start attempts
        self.feasible_iters = 300
        self.nutrient_iters = 200
        self.band_delta = 0.25
        self.degree_cap = 4
        self.top_k_simulate = 1  # For MVP, just use best by graph score
    
    def cultivate_garden(self) -> None:
        """
        Main cultivation method: place plants optimally in the garden.
        
        MVP Pipeline:
        1. Generate random seed positions
        2. Apply feasibility forces (remove overlaps)
        3. Apply nutrient forces (create beneficial interactions)
        4. Place plants in garden
        """
        if not self.varieties:
            return
        
        best_score = -float('inf')
        best_layout = None
        best_labels = None
        
        # Multi-start: try multiple random seeds
        for seed_idx in range(self.num_seeds):
            # Step 1: Scatter seeds randomly
            X, labels, inv = scatter_seeds(
                self.varieties,
                W=self.garden.width,
                H=self.garden.height
            )
            
            # Step 2: Separate overlapping plants
            X = separate_overlapping_plants(
                X,
                self.varieties,
                labels,
                iters=self.feasible_iters
            )
            
            # Step 3: Create beneficial interactions
            X = create_beneficial_interactions(
                X,
                self.varieties,
                labels,
                inv,
                iters=self.nutrient_iters,
                band_delta=self.band_delta,
                degree_cap=self.degree_cap
            )
            
            # Step 4: Measure garden quality
            score = measure_garden_quality(X, self.varieties, labels)
            
            # Keep best
            if score > best_score:
                best_score = score
                best_layout = X.copy()
                best_labels = labels.copy()
        
        # Place the best layout in the garden
        if best_layout is not None:
            self._place_plants(best_layout, best_labels)
    
    def _place_plants(self, X: np.ndarray, labels: list[int]) -> None:
        """
        Place plants from layout into the garden.
        
        Args:
            X: N×2 array of positions
            labels: List mapping plant index to variety index
        """
        for i, label in enumerate(labels):
            variety = self.varieties[label]
            position = Position(x=float(X[i, 0]), y=float(X[i, 1]))
            
            # Attempt to place plant
            plant = self.garden.add_plant(variety, position)
            
            # Note: garden.add_plant returns None if placement fails
            # In MVP, we trust our force layout to produce valid positions
            if plant is None:
                # Optional: log or handle failed placements
                pass
