#version 330 core
uniform sampler2D memSlot;
uniform float alpha = 1.0;
uniform vec4 outlineColor = vec4(0.92, 0.08, 0.08, 1.0); // black by default
uniform float outlineThickness = 1.0;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec2 texelSize = 1.0 / textureSize(memSlot, 0);
    vec4 sample = texture(memSlot, uvs);

    if (sample.a > 0) {
        // solid sprite pixel, draw normally
        f_color = vec4(sample.r, sample.g, sample.b, sample.a * alpha);
    } else {
        // check neighbours
        float neighbourAlpha = 0.0;
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                if (x == 0 && y == 0) continue;
                vec2 offset = vec2(x, y) * texelSize * outlineThickness;
                neighbourAlpha += texture(memSlot, uvs + offset).a;
            }
        }

        if (neighbourAlpha > 0.1) {
            f_color = vec4(outlineColor.rgb, outlineColor.a * alpha);
        } else {
            discard;
        }
    }
}