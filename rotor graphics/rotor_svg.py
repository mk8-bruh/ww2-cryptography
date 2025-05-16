import math
from svgwrite import Drawing

def generate_enigma_rotor_svg(wiring, filename="enigma_rotor.svg", size=500):
    # Validate wiring
    if len(wiring) != 26 or not all(c.isalpha() and c.isupper() for c in wiring):
        raise ValueError("Wiring must be 26 uppercase letters")
    
    # Calculate dimensions
    wide_width = size/200
    thin_width = wide_width/8
    outer_radius = size / 2
    inner_radius = outer_radius * (7.25 / 24)
    letter_radius = outer_radius * 0.95  # Position for letter markers
    dot_radius = outer_radius * 0.005
    dot_outer = dot_radius * 4
    arrow_offset = outer_radius * 0.025
    arrow_size = wide_width * 4

    # Create drawing
    dwg = Drawing(filename, size=(size + wide_width, size + wide_width), profile='tiny')
    center = (size + wide_width) / 2
    
    # Draw concentric circles
    dwg.add(dwg.circle(center=(center, center), r=outer_radius, fill='none', stroke='black', stroke_width=wide_width))
    dwg.add(dwg.circle(center=(center, center), r=inner_radius, fill='none', stroke='black', stroke_width=thin_width))
    
    # Draw center cross
    cross_size = inner_radius * 0.07
    dwg.add(dwg.line((center - cross_size, center), (center + cross_size, center), stroke='black', stroke_width=thin_width))
    dwg.add(dwg.line((center, center - cross_size), (center, center + cross_size), stroke='black', stroke_width=thin_width))
    
    # Calculate positions for each letter
    letter_positions = []
    for i in range(26):
        angle = 2 * math.pi * i / 26 - math.pi/2  # Start at top (12 o'clock)
        x = center + letter_radius * math.cos(angle)
        y = center + letter_radius * math.sin(angle)
        letter_positions.append((x, y))
    
    # Draw arrows for wiring
    for i in range(26):
        start_pos = letter_positions[i]
        end_letter = wiring[i]
        end_idx = ord(end_letter) - ord('A')
        end_pos = letter_positions[end_idx]
        
        dwg.add(dwg.circle(center=start_pos, r=2.5, fill='black'))

        if i == end_idx:
            dwg.add(dwg.circle(center=start_pos, r=dot_outer, fill='none', stroke='black', stroke_width=wide_width/2))
            continue
        
        dir_vec = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        dir_len = math.sqrt(dir_vec[0]**2 + dir_vec[1]**2)

        start_pos = (start_pos[0] + dir_vec[0]/dir_len*arrow_offset, start_pos[1] + dir_vec[1]/dir_len*arrow_offset)
        end_pos = (end_pos[0] - dir_vec[0]/dir_len*arrow_offset, end_pos[1] - dir_vec[1]/dir_len*arrow_offset)

        # Create quadratic Bezier curve for the arrow
        path = dwg.path(d=f"M {start_pos[0] + dir_vec[0]/dir_len*arrow_size/2} {start_pos[1] + dir_vec[1]/dir_len*arrow_size/2} {end_pos[0] - dir_vec[0]/dir_len*arrow_size/2} {end_pos[1] - dir_vec[1]/dir_len*arrow_size/2}", 
                        fill='none', 
                        stroke='black', 
                        stroke_width=wide_width)
        
        # Add arrowhead
        angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
        arrow_x1 = end_pos[0] - arrow_size * math.cos(angle - math.pi/6)
        arrow_y1 = end_pos[1] - arrow_size * math.sin(angle - math.pi/6)
        arrow_x2 = end_pos[0] - arrow_size * math.cos(angle + math.pi/6)
        arrow_y2 = end_pos[1] - arrow_size * math.sin(angle + math.pi/6)
        
        dwg.add(path)
        dwg.add(dwg.polyline([end_pos, (arrow_x1, arrow_y1), (arrow_x2, arrow_y2), end_pos], 
                             fill='black', 
                             stroke='none'))
    
    dwg.save()

while True:
    [wiring, filename] = input().split()
    if wiring != "#":
        generate_enigma_rotor_svg(wiring, filename)