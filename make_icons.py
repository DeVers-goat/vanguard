"""Generate professional PWA icons for The Vanguard app."""
import os, struct, zlib, math

os.makedirs("icons", exist_ok=True)

def lerp(a, b, t): return a + (b - a) * t
def lerp_color(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def make_png(size):
    img = [[(0,0,0,0)]*size for _ in range(size)]

    # Background: deep gradient — top-left dark purple to bottom-right deep navy
    bg1 = (14, 8, 42, 255)   # deep purple
    bg2 = (6, 14, 38, 255)   # deep navy

    cr = int(size * 0.22)  # corner radius
    pad = int(size * 0.0)

    def in_rounded_rect(x, y, r):
        w, h = size, size
        if r <= x <= w-r and 0 <= y <= h: return True
        if 0 <= x <= w and r <= y <= h-r: return True
        for ox, oy in [(r,r),(w-r,r),(r,h-r),(w-r,h-r)]:
            if math.hypot(x-ox, y-oy) <= r: return True
        return False

    # Draw background with gradient
    for y in range(size):
        for x in range(size):
            if in_rounded_rect(x, y, cr):
                t = (x + y) / (size * 2)
                img[y][x] = lerp_color(bg1, bg2, t)

    # V shape parameters
    # Left arm: top-left → bottom-center
    # Right arm (wing): bottom-center → top-right, with a swept wing tip

    cx = size * 0.5   # center x (bottom of V)
    cy = size * 0.72  # center y (bottom of V)
    stroke = max(3, size // 14)

    # Left arm endpoints
    lx1, ly1 = size * 0.20, size * 0.24   # top-left
    lx2, ly2 = cx, cy                      # bottom-center

    # Right arm: main direction
    rx1, ry1 = cx, cy                      # bottom-center
    rx2, ry2 = size * 0.78, size * 0.24   # top-right

    # Wing tip: extends from top of right arm, sweeping right and slightly up
    wx1, wy1 = rx2, ry2
    wx2, wy2 = size * 0.88, size * 0.20   # wing tip end

    # Color for left arm: purple gradient
    left_color1 = (124, 110, 248, 255)   # var(--p) purple
    left_color2 = (167, 139, 250, 255)   # lighter purple

    # Color for right arm + wing: teal to cyan
    right_color1 = (45, 212, 160, 255)   # var(--em) teal
    right_color2 = (103, 232, 249, 255)  # cyan

    def draw_thick_line(x0, y0, x1, y1, w, color_fn):
        dx, dy = x1-x0, y1-y0
        length = max(abs(dx), abs(dy), 1)
        steps = int(length * 2)
        for i in range(steps+1):
            t = i/steps
            px, py = x0 + dx*t, y0 + dy*t
            color = color_fn(t)
            hw = int(w * (1 + 0.3 * math.sin(t * math.pi)))  # slightly thicker in middle
            for ox in range(-hw, hw+1):
                for oy in range(-hw, hw+1):
                    if ox*ox+oy*oy <= hw*hw:
                        nx, ny = int(px+ox), int(py+oy)
                        if 0 <= nx < size and 0 <= ny < size:
                            bg = img[ny][nx]
                            # blend on top
                            a = color[3] / 255
                            img[ny][nx] = (
                                int(bg[0]*(1-a) + color[0]*a),
                                int(bg[1]*(1-a) + color[1]*a),
                                int(bg[2]*(1-a) + color[2]*a),
                                255
                            )

    # Draw left arm (purple)
    draw_thick_line(lx1, ly1, lx2, ly2, stroke,
        lambda t: (*lerp_color(left_color1[:3], left_color2[:3], t), 255))

    # Draw right arm (teal→cyan)
    draw_thick_line(rx1, ry1, rx2, ry2, stroke,
        lambda t: (*lerp_color(right_color1[:3], right_color2[:3], t), 255))

    # Draw wing tip (thinner, cyan)
    wing_stroke = max(2, stroke * 2 // 3)
    draw_thick_line(wx1, wy1, wx2, wy2, wing_stroke,
        lambda t: (*lerp_color(right_color2[:3], (200, 245, 255), t), int(255*(1-t*0.3))))

    # Add a small glow/dot at the V junction
    glow_r = max(3, stroke // 2)
    for ox in range(-glow_r*3, glow_r*3+1):
        for oy in range(-glow_r*3, glow_r*3+1):
            d = math.hypot(ox, oy)
            if d <= glow_r*3:
                nx, ny = int(cx+ox), int(cy+oy)
                if 0 <= nx < size and 0 <= ny < size:
                    a = max(0, 1 - d/(glow_r*3)) * 0.4
                    bg = img[ny][nx]
                    glow = (180, 255, 210)
                    img[ny][nx] = (
                        int(bg[0]*(1-a) + glow[0]*a),
                        int(bg[1]*(1-a) + glow[1]*a),
                        int(bg[2]*(1-a) + glow[2]*a),
                        255
                    )

    # Build PNG
    def pack_chunk(name, data):
        c = zlib.crc32(name+data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)

    raw = b'\x89PNG\r\n\x1a\n'
    raw += pack_chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    rows = b''
    for row in img:
        rows += b'\x00' + b''.join(struct.pack('BBBB', r, g, b, a) for r, g, b, a in row)
    raw += pack_chunk(b'IDAT', zlib.compress(rows, 9))
    raw += pack_chunk(b'IEND', b'')
    return raw

for sz, name in [(192, 'icon-192.png'), (512, 'icon-512.png')]:
    with open(f'icons/{name}', 'wb') as f:
        f.write(make_png(sz))
    print(f"Created icons/{name} ({sz}x{sz})")

print("Done!")
