#version 330 core


uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 orthographicMatrix;
//uniform mat4 projectionMatrix;
// uniform mat4 transformationMatrix;

in vec2 vertexPosition;
in vec2 textureCoordinate;
out vec2 uvs;   

void main() {
    
    uvs = textureCoordinate;

    gl_Position = orthographicMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 0.0, 1.0);
}