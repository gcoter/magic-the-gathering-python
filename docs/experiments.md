# Experiments
## Technical considerations for reproducibility
This project uses [DVC](https://dvc.org/) for data versioning and [MLflow](https://mlflow.org/) for experiment tracking.

If you want to download the data corresponding to these experiments, run:
```bash
dvc pull -aT
```

In particular, `dvc pull` should retrieve the `mlruns/` folder. You can then open MLflow like this:
```bash
mlflow ui
```

In the results, the git commit hashes and the MLflow experiment names are always given for reference.

## 2023-07-01
### Description
#### Objectives
The main goal of these experiments is to develop an AI player to play Magic The Gathering using Machine Learning. In order to find the best model, it is necessary to try different strategies, architectures and model configurations.

As a first baseline result, we evaluate an AI in comparison to a random player (which always chooses one action randomly among the legal actions).

#### What is the experimental design?
This project implements a DVC pipeline to make it easier to train and evaluate Machine Learning model. The pipeline looks like this (output of `dvc dag`):
```
        +--------------+           
        | collect_data |           
        +--------------+           
                *                  
                *                  
                *                  
  +----------------------------+   
  | train_deep_learning_scorer |   
  +----------------------------+   
                *                  
                *                  
                *                  
+-------------------------------+  
| evaluate_deep_learning_player |  
+-------------------------------+  
```

Here is a description of each stage:
1. **collect_data**: This stage simulates N games between two random players and save the game logs as a pickle (`data/game_logs_dataset.pickle`)
2. **train_deep_learning_scorer**: This stage applies a train/validation split on the game logs data, trains a "scorer" and saves the best checkpoint (according the the validation loss) at `results/models/deep_learning_scorer.ckpt`
3. **evaluate_deep_learning_player**: This stage simulates N games between a random player and an AI which uses the trained scorer, the win rate is saved and used as an evaluation metric

#### What is a "scorer" and how does the player AI work?
In Magic The Gathering, a player needs regularly to choose which action it wants to play. A naive strategy consists in choosing one action at random among the legal actions, this is what we call a random player.

In order to implement a more intelligent player, it is necessary to gain the ability to evaluate actions in the context of a given game state. The module which is responsible for this is called a "scorer".

A scorer receives the current game state and a set of possible actions, then it assigns a score to each possible action. The AI player can then choose which action to play based on these scores.

There are different strategies to choose actions based on scores, currently only one is implemented:
- `SampleActionFromScoresPlayer`: it interprets the scores as a probability distribution and samples the action to choose accordingly to the score distribution

There are also different architectures of scorer:
- `SingleActionScorerV1`: a quite complex architecture which relies on MLP and Transformer Encoders to process the current game state and one action at a time
- `SingleActionScorerV2`: a simpler architecture that is composed of 2 Transformer Encoders, one for the game state and one for the action to evaluate, and a classification MLP

#### What is the training objective?
In order to train a scorer, we need to define an objective. Here is how we do it currently.

The game logs dataset records all the tuples (game_state, chosen_action) from the point of view of each player. That means that for each game we can identify the tuples which correspond to Player 0's decisions and similarly for Player 1. At the end of each game, the winner's player index is recorded.

We define a label like this:
- 0 for all tuples (game_state, chosen_action) which belong to the loser
- 1 for all tuples (game_state, chosen_action) which belong to the winner

This label is what the scorers tries to predict.

We make the assumption that if we are given enough data, this label could be a good proxy to differentiate "good actions" from "bad actions". For instance, it is expected that declaring attackers would be evaluated as rather "good" since winners need to do this in order to decrease their opponent life points.

### Results
#### Dataset
Here are some information regarding the game logs dataset which is created in the first state of the pipeline:

| Git commit Hash | Number of games for data collection | Number of games for evaluation | Player Class 0 | Player Class 1 | Total number of instances | Training Proportion | Validation Proportion |
| ----------------| ----------------------------------- | ------------------------------ | -------------- | -------------- | ------------------------- | ------------------- | --------------------- |
| b65b4134        | 1,000                               | 1,000                          | RandomPlayer   | RandomPlayer   | 268,388                   | 80%                 | 20%                   |

#### Summary Table
Several experiments were run using the same dataset as input:

| Git commit Hash | MLflow experiment name | Player Class                 | Scorer Model Class   | Number of parameters | transformer_n_layers | transformer_n_heads | Win Rate against a random player |
| --------------- | -----------------------| ---------------------------- | -------------------- | -------------------- | -------------------- | ------------------- | -------------------------------- |
| 5aa07cac        | invincible-loon-124    | SampleActionFromScoresPlayer | SingleActionScorerV1 | ~29,000              | NA                   | NA                  | 51.5%                            |
| 4928af16        | stately-roo-854        | SampleActionFromScoresPlayer | SingleActionScorerV2 | 141,825              | 2                    | 4                   | 50.1%                |
| 0a1f0c67        | able-cub-192           | SampleActionFromScoresPlayer | SingleActionScorerV2 | 141,825              | 2                    | 8                   | 51.3%                |
| b031673e        | stylish-lynx-414       | SampleActionFromScoresPlayer | SingleActionScorerV2 | 275,713              | 4                    | 8                   | 51.7%                |

#### Training Loss Comparison
![](img/2023-07-01-18-48-18.png)

#### Validation Loss Comparison
![](img/2023-07-01-18-49-52.png)

### Analysis of the results
For now, our results show that it is challenging to create an AI that plays significantly better than a random player. However we can note several things:
- `SingleActionScorerV2` provides a good basis for future experiments as it looks more stable than `SingleActionScorerV1`
- The win rate evolves accordingly to the complexity of the scorer, although the effect is small. At least, it becomes easier to predict how well an AI will perform based on its scorer configuration

#### Possible improvements
The current scorers don't take into consideration the past and the future. They only consider the current game state.

It would be quite easy to extend the architecture of `SingleActionScorerV2` in order to receive the action history as input. That way, the scorer would have more context to choose the next action based on the past.

Some features could be added as well. For instance, currently the scorer doesn't "know" what is the current phase in the game.

We could also change the way actions are sampled by the player, for instance always choosing the action with the highest score.

Finally, a new player class could be developed to implement a form of "Monte Carlo Tree Seach" in order to take into account the possible consequences of each action. This would require some additionnal development as the player should be able to simulate games starting from its current situation.

#### Possible biases and broken rules
The project is still not mature and some rules of Magic The Gathering are still to be developed:
- The players' hand size is not limited as it should be, that means that players can have a lot of cards in their hand (tracked by issue https://github.com/gcoter/magic-the-gathering-python/issues/46)
- The scorer receives the full game state as input (apart from the libraries), it means that in particular the current player can "see" its opponent's hand which is not permitted by the rules of Magic The Gathering (tracked by issue https://github.com/gcoter/magic-the-gathering-python/issues/49)
