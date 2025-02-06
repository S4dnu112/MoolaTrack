import shutil, math
from termcolor import colored
    

def match_category(keyword):
    keyword = keyword.lower().strip()

    category_map = {
        "Food & Dining": ["food", "dining"],
        "Leisure & Shopping": ["leisure", "shopping", "shop"],
        "Transportation": ["transpo", "transportation"],
        "Family & Education": ["family", "education"],
        "Health & Wellness": ["health", "wellness"],
        "Household": ["household"],
        "Other": ["other"]
    }
    valid_keywords = sorted({kw for kws in category_map.values() for kw in kws})

    for category, keywords in category_map.items():
        if keyword in keywords:
            return category

    raise ValueError(
        f"Invalid category. Must be one of: {', '.join(valid_keywords)}"
    )

    
def pie_chart(labels, data):
    
    terminal_width, terminal_height = shutil.get_terminal_size()

    try:
        total = sum(data)
        # Convert data to percentages
        percentages = [(val / total) * 100 for val in data]

        radius = min(terminal_height // 2 - 2, terminal_width // 4)
        center_x = terminal_width // 2
        center_y = terminal_height // 2

        colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

        # Draw the pie chart
        current_angle = 0
        chart = [[' ' for _ in range(terminal_width)] for _ in range(terminal_height)]
        for i, (percentage, label) in enumerate(zip(percentages, labels)):
            angle = percentage * 3.6  # Convert percentage to degrees
            color = colors[i % len(colors)]

            for y in range(terminal_height):
                for x in range(0, terminal_width, 2):
                    dx = (x - center_x) / 2  # Compensate for character width
                    dy = y - center_y
                    distance = math.sqrt(dx**2 + dy**2)

                    if distance <= radius:
                        point_angle = math.degrees(math.atan2(dy, dx))
                        if point_angle < 0:
                            point_angle += 360

                        if current_angle <= point_angle < current_angle + angle:
                            chart[y][x] = colored('█', color)
                            
            current_angle += angle

        print("\nPie Chart:")
        for row in chart:
            print(''.join(char if char else ' ' for char in row))
        
        
        print("\033[1m" + "Legend:\n".center(terminal_width) + "\033[0m")
        for i, (label, percentage, data) in enumerate(zip(labels, percentages, data)):
            color = colors[i % len(colors)]
            legend_text = label.ljust(18) + f"({percentage:.1f}%): ".rjust(11) + f"${data:,}".ljust(9)
            print(colored(f"█ {legend_text}".center(terminal_width), color))
            
    except Exception as e:
        print(e)

