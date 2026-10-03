#version 330 core

in vec2 vertexPosition;
in vec2 textureCoordinate;
out vec2 uvs;

void main() {
    
    uvs = textureCoordinate;


    gl_Position = vec4(vertexPosition,0.0,1.0);
}