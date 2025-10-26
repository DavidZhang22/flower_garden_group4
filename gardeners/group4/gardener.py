from core.garden import Garden
from core.gardener import Gardener
from core.micronutrients import Micronutrient
from core.plants.plant_variety import PlantVariety
from core.plants.species import Species


class Gardener4(Gardener):
    def __init__(self, garden: Garden, varieties: list[PlantVariety]):
        super().__init__(garden, varieties)
        self.r_plants: list[PlantVariety] = []
        self.b_plants: list[PlantVariety] = []
        self.g_plants: list[PlantVariety] = []
        self.group()

    def cultivate_garden(self) -> None:
        # use garden.add_plant(...) to add plants to the garden
        pass

    # creates clusters of points where each cluster should promote growth (not where to place them)
    def total_growth_clusters(self) -> list[list[PlantVariety]]:
        # use garden.add_plant(...) to add plants to the garden
        self.sort_species_delta_radii()
        # find limiting plant of the three top options - the one that consumes the most
        clusters: list[list[PlantVariety]] = []
        curr_cluster: list[PlantVariety] = []

        curr_red = 0
        curr_blue = 0
        curr_green = 0

        while (len(self.r_plants) > 0 or len(self.b_plants) > 0 or len(self.g_plants) > 0):
            # create a growing cluster
            if curr_red > 0 and curr_blue > 0 and curr_green > 0:
                clusters.append(curr_cluster)
                curr_red = 0
                curr_blue = 0
                curr_green = 0
                continue
            if (curr_red <= 0 and len(self.r_plants) <= 0) or (curr_green <= 0 and len(self.g_plants) <= 0) or (curr_blue <= 0 and len(self.b_plants) <= 0):
                # can no longer cluster any more plants without detrimenting the bad current cluster
                return clusters
        
        # not clusters - instead put it back in the list -->
        if len(self.r_plants) == 0 or len(self.b_plants) == 0 or len(self.g_plants) == 0:
            # not enough plants
            return []
        plant_placement_order = []
        while len(plant_placement_order) < len(self.varieties):
            if len(self.r_plants) == 0:
                plant_placement_order += self.b_plants + self.g_plants
            elif len(self.b_plants) == 0:
                plant_placement_order += self.r_plants + self.g_plants
            elif len(self.g_plants) == 0:
                plant_placement_order += self.r_plants + self.b_plants
            else:
                #alternate 3 in a row? But only possible
                r = self.r_plants[-1]
                b = self.b_plants[-1]
                g = self.g_plants[-1]
                p = self.max_cost_plant(r, g, b)
                plant_placement_order.append(p)
                #p_species = max(p.nutrient_coefficients, key=p.nutrient_coefficients.get)
                min_coefficient = min(p.nutrient_coefficients, key=p.nutrient_coefficients.get)
                if min_coefficient == Species.RHODODENDRON:
                    r_amt = p.nutrient_coefficients[r]
                if min_coefficient == Species.BEGONIA:
                    b_amt = p.nutrient_coefficients[b]
                if min_coefficient == Species.GERANIUM:
                    g_amt = p.nutrient_coefficients[g]
                # pop from the right list

        return plant_placement_order

    def max_cost_plant(self, r, g, b) -> PlantVariety:
        r_cost = r.nutrient_coefficients[Micronutrient.B] + r.nutrient_coefficients[Micronutrient.G]
        b_cost = b.nutrient_coefficients[Micronutrient.R] + b.nutrient_coefficients[Micronutrient.G]
        g_cost = g.nutrient_coefficients[Micronutrient.B] + g.nutrient_coefficients[Micronutrient.R]
        if r_cost <= b_cost and r_cost <= g_cost:
            return r
        if b_cost <= r_cost and b_cost <= g_cost:
            return b
        else:
            return g

    # split into three species types at least - sorted - pick the top one
    # do we want to also split into radii/area - like class --> always choose radius 1 plants first, or no
    # i.e. geometry considerations? pack everything together?
    # obviously smaller objects are better usually, but they may not produce as much
    def group_species(self):
        self.r_plants = list(filter(lambda variety: variety.species == Species.RHODODENDRON, self.varieties))
        self.b_plants = list(filter(lambda variety: variety.species == Species.BEGONIA, self.varieties))
        self.g_plants = list(filter(lambda variety: variety.species == Species.GERANIUM, self.varieties))

    def sort_species_delta_radii(self):
        # we want largest deltas for small radii for all 3
        self.r_plants.sort(key = lambda plant: (sum(plant.nutrient_coefficients.values())/plant.radius))
        self.b_plants.sort(key = lambda plant: (sum(plant.nutrient_coefficients.values())/plant.radius))
        self.g_plants.sort(key = lambda plant: (sum(plant.nutrient_coefficients.values())/plant.radius))
    
    # other metrics?
    def sort_species_none_left_behind(self):
        return
    
    def sort_species_fastest(self):
        return
    