"""
Cradle-to-gate LCA metric calculator.
Net CO2 equivalent per functional unit, scaled to integer for
uint32 smart contract storage.
PROPOSED ARCHITECTURE — not deployed.
"""


def calculate_cradle_to_gate_lca(verified_acreage_acres: float,
                                 raw_biomass_mass_kg: float,
                                 base_lca_factor: float = 1.25) -> int:
    """
    Calculates the net CO2 equivalent sequestered or emitted per functional unit
    based on verified acreage and delivered biomass mass, scaled to an integer
    for smart contract parameter storage (e.g., multiplied by 1000 for precision).
    """
    # Example formula: Biomass mass weighted against acreage efficiency and LCA multiplier
    if verified_acreage_acres <= 0:
        return 0

    biomass_per_acre = raw_biomass_mass_kg / verified_acreage_acres
    net_lca_metric = biomass_per_acre * base_lca_factor

    # Scale to integer representation (e.g., 3 decimal places precision) for uint32 contract storage
    return int(round(net_lca_metric * 1000))
