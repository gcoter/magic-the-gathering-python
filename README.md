# magic-the-gathering-python
A Python implementation of Magic The Gathering.

## Requirements
It must fulfill the following requirements:
- [x] It must be easy to implement a new AI (by subclassing)
- [x] It should be able to simulate thousands games between two AIs
- [ ] It should have a GUI in order for one human to play against an AI
- [x] The game state must be easy to save and recover (so that datasets of simulated plays can be created)
- [ ] An AI must be able to simulate a tree of possible upcoming actions (this is necessary for planning and finding the best action)
- [ ] Cards should be easy to import from public databases (such as https://mtgjson.com/downloads/all-files/)
- [ ] It must be easy to filter cards to create decks with given constraints

## Experiments
One of the main goals of this project is to implement Machine Learning based AIs for Magic The Gathering. We have been running experiments, trying different models and strategies. You can see the latest results [here](docs/experiments.md).
