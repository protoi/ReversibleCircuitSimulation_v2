from circuit_generator import Circuit

# gateConfig = [{"target": "0b01000", "controls": "0b10101"}, {"target": "0b10000", "controls": "0b00100"},
#               {"target": "0b00100", "controls": "0b01011"}, {"target": "0b00001", "controls": "0b01000"},
#               {"target": "0b00100", "controls": "0b00001"}, {"target": "0b00001", "controls": "0b10100"}]

gateConfig = [{"target": "0b00100", "controls": "0b00001"}, {"target": "0b00001", "controls": "0b10100"}]

fixedGateConfig = [{"target": int(x["target"], 2), "controls": int(x["controls"], 2)} for x in gateConfig]
# g = Gate(0b0000001, 0b1100110, 3)

c = Circuit(5)
c.circuit_maker(fixedGateConfig)

c.explore_pmgf()
