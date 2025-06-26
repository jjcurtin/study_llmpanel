import numpy as np
import matplotlib.pyplot as plt

def draw_horizontal_speedometer(percentage):
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("equal")
    ax.axis("off")

    radius = 1.0
    center = (0, 0)
    arc_width = 0.2

    # Helper to draw colored arc segment
    def draw_arc(start_angle, end_angle, color):
        theta = np.radians(np.linspace(start_angle, end_angle, 100))
        x_outer = center[0] + radius * np.cos(theta)
        y_outer = center[1] + radius * np.sin(theta)
        x_inner = center[0] + (radius - arc_width) * np.cos(theta[::-1])
        y_inner = center[1] + (radius - arc_width) * np.sin(theta[::-1])

        x = np.concatenate([x_outer, x_inner])
        y = np.concatenate([y_outer, y_inner])
        ax.fill(x, y, color=color, edgecolor='white', linewidth=2)

    # arc segments for speedometer
    draw_arc(180, 120, 'green')
    draw_arc(120, 60, 'yellow')
    draw_arc(60, 0, 'red')

    # needle line
    angle = 180 - (percentage * 180 / 100)
    angle_rad = np.radians(angle)
    x = center[0] + (radius - arc_width/2) * np.cos(angle_rad)
    y = center[1] + (radius - arc_width/2) * np.sin(angle_rad)
    ax.plot([center[0], x], [center[1], y], color='black', linewidth=3)

    #  Add labels for relative lapse risk percentage zones
    zone = 'High' if percentage > 66 else 'Medium' if percentage > 33 else 'Low'
    ax.text(0, -0.3, f"{zone}", fontsize=16, ha='center')

    plt.tight_layout()

    # save image
    fig.savefig(f'speedometer_{percentage}.png', bbox_inches='tight', pad_inches=0.1, dpi=300)

# Example usage
if __name__ == "__main__":
    while True:
        try:
            percentage = float(input("Enter a percentage (0-100): "))
            draw_horizontal_speedometer(percentage)
            print(f"Speedometer image saved as 'speedometer_{percentage}.png'")
        except ValueError as e:
            print(f"Error: {e}. Please enter a valid percentage between 0 and 100.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
