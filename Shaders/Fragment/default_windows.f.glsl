#version 330 core

uniform sampler2D memSlot;
uniform float alpha=1.0; // between 0 and 1

// uniform float time;

in vec2 uvs;
out vec4 f_color;

void main() {


    vec2 uvMapping = vec2(uvs.x ,-uvs.y);

    f_color = vec4(texture(memSlot,uvMapping).r,texture(memSlot,uvMapping).g ,texture(memSlot,uvMapping).b,texture(memSlot,uvMapping).a*alpha);
    
}