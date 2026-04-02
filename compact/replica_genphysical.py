import csv
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


SEED = 42
random.seed(SEED)


@dataclass
class Sample:
    theta: Tuple[float, float, float]
    temp: List[float]
    y_clean: List[float]


def office_profile(hour: int) -> float:
    if hour < 7 or hour > 20:
        return 0.1
    if 9 <= hour <= 17:
        return 1.0
    return 0.45


def make_temp_profile(day_index: int) -> List[float]:
    phase = day_index * 0.07
    profile = []
    for h in range(24):
        daily_wave = 8.0 * math.sin((2.0 * math.pi * (h - 7)) / 24.0 + phase)
        temp = 20.0 + daily_wave + random.gauss(0.0, 0.7)
        profile.append(temp)
    return profile


def forward_model(theta: Tuple[float, float, float], temp: Sequence[float]) -> List[float]:
    occ_scale, light_scale, plug_scale = theta
    electricity = []
    gas = []
    for h, t in enumerate(temp):
        prof = office_profile(h)
        cooling_kw = max(0.0, t - 24.0) * (1.8 + 0.3 * occ_scale)
        heating_kw = max(0.0, 18.0 - t) * (1.3 + 0.2 * occ_scale)
        internal_load = prof * (
            10.0 * occ_scale
            + 7.0 * light_scale
            + 6.0 * plug_scale
        )
        elec = 13.0 + internal_load + cooling_kw + random.gauss(0.0, 0.15)
        gas_kw = 2.5 + heating_kw * (0.8 + 0.2 * light_scale) + random.gauss(0.0, 0.08)
        electricity.append(max(elec, 0.1))
        gas.append(max(gas_kw, 0.05))
    return electricity + gas


def sample_theta() -> Tuple[float, float, float]:
    return (
        random.uniform(0.55, 1.45),
        random.uniform(0.60, 1.40),
        random.uniform(0.60, 1.40),
    )


def generate_dataset(n: int) -> List[Sample]:
    rows = []
    for i in range(n):
        th = sample_theta()
        temp = make_temp_profile(i)
        y = forward_model(th, temp)
        rows.append(Sample(theta=th, temp=temp, y_clean=y))
    return rows


def standardize_matrix(rows: List[List[float]]) -> Tuple[List[List[float]], List[float], List[float]]:
    n_feat = len(rows[0])
    means = []
    stds = []
    for j in range(n_feat):
        col = [r[j] for r in rows]
        m = statistics.fmean(col)
        s = statistics.pstdev(col)
        if s < 1e-8:
            s = 1.0
        means.append(m)
        stds.append(s)
    z = [[(r[j] - means[j]) / stds[j] for j in range(n_feat)] for r in rows]
    return z, means, stds


def apply_norm(vec: Sequence[float], means: Sequence[float], stds: Sequence[float]) -> List[float]:
    return [(vec[j] - means[j]) / stds[j] for j in range(len(vec))]


def add_noise(vec: Sequence[float], factor: float = 0.10) -> List[float]:
    out = []
    for v in vec:
        sigma = max(1e-4, abs(v) * factor)
        out.append(v + random.gauss(0.0, sigma))
    return out


def add_noise_and_missing(vec: Sequence[float], factor: float = 0.10, miss_ratio: float = 0.35) -> List[float]:
    noisy = add_noise(vec, factor=factor)
    n = len(noisy)
    m = max(1, int(n * miss_ratio))
    idx = list(range(n))
    random.shuffle(idx)
    miss_idx = set(idx[:m])
    observed = [noisy[i] for i in range(n) if i not in miss_idx]
    fill = statistics.fmean(observed) if observed else 0.0
    return [fill if i in miss_idx else noisy[i] for i in range(n)]


def build_training_pool(train_rows: List[Sample]) -> Dict[str, List]:
    x_clean = [r.y_clean for r in train_rows]
    th = [list(r.theta) for r in train_rows]

    x_noisy = [add_noise(r.y_clean, factor=0.10) for r in train_rows]
    x_noisy_missing = [add_noise_and_missing(r.y_clean, factor=0.10, miss_ratio=0.35) for r in train_rows]

    x_all = x_clean + x_noisy + x_noisy_missing
    th_all = th + th + th

    z_all, means, stds = standardize_matrix(x_all)
    return {
        "x_raw": x_all,
        "x_z": z_all,
        "theta": th_all,
        "mean": means,
        "std": stds,
    }


def sq_dist(a: Sequence[float], b: Sequence[float]) -> float:
    return sum((x - y) * (x - y) for x, y in zip(a, b))


