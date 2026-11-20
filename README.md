# Particle Swarm Optimization
**Optimization of Sphere, Rosenbrock and Schwefel Functions**

---

## 1. Objective

The goal of this project is to implement and evaluate three versions of the particle swarm optimization (PSO) algorithm:

- **Linear w, star** - linearly decreasing inertia weight (`w = 0.8 -> 0.3`), `c1 = c2 = 2`, global (star) topology.
- **Constant w, star** - constant inertia weight `w = 0.7`, `c1 = c2 = 1.49618`, global (star) topology.
- **Constant w, ring** - constant inertia weight `w = 0.7`, `c1 = c2 = 1.49618`, ring topology with neighbourhood size 3.

The algorithms are tested on three minimization problems: **Sphere** `[-5.12, 5.12]`, **Rosenbrock** `[-2.048, 2.048]` and **Schwefel** `[-500, 500]`. All of them have an optimal fitness equal to `0`.

## 2. Algorithm Design

Each particle has a position, a velocity and its personal best position.

The algorithm follows these steps:

1. **Initialization** - generate random positions and velocities and evaluate all particles.
2. **Leader selection** - find the best particle of the whole swarm (star) or of the particle and its two neighbours (ring).
3. **Velocity update** - `v = w*v + c1*r1*(pbest - x) + c2*r2*(leader - x)`, where the velocity is limited to `vmax = 0.2 * Range`.
4. **Movement** - move the particle: `x = x + v`.
5. **Evaluation** - evaluate the particle only if it is inside the search space. Particles outside keep flying but are not evaluated.
6. **Replacement** - update the personal best and repeat until the evaluation budget (MAXFES) is exhausted.

The leaders are selected once at the beginning of each iteration, while the personal best of a particle is updated immediately after its evaluation.

In the linear version, the inertia weight decreases according to the number of used evaluations.

## 3. Experimental Setup

Experiments are performed for three dimensions, with **10 independent runs** per configuration.

| Dimension | Fitness Evaluations | Runs |
|:---:|---:|:---:|
| 10D | 10,000 | 10 |
| 30D | 30,000 | 10 |
| 100D | 100,000 | 10 |

### Default Parameters

| Parameter | Value |
|---|---|
| Population size | 40 |
| Maximum velocity | 0.2 * Range |
| Iterations | at least MAXFES / 40 |

### Tested Versions

| Version | Inertia weight | c1 = c2 | Topology |
|---|---|---|---|
| Linear w, star | 0.8 -> 0.3 | 2 | Star |
| Constant w, star | 0.7 | 1.49618 | Star |
| Constant w, ring | 0.7 | 1.49618 | Ring (3) |

## 4. Experimental Results

### 4.1 Performance

The following table shows the median of the final best fitness values obtained across 10 runs. A run is counted as optimal when it reaches `f <= 0.00000001`.

| Problem | Dimension | Linear w, star | Constant w, star | Constant w, ring |
|---|---|---|---|---|
| Sphere | 10D | 3.768e-12 (10/10) | 6.052e-16 (10/10) | 6.958e-09 (9/10) |
| Sphere | 30D | 2.134e-09 (9/10) | 1.611e-16 (10/10) | 9.414e-09 (6/10) |
| Sphere | 100D | 0.0001 (0/10) | 0.0034 (0/10) | 1.171e-08 (2/10) |
| Rosenbrock | 10D | 5.7472 | 4.0089 | 6.1927 |
| Rosenbrock | 30D | 25.7111 | 22.3642 | 25.5977 |
| Rosenbrock | 100D | 96.0194 | 97.7009 | 94.5211 |
| Schwefel | 10D | 730.3765 | 1194.2695 | 1017.0660 |
| Schwefel | 30D | 4036.8360 | 4935.2919 | 4760.6082 |
| Schwefel | 100D | 16761.2237 | 20218.5967 | 19503.6033 |

*Values are rounded to 4 decimal places. Values smaller than 0.0001 are written in scientific notation.*

### 4.2 Best Configurations

The best versions were selected primarily by median fitness, followed by the number of successful runs and convergence speed.

| Problem | Dimension | Best Version | Median Fitness | Optimal Runs |
|---|---|---|---|---|
| Sphere | 10D | Constant w, star | 6.052e-16 | 10/10 |
| Sphere | 30D | Constant w, star | 1.611e-16 | 10/10 |
| Sphere | 100D | Constant w, ring | 1.171e-08 | 2/10 |
| Rosenbrock | 10D | Constant w, star | 4.0089 | 0/10 |
| Rosenbrock | 30D | Constant w, star | 22.3642 | 0/10 |
| Rosenbrock | 100D | Constant w, ring | 94.5211 | 0/10 |
| Schwefel | 10D | Linear w, star | 730.3765 | 0/10 |
| Schwefel | 30D | Linear w, star | 4036.8360 | 0/10 |
| Schwefel | 100D | Linear w, star | 16761.2237 | 0/10 |

### 4.3 Convergence Analysis

The convergence graphs show the **median best-so-far fitness over 10 runs** as a function of the number of fitness evaluations. The coloured area shows the spread between the 25th and 75th percentile and the horizontal dashed line represents the target fitness.

Complete statistics for all configurations are available in [`pso_results/summary.csv`](pso_results/summary.csv).

## 5. Discussion

**Sphere**

All versions found the optimum in 10D and 30D in almost every run, but the constant star version was the fastest. In 100D the star versions did not have enough evaluations: their curves were still going down at the end of the budget. The constant star version improved only in steps with long flat parts, and the linear version was slow at the beginning because of the large inertia. The ring topology converged more steadily and was the only version that reached the target in 100D.

**Rosenbrock**

No version reached the optimum within the evaluation budget. To check whether the budget is the reason, the 10D problem was also run with 100,000 evaluations. The median of the constant star version improved from 4.0089 to 0.0081, but still no run reached the target.

**Schwefel**

All versions got stuck in local minima. The linear version gave the best results in all dimensions, because the larger inertia at the beginning helps the particles explore more of the search space. Its particles also left the search space more often (up to 45.6% of moves in 100D), and since these moves were not evaluated, it made more iterations.

## 6. Conclusion

The experiments demonstrate that all three versions of PSO work and are able to solve the Sphere function, while Rosenbrock and Schwefel were not solved within the evaluation budget.

The constant star version was the best for simpler problems in lower dimensions, the ring topology worked better in 100D, and the linear version was the best on the multimodal Schwefel function.

Overall, the results show that inertia weight and topology influence both convergence speed and solution quality. More evaluations and more independent runs could provide more reliable conclusions.

---

## 7. Convergence Graphs

The following graphs compare the median convergence of all tested versions over 10 runs.

### Sphere

- [Sphere – 10D](pso_results/Sphere_10D.png)
- [Sphere – 30D](pso_results/Sphere_30D.png)
- [Sphere – 100D](pso_results/Sphere_100D.png)

### Rosenbrock

- [Rosenbrock – 10D](pso_results/Rosenbrock_10D.png)
- [Rosenbrock – 30D](pso_results/Rosenbrock_30D.png)
- [Rosenbrock – 100D](pso_results/Rosenbrock_100D.png)
- [Rosenbrock – 10D (100,000 evaluations)](pso_results/Rosenbrock_10D_control.png)

### Schwefel

- [Schwefel – 10D](pso_results/Schwefel_10D.png)
- [Schwefel – 30D](pso_results/Schwefel_30D.png)
- [Schwefel – 100D](pso_results/Schwefel_100D.png)
