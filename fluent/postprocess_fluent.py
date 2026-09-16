import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.typing import ColorType


def load(file_path: str, column_name: str) -> pd.DataFrame:
    """
    Lazyloading function... file_path refers to the path of the .out file
    containing the Fluent simulation plaintext output of the variable...
    column_name can be chosen arbitrary but is intended to represent the
    desired name of the column containing the variable...
    """
    return pd.read_csv(
        file_path,
        sep=r"\s+",
        comment="(",
        names=["iteration", column_name],
        on_bad_lines="skip",
        skiprows=2,
        index_col=0,
    )


file_paths = {
    "hinge_moment_upper_flap": "~/CFD/Fluent/hinge_moment_upper_flap-rfile.out",
    "hinge_moment_lower_flap": "~/CFD/Fluent/hinge_moment_lower_flap-rfile.out",
    "normal_force_total": "~/CFD/Fluent/normal_force_total-rfile.out",
    "tangential_force_total": "~/CFD/Fluent/tangential_force_total-rfile.out",
    "side_force_total": "~/CFD/Fluent/side_force_total-rfile.out",
    "yaw_moment_total": "~/CFD/Fluent/yaw_moment_total-rfile.out",
    "roll_moment_total": "~/CFD/Fluent/roll_moment_total-rfile.out",
    "pitch_moment_total": "~/CFD/Fluent/pitch_moment_total-rfile.out",
}

df = pd.concat(
    [load(path, variable) for variable, path in file_paths.items()], axis=1
).reset_index()


# Case: Mach 1.6, 1 deg AoA, 10,000 m altitude...

GAMMA = 1.4  # air ratio of specific heats
R_AIR = 287.05  # J/(kg*K), specific gas constant for air
G0 = 9.80665  # m/s^2, standard gravity
LAPSE_RATE = 0.0065  # K/m, ISA troposphere lapse rate
T0_MSL = 288.15  # K, ISA sea-level temperature
P0_MSL = 101_325.0  # Pa, ISA sea-level pressure

MACH = 1.6
ALTITUDE = 10_000.0  # m
ALPHA_DEG = 1.0  # angle of attack, degrees

AREF = 13.825  # m^2, wing reference area
LREF = 4.3772  # m, reference length for roll/pitch/yaw moments

FLAP_CHORD = 0.55  # m, hinge-moment reference chord (per flap)
FLAP_SPAN = 2.0  # m, per flap
FLAP_AREA = FLAP_CHORD * FLAP_SPAN  # m^2, hinge-moment reference area (per flap)


def isa_troposphere(altitude_m: float) -> tuple[float, float, float]:
    """Standard atmosphere... Returns (T [K], rho [kg/m^3], a [m/s])..."""
    temperature = T0_MSL - LAPSE_RATE * altitude_m
    pressure = P0_MSL * (temperature / T0_MSL) ** (G0 / (R_AIR * LAPSE_RATE))
    density = pressure / (R_AIR * temperature)
    speed_of_sound = math.sqrt(GAMMA * R_AIR * temperature)
    return temperature, density, speed_of_sound


T_INF, RHO_INF, A_INF = isa_troposphere(ALTITUDE)
V_INF = MACH * A_INF
Q_INF = 0.5 * RHO_INF * V_INF**2

print(
    f"Freestream @ Mach {MACH}, {ALTITUDE:.0f} m ISA: "
    f"T={T_INF:.2f} K, rho={RHO_INF:.4f} kg/m^3, a={A_INF:.2f} m/s, "
    f"V={V_INF:.2f} m/s, q={Q_INF:.1f} Pa"
)

_alpha = math.radians(ALPHA_DEG)

df["lift_total"] = df["normal_force_total"] * math.cos(_alpha) - df[
    "tangential_force_total"
] * math.sin(_alpha)
df["drag_total"] = df["normal_force_total"] * math.sin(_alpha) + df[
    "tangential_force_total"
] * math.cos(_alpha)

