from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load(file_path: str, column_name: str) -> pd.DataFrame:
    """
    Lazyloading function... file_path refers to the path of the .out file
    containing the Fluent simulation plaintext output of the variable... 
    column_name can be chosen arbitrary but is intended to represent the
    desired name of the column containing the variable...
    """
    return pd.read_csv(
        file_path,
        sep = r'\s+',
        comment = '(',
        names = ['iteration', column_name],
        on_bad_lines= 'skip',
        skiprows = 2,  
        index_col = 0,
    )


file_paths = {
        "hinge_moment_upper_flap": "~/CFD/Fluent/hinge_moment_upper_flap-rfile.out",
        "hinge_moment_lower_flap": "~/CFD/Fluent/hinge_moment_lower_flap-rfile.out",
        "normal_force_total": "~/CFD/Fluent/normal_force_total-rfile.out",
        "tangential_force_total": "~/CFD/Fluent/tangential_force_total-rfile.out",
        "side_force_total": "~/CFD/Fluent/side_force_total-rfile.out",
        "yaw_moment_total": "~/CFD/Fluent/yaw_moment_total-rfile.out",
        "roll_moment_total": "~/CFD/Fluent/roll_moment_total-rfile.out",
        "pitch_moment_total": "~/CFD/Fluent/pitch_moment_total-rfile.out"
        }

df = pd.concat(
    [load(path, variable) for variable, path in file_paths.items()], axis=1
    ).reset_index()


plt.style.use(Path(__file__).parent.parent / "config" / "tokyonight.mplstyle")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df["iteration"], df["hinge_moment_upper_flap"])

ax.set_xlabel("Solver Iteration")
ax.set_ylabel("Hinge Moment [N·m]")
ax.set_title("Upper Flap Hinge Moment Convergence", loc="left", pad=15, fontweight="bold")
ax.set_xlim(left=0)

plt.savefig("hinge_moment_upper_flap_hsp.png", dpi=200, bbox_inches="tight")
plt.show()

# Unit mapping based on standard Fluent report conventions
UNITS = {
    "moment": "N·m",
    "force": "N",
}

def _get_metadata(column_name: str) -> tuple[str, str]:
    """Extracts a human-readable title and unit from the column name."""
    clean_title = column_name.replace("_", " ").title()
    
    # Infer unit from variable name
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
    show: bool = False
) -> None:
    """
    Plots all variables in df against x_col and saves individual images.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load stylesheet relative to current script safely
    style_file = Path(__file__).parent.parent / "config" / "tokyonight.mplstyle"
    if style_file.exists():
        plt.style.use(style_file)

    y_columns = [col for col in df.columns if col != x_col]

    for col in y_columns:
        title, unit = _get_metadata(col)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df[x_col], df[col], linewidth=1.5)

        ax.set_xlabel(x_col.replace("_", " ").title())
        ax.set_ylabel(f"{title} [{unit}]")
        ax.set_title(f"{title} Convergence", loc="left", pad=15, fontweight="bold")
        ax.set_xlim(left=0)

        # Clean file export
        file_out = output_path / f"{col}_convergence.png"
        fig.savefig(file_out, dpi=200, bbox_inches="tight")
        
        if show:
            plt.show()
        else:
            plt.close(fig)

render(df, show=True)
