#version 330 core

uniform sampler2D memSlot;
uniform float alpha=1; // between 0 and 1

// uniform float time;

in vec2 uvs;
out vec4 f_color;

void main() {


    vec2 uvMapping = vec2(uvs.x,uvs.y);

    // get sampled vertex (from texture) at that uv coor
    vec4 sample = texture(memSlot,uvMapping);

    if (sample.a > 0 ){
        f_color = vec4(sample.r,sample.g,sample.b,sample.a*alpha);
    }
    else{
        discard;
    }
    
}