df["CL"] = df["lift_total"] / (Q_INF * AREF)
df["CD"] = df["drag_total"] / (Q_INF * AREF)
df["CY"] = df["side_force_total"] / (Q_INF * AREF)
df["Cl_roll"] = df["roll_moment_total"] / (Q_INF * AREF * LREF)
df["Cm_pitch"] = df["pitch_moment_total"] / (Q_INF * AREF * LREF)
df["Cn_yaw"] = df["yaw_moment_total"] / (Q_INF * AREF * LREF)
df["Ch_upper_flap"] = df["hinge_moment_upper_flap"] / (Q_INF * FLAP_AREA * FLAP_CHORD)
df["Ch_lower_flap"] = df["hinge_moment_lower_flap"] / (Q_INF * FLAP_AREA * FLAP_CHORD)


plt.style.use(Path(__file__).parent.parent / "config" / "tokyonight.mplstyle")


def _annotate_final_value(
    ax: Axes, x_last: float, y_last: float, color: ColorType
) -> None:
    """Marks the last data point and labels it with its value, in the
    line's own color..."""
    ax.plot(x_last, y_last, "o", color=color, markersize=5, zorder=5)
    ax.annotate(
        f"{y_last:.4g}",
        xy=(x_last, y_last),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        color=color,
        fontsize=12,
        fontweight="bold",
    )


fig, ax = plt.subplots(figsize=(12, 6))
(line,) = ax.plot(df["iteration"], df["hinge_moment_upper_flap"])
_annotate_final_value(
    ax,
    df["iteration"].iloc[-1],
    df["hinge_moment_upper_flap"].iloc[-1],
    line.get_color(),
)

ax.set_xlabel("Solver Iteration")
ax.set_ylabel("Hinge Moment [N·m]")
ax.set_title(
    "Upper Flap Hinge Moment Convergence", loc="left", pad=15, fontweight="bold"
)
ax.set_xlim(left=0, right=df["iteration"].max() * 1.12)

plt.savefig("hinge_moment_upper_flap_hsp.png", dpi=200, bbox_inches="tight")
plt.show()


UNITS = {
    "moment": "N·m",
    "force": "N",
}

DERIVED_METADATA: dict[str, tuple[str, str]] = {
    "lift_total": ("Total Lift", "N"),
    "drag_total": ("Total Drag", "N"),
    "CL": ("Lift Coefficient (C_L)", ""),
    "CD": ("Drag Coefficient (C_D)", ""),
    "CY": ("Side Force Coefficient (C_Y)", ""),
    "Cl_roll": ("Roll Moment Coefficient (C_l)", ""),
    "Cm_pitch": ("Pitch Moment Coefficient (C_m)", ""),
    "Cn_yaw": ("Yaw Moment Coefficient (C_n)", ""),
    "Ch_upper_flap": ("Upper Flap Hinge Moment Coefficient (C_h)", ""),
    "Ch_lower_flap": ("Lower Flap Hinge Moment Coefficient (C_h)", ""),
}


def _get_metadata(column_name: str) -> tuple[str, str]:
    """Extracts a readable title and unit from the column name..."""
    if column_name in DERIVED_METADATA:
        return DERIVED_METADATA[column_name]

    clean_title = column_name.replace("_", " ").title()

    # Infer unit from variable name...
    unit = "Unknown"
    for keyword, u in UNITS.items():
        if keyword in column_name:
            unit = u
            break

    return clean_title, unit


def render(
    df: pd.DataFrame,
    x_col: str = "iteration",
    output_dir: str | Path = ".",
    show: bool = False,
) -> None:
    """
    Plots all variables in df against x_col and saves individual images...
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    style_file = Path(__file__).parent.parent / "config" / "tokyonight.mplstyle"
    if style_file.exists():
        plt.style.use(style_file)

    y_columns = [col for col in df.columns if col != x_col]

    for col in y_columns:
        title, unit = _get_metadata(col)

        fig, ax = plt.subplots(figsize=(12, 6))
        (line,) = ax.plot(df[x_col], df[col], linewidth=1.5)
        _annotate_final_value(
            ax, df[x_col].iloc[-1], df[col].iloc[-1], line.get_color()
        )

        ax.set_xlabel(x_col.replace("_", " ").title())
        ax.set_ylabel(f"{title} [{unit}]" if unit else title)
        ax.set_title(f"{title} Convergence", loc="left", pad=15, fontweight="bold")
        ax.set_xlim(left=0, right=df[x_col].max() * 1.12)

        file_out = output_path / f"{col}_convergence.png"
        fig.savefig(file_out, dpi=200, bbox_inches="tight")

        if show:
            plt.show()
        else:
            plt.close(fig)


render(df, show=True)
