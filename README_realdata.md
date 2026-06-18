# ATP Tennis Match Prediction

Source code for predicting ATP tennis match outcomes.

## Run the Code

### Part 1.1: Environment Setup

```bash
conda env create -f environment.yml
```

### Part 2: Full Experiment Pipeline

To run the complete experiment workflow:

```bash
bash run_full_experiment.sh
```

### Part 3: Example Commands for Separate Steps

The commands below show an example run for a single random seed / replication.
#### Feature Groups

- **MI** (17 dim): Match Information
- **PP** (15 dim): Player Profile
- **TS** (34 dim): Time Series Statistics
- **Total**: MI_PP_TS = 66 dimensions

---
#### 3.1 Train Models

```bash
python main_train_realdata.py --feature_name MI_PP_TS_dim66 --sim_id 1 --hidden_dim 16 --hidden_num 3 --bs 32 --lr 0.001 --weight_decay 0.0001

```

Train Deep, Deep_no_u, PL, PlusDC models

we can also use a bash script to train all models across multiple feature sets (and optionally reps/seeds).

```bash
# Single feature groups
bash run_train.sh
```

You can increase training speed by running multiple training jobs in parallel. Edit `run_train.sh` and increase `CONCURRENT` to the number of processes you want to run at the same time. A larger value can finish the grid search faster, but it will also use more CPU resources.

```bash
# Number of concurrent processes
CONCURRENT=1
```

---

#### 3.3 Calculate Optimal Metrics

Example with one replication:

```bash
python main_optimal_metrics.py --rep_start 1 --rep_end 1
```

#### Evaluation Metrics

- Likelihood (train/test/val)
- Win Rate (train/test/val)
- Brier Score (train/test/val)

Evaluates performance and outputs `metrics_summary.json`, `metrics_summary.csv`, `accumulate_dim.png`

---

#### 3.4 Visualize Results

Example visualization for one replication:

```bash
python fig6_radar_plot_enhanced.py --style style2
python fig7_visualize_single_model.py --feature_name MI_PP_TS_dim66 --model_type Deep --rep_id 1 --num_reps 1
```

Generates trajectories plots and radar charts

---
