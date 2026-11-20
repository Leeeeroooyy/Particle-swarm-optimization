
import csv
import math
import random
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


def sphere(individual):
    return sum(x * x for x in individual)


def rosenbrock(individual):
    return sum(
        100 * (next_x - x * x) ** 2 + (1 - x) ** 2
        for x, next_x in zip(individual, individual[1:])
    )


def schwefel(individual):
    return 418.9828872724338 * len(individual) - sum(
        x * math.sin(math.sqrt(abs(x))) for x in individual
    )


def create_particle(dimension, low, high, vmax):
    position = [random.uniform(low, high) for _ in range(dimension)]
    velocity = [random.uniform(-vmax, vmax) for _ in range(dimension)]
    return position, velocity


def neighbourhood_leaders(personal_best_fitness, topology):
    size = len(personal_best_fitness)

    if topology == "star":
        best = min(range(size), key=lambda i: personal_best_fitness[i])
        return [best] * size

    if topology == "ring":
        return [
            min(((i - 1) % size, i, (i + 1) % size), key=lambda j: personal_best_fitness[j])
            for i in range(size)
        ]

    raise ValueError("Unknown topology")


def inertia_weight(w_start, w_end, evaluations, max_evaluations):
    return w_start - (w_start - w_end) * evaluations / max_evaluations


def update_velocity(position, velocity, personal_best, leader, w, c1, c2, vmax):
    return [
        min(max(w * v + c1 * random.random() * (p - x) + c2 * random.random() * (g - x), -vmax), vmax)
        for x, v, p, g in zip(position, velocity, personal_best, leader)
    ]


def is_inside(position, low, high):
    return all(low <= x <= high for x in position)


def particle_swarm(
    dimension,
    fitness_function,
    low,
    high,
    max_evaluations,
    population_size=40,
    w_start=0.7,
    w_end=0.7,
    c1=1.49618,
    c2=1.49618,
    topology="star",
    vmax_ratio=0.2
):
    if dimension < 1:
        raise ValueError("Dimension is too small")
    if population_size < 3 or population_size > max_evaluations:
        raise ValueError("Invalid population size")
    if not 0 < vmax_ratio <= 1:
        raise ValueError("vmax ratio must be between 0 and 1")

    vmax = vmax_ratio * (high - low)
    positions = []
    velocities = []
    for _ in range(population_size):
        position, velocity = create_particle(dimension, low, high, vmax)
        positions.append(position)
        velocities.append(velocity)

    personal_best = [position.copy() for position in positions]
    personal_best_fitness = []
    convergence = []
    best_fitness = float("inf")
    evaluations = 0
    iterations = 0
    moves = 0
    outside_moves = 0

    for position in positions:
        fitness = fitness_function(position)
        personal_best_fitness.append(fitness)
        evaluations += 1
        best_fitness = min(best_fitness, fitness)
        convergence.append(best_fitness)

    while evaluations < max_evaluations and iterations < max_evaluations:
        iterations += 1
        w = inertia_weight(w_start, w_end, evaluations, max_evaluations)
        leaders = neighbourhood_leaders(personal_best_fitness, topology)

        for i in range(population_size):
            if evaluations >= max_evaluations:
                break

            velocities[i] = update_velocity(
                positions[i], velocities[i], personal_best[i],
                personal_best[leaders[i]], w, c1, c2, vmax
            )
            positions[i] = [x + v for x, v in zip(positions[i], velocities[i])]
            moves += 1

            if not is_inside(positions[i], low, high):
                outside_moves += 1
                continue

            fitness = fitness_function(positions[i])
            evaluations += 1
            best_fitness = min(best_fitness, fitness)
            convergence.append(best_fitness)

            if fitness <= personal_best_fitness[i]:
                personal_best[i] = positions[i].copy()
                personal_best_fitness[i] = fitness

    convergence += [best_fitness] * (max_evaluations - len(convergence))
    return best_fitness, convergence, iterations, outside_moves / moves


def run_experiment(problem_index, problem, dimension, max_evaluations, runs, settings, target):
    problem_name, fitness_function, low, high = problem
    final_results = []
    all_convergences = []
    all_iterations = []
    all_outside_ratios = []
    first_optimum_evaluations = []

    for run in range(runs):
        random.seed(1000 + run + dimension * 10 + problem_index * 100000)
        best, convergence, iterations, outside_ratio = particle_swarm(
            dimension=dimension,
            fitness_function=fitness_function,
            low=low,
            high=high,
            max_evaluations=max_evaluations,
            **settings
        )

        final_results.append(best)
        all_convergences.append(convergence)
        all_iterations.append(iterations)
        all_outside_ratios.append(outside_ratio)
        if best <= target:
            first_optimum_evaluations.append(
                next(i for i, value in enumerate(convergence, start=1) if value <= target)
            )

    convergence_quartiles = [
        statistics.quantiles(values, n=4, method="inclusive")
        for values in zip(*all_convergences)
    ]
    stats = {
        "best": min(final_results),
        "worst": max(final_results),
        "mean": statistics.mean(final_results),
        "median": statistics.median(final_results),
        "std": statistics.stdev(final_results),
        "optimal_runs": len(first_optimum_evaluations),
        "avg_optimum_evaluations": (
            statistics.mean(first_optimum_evaluations)
            if first_optimum_evaluations else None
        ),
        "avg_iterations": statistics.mean(all_iterations),
        "outside_ratio": statistics.mean(all_outside_ratios)
    }
    return stats, convergence_quartiles


