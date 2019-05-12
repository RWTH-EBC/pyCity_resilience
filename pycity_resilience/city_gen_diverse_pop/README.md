## city_gen_diverse_pop

Holding scripts to generate diverse start population for GA execution.
Therefore, it:
- Loads city object with or without energy systems 
(existing energy systems will be overwritten)
- Loops over different energy system scenarios and 
estimates the dimensions of each energy system.
- Parses city data to each individuum dict (ind).
- Saves sum of individuums as pickled population file 