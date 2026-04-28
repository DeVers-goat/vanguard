"""Generate PWA icons for The Vanguard app."""
import os, struct, zlib, math

os.makedirs("icons", exist_ok=True)

def make_png(size):
    img = [[(0,0,0,0)]*size for _ in range(size)]
    cx, cy, r = size//2, size//2, int(size*0.46)

    # Draw filled rounded square background
    pad = int(size*0.08)
    for y in range(size):
        for x in range(size):
            # Rounded rect
            cr = int(size*0.22)
            rx, ry = x-pad, y-pad
            w, h = size-2*pad, size-2*pad
            in_rect = (cr<=rx<=w-cr and 0<=ry<=h) or (0<=rx<=w and cr<=ry<=h-cr)
            # corners
            for (ox,oy) in [(cr,cr),(w-cr,cr),(cr,h-cr),(w-cr,h-cr)]:
                if math.hypot(rx-ox, ry-oy) <= cr:
                    in_rect = True
                    break
            if in_rect:
                img[y][x] = (20, 16, 48, 255)  # dark purple bg

    # Draw "V" letter
    stroke = max(2, size//24)
    lw = max(3, size//16)
    # V shape: two lines meeting at bottom center
    v_top_y = int(size*0.25)
    v_bot_y = int(size*0.72)
    v_left_x = int(size*0.22)
    v_right_x = int(size*0.78)
    v_mid_x = size//2

    def draw_line(x0,y0,x1,y1,color,w):
        dx,dy = x1-x0, y1-y0
        length = max(abs(dx),abs(dy),1)
        for i in range(length+1):
            t = i/length
            px,py = int(x0+dx*t), int(y0+dy*t)
            for ox in range(-w,w+1):
                for oy in range(-w,w+1):
                    if ox*ox+oy*oy <= w*w:
                        nx,ny = px+ox, py+oy
                        if 0<=nx<size and 0<=ny<size:
                            img[ny][nx] = color

    # Left arm of V
    draw_line(v_left_x, v_top_y, v_mid_x, v_bot_y, (160,140,255,255), lw)
    # Right arm of V
    draw_line(v_right_x, v_top_y, v_mid_x, v_bot_y, (100,220,200,255), lw)

    # Build PNG bytes
    def pack_chunk(name, data):
        c = zlib.crc32(name+data)&0xffffffff
        return struct.pack('>I',len(data))+name+data+struct.pack('>I',c)

    raw = b'\x89PNG\r\n\x1a\n'
    raw += pack_chunk(b'IHDR', struct.pack('>IIBBBBB',size,size,8,6,0,0,0))
    rows = b''
    for row in img:
        rows += b'\x00' + b''.join(struct.pack('BBBB',r,g,b,a) for r,g,b,a in row)
    raw += pack_chunk(b'IDAT', zlib.compress(rows,9))
    raw += pack_chunk(b'IEND', b'')
    return raw

for sz, name in [(192,'icon-192.png'),(512,'icon-512.png')]:
    with open(f'icons/{name}','wb') as f:
        f.write(make_png(sz))
    print(f"Created icons/{name}")

print("Done!")
