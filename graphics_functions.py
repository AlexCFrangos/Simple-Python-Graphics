import math


def rotate_points(points, rotation):
    
    rotated_points = []
    rx = rotation[0] * (math.pi / 180)
    ry = rotation[1] * (math.pi / 180)
    rz = rotation[2] * (math.pi / 180)
    
    for x, y, z in points:
        #rotate x
        x1 = x
        y1 = y * math.cos(rx) - z * math.sin(rx)
        z1 = y * math.sin(rx) + z * math.cos(rx)

        #rotate y
        x2 = z1 * math.sin(ry) + x1 * math.cos(ry)
        y2 = y1
        z2 = z1 * math.cos(ry) - x1 * math.sin(ry)

        #rotate z
        x3 = x2 * math.cos(rz) - y2 * math.sin(rz)
        y3 = x2 * math.sin(rz) + y2 * math.cos(rz)
        z3 = z2
        
        rotated_points.append([x3, y3, z3])
        
    return rotated_points

def transform_points(points, transform):
    
    transformed_points = []
    tx, ty, tz = transform
    
    for point in points:
        x, y, z = point
        
        transformed_points.append(
            [
                x + tx,
                y + ty,
                z + tz
            ]
        )
        
    return transformed_points

def scale_points(points, scale):
    
    scaled_points = []
    sx, sy, sz = scale
    
    for point in points:
        x, y, z = point

        scaled_points.append(
            [
                x * sx,
                y * sy,
                z * sz
            ]
        )
        
    return scaled_points

def clip_points(points, distance):
    clipped_points = []
    previous = points[-1]

    for current in points:
        current_clipped = current[2] < distance
        previous_clipped = previous[2] < distance

        #calculate intersection point if two points cross clipping distance
        if current_clipped != previous_clipped:

            interpolant = (distance - previous[2]) / (current[2] - previous[2])

            intersection = [
                previous[0] + (current[0] - previous[0]) * interpolant,
                previous[1] + (current[1] - previous[1]) * interpolant,
                previous[2] + (current[2] - previous[2]) * interpolant
            ]

            clipped_points.append(intersection)

        if not current_clipped:
            clipped_points.append(current)

        previous = current

    return clipped_points

def project_points(points, focal_length, screen_size):
    
    flat_points = []
    for point in points:
        x, y, z = point

        fx = focal_length * (x / z) + (screen_size[0] / 2)
        fy = focal_length * (y / z) + (screen_size[1] / 2)

        flat_points.append([fx, fy])
    
    return flat_points