def draw_graph(problem_name, dimension, curves, target, output_dir, file_suffix=""):
    plt.figure(figsize=(11, 6))

    for label, quartiles in curves.items():
        evaluations = range(1, len(quartiles) + 1)
        lower, median, upper = zip(*quartiles)
        line, = plt.plot(evaluations, median, label=label)
        plt.fill_between(evaluations, lower, upper, color=line.get_color(), alpha=0.15, linewidth=0)

    plt.axhline(target, linestyle="--", color="gray", linewidth=1, label="Target (1e-8)")
    plt.yscale("log")
    plt.title(f"{problem_name} - Median Convergence - {dimension}D, {len(quartiles)} evaluations (10 runs, 25-75% band)")
    plt.xlabel("Fitness Evaluations")
    plt.ylabel("Best Fitness (median, log scale)")
    plt.legend(fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    file_name = output_dir / f"{problem_name}_{dimension}D{file_suffix}.png"
    plt.savefig(file_name, dpi=150)
    plt.close()
    print(f"Graph saved: {file_name}")


def format_number(value):
    if value == 0 or value >= 0.0001:
        return f"{value:.4f}"
    return f"{value:.3e}"


def run_group(problem_index, problem, dimension, max_evaluations, runs, experiments, base_settings, target):
    problem_name = problem[0]
    print(f"\n{'=' * 110}")
    print(f"{problem_name} - {dimension}D, {runs} runs, {max_evaluations} evaluations per run")
    print(f"{'=' * 110}")
    print(
        f"{'Configuration':<20} {'Best':>11} {'Worst':>11} {'Mean':>11} {'Median':>11} "
        f"{'Std':>11} {'Optimal':>8} {'Iter':>7} {'Out':>6}"
    )

    curves = {}
    group_rows = []

    for label, changes in experiments:
        settings = {**base_settings, **changes}
        stats, convergence_quartiles = run_experiment(
            problem_index, problem, dimension, max_evaluations, runs, settings, target
        )
        curves[label] = convergence_quartiles

        group_rows.append({
            "problem": problem_name,
            "dimension": dimension,
            "max_evaluations": max_evaluations,
            "configuration": label,
            **settings,
            **stats
        })

        values = " ".join(
            f"{format_number(stats[key]):>11}" for key in ("best", "worst", "mean", "median", "std")
        )
        print(
            f"{label:<20} {values} {stats['optimal_runs']:>5}/{runs} "
            f"{stats['avg_iterations']:>7.0f} {stats['outside_ratio']:>6.1%}",
            flush=True
        )

    best = max(
        group_rows,
        key=lambda row: (
            -row["median"], row["optimal_runs"],
            -row["avg_optimum_evaluations"]
            if row["avg_optimum_evaluations"] is not None else float("-inf")
        )
    )
    print(f"Best configuration: {best['configuration']}")
    return group_rows, curves


def main():
    base_settings = {
        "population_size": 40,
        "w_start": 0.7,
        "w_end": 0.7,
        "c1": 1.49618,
        "c2": 1.49618,
        "topology": "star",
        "vmax_ratio": 0.2
    }

    experiments = [
        ("Linear w, star", {"w_start": 0.8, "w_end": 0.3, "c1": 2.0, "c2": 2.0}),
        ("Constant w, star", {}),
        ("Constant w, ring", {"topology": "ring"})
    ]

    problems = [
        ("Sphere", sphere, -5.12, 5.12),
        ("Rosenbrock", rosenbrock, -2.048, 2.048),
        ("Schwefel", schwefel, -500.0, 500.0)
    ]
    dimensions = [10, 30, 100]
    runs = 10
    target = 1e-8
    output_dir = Path(__file__).resolve().parent / "pso_results"
    output_dir.mkdir(exist_ok=True)
    summary_rows = []

    for problem_index, problem in enumerate(problems):
        for dimension in dimensions:
            group_rows, curves = run_group(
                problem_index, problem, dimension, 1000 * dimension,
                runs, experiments, base_settings, target
            )
            summary_rows += group_rows
            draw_graph(problem[0], dimension, curves, target, output_dir)

    control_rows, control_curves = run_group(
        1, problems[1], 10, 10000 * 10,
        runs, experiments, base_settings, target
    )
    summary_rows += control_rows
    draw_graph(problems[1][0], 10, control_curves, target, output_dir, file_suffix="_control")

    csv_file = output_dir / "summary.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nResults saved to: {output_dir}")
    print(f"Summary saved to: {csv_file}")


if __name__ == "__main__":
    main()