def estimate_posterior_samples(
    obs_vec: Sequence[float],
    pool_z: Sequence[Sequence[float]],
    pool_theta: Sequence[Sequence[float]],
    means: Sequence[float],
    stds: Sequence[float],
    k: int = 120,
    n_samples: int = 400,
) -> List[List[float]]:
    z = apply_norm(obs_vec, means, stds)
    dists = [(sq_dist(z, pool_z[i]), i) for i in range(len(pool_z))]
    dists.sort(key=lambda t: t[0])
    nn = dists[:k]

    eps = 1e-12
    inv = [1.0 / (math.sqrt(d) + eps) for d, _ in nn]
    s_inv = sum(inv)
    probs = [v / s_inv for v in inv]

    cdf = []
    acc = 0.0
    for p in probs:
        acc += p
        cdf.append(acc)

    chosen = []
    for _ in range(n_samples):
        r = random.random()
        pos = 0
        while pos < len(cdf) and r > cdf[pos]:
            pos += 1
        if pos >= len(nn):
            pos = len(nn) - 1
        _, idx = nn[pos]
        base = pool_theta[idx]
        chosen.append([
            base[0] + random.gauss(0.0, 0.02),
            base[1] + random.gauss(0.0, 0.02),
            base[2] + random.gauss(0.0, 0.02),
        ])
    return chosen


def density_score(sample: Sequence[float], cloud: Sequence[Sequence[float]], bw: float = 0.05) -> float:
    denom = 2.0 * bw * bw
    return sum(math.exp(-sq_dist(sample, o) / denom) for o in cloud)


def map_from_samples(samples: Sequence[Sequence[float]]) -> List[float]:
    best = None
    best_s = -1.0
    for s in samples:
        sc = density_score(s, samples, bw=0.06)
        if sc > best_s:
            best_s = sc
            best = s
    return list(best)


def rmse(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / len(a))


def cvrmse(sim: Sequence[float], meas: Sequence[float]) -> float:
    m = statistics.fmean(meas)
    if abs(m) < 1e-9:
        return 0.0
    return math.sqrt(sum((s - y) ** 2 for s, y in zip(sim, meas)) / len(sim)) / m * 100.0


def scenario_observation(clean_vec: Sequence[float], scenario: str) -> List[float]:
    if scenario == "exp1_clean":
        return list(clean_vec)
    if scenario == "exp2_noise":
        return add_noise(clean_vec, factor=0.10)
    if scenario == "exp3_noise_missing":
        return add_noise_and_missing(clean_vec, factor=0.10, miss_ratio=0.35)
    raise ValueError("Unknown scenario")


def evaluate(
    test_rows: List[Sample],
    pool: Dict[str, List],
    out_dir: Path,
) -> Dict[str, Dict[str, float]]:
    scenarios = ["exp1_clean", "exp2_noise", "exp3_noise_missing"]
    result = {}

    posterior_dump = []

    for sc in scenarios:
        theta_errors = []
        cvrmse_elec = []
        cvrmse_gas = []
        t_infer = []

        for i, row in enumerate(test_rows):
            obs = scenario_observation(row.y_clean, sc)
            t0 = time.perf_counter()
            samples = estimate_posterior_samples(
                obs,
                pool_z=pool["x_z"],
                pool_theta=pool["theta"],
                means=pool["mean"],
                stds=pool["std"],
                k=120,
                n_samples=300,
            )
            theta_hat = map_from_samples(samples)
            t1 = time.perf_counter()

            y_hat = forward_model(tuple(theta_hat), row.temp)
            y_true = row.y_clean

            theta_errors.append(rmse(theta_hat, row.theta))
            cvrmse_elec.append(cvrmse(y_hat[:24], y_true[:24]))
            cvrmse_gas.append(cvrmse(y_hat[24:], y_true[24:]))
            t_infer.append(t1 - t0)

            if i == 0:
                for s in samples[:120]:
                    posterior_dump.append(
                        {
                            "scenario": sc,
                            "theta_occ": s[0],
                            "theta_light": s[1],
                            "theta_plug": s[2],
                        }
                    )

        result[sc] = {
            "theta_rmse": statistics.fmean(theta_errors),
            "cvrmse_electricity_pct": statistics.fmean(cvrmse_elec),
            "cvrmse_gas_pct": statistics.fmean(cvrmse_gas),
            "avg_inference_time_sec": statistics.fmean(t_infer),
        }

    posterior_path = out_dir / "posterior_samples_case0.csv"
    with posterior_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scenario", "theta_occ", "theta_light", "theta_plug"])
        w.writeheader()
        w.writerows(posterior_dump)

    return result


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    n_train = 1600
    n_test = 240

    train_rows = generate_dataset(n_train)
    test_rows = generate_dataset(n_test)

    pool = build_training_pool(train_rows)
    metrics = evaluate(test_rows, pool, out_dir)

    summary = {
        "paper": "Continuous model calibration framework for smart-building digital twin: A generative model-based approach",
        "replica": "Replicacion simplificada basada en simulacion forward + inverso generativo por vecindad",
        "seed": SEED,
        "n_train": n_train,
        "n_test": n_test,
        "metrics": metrics,
    }

    summary_path = out_dir / "resultados_resumen.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    table_path = out_dir / "metricas_replicacion.csv"
    with table_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "scenario",
            "theta_rmse",
            "cvrmse_electricity_pct",
            "cvrmse_gas_pct",
            "avg_inference_time_sec",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for sc, vals in metrics.items():
            row = {"scenario": sc}
            row.update(vals)
            w.writerow(row)

    print("Replica ejecutada correctamente.")
    for sc, vals in metrics.items():
        print(sc, vals)
    print("Archivos generados en:", out_dir)


if __name__ == "__main__":
    main()