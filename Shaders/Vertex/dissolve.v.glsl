#version 330 core

uniform vec2 screenSize;
uniform vec2 spriteSize;
uniform vec2 spriteOffset;
uniform vec2 bgOffset;
uniform vec2 position;
uniform float rotation;
uniform float zoom;
uniform float screenZoom;
//uniform mat4 projectionMatrix;
// uniform mat4 transformationMatrix;

in vec2 vertexPosition;
in vec2 textureCoordinate;
out vec2 uvs;   

void main() {
    
    uvs = textureCoordinate;

    // scale sprite down to its appropriate size, but it is still at 0,0
    vec2 scaledVertexPosition = vertexPosition * (spriteSize*zoom*screenZoom/2);
    
    // find rotation
    float s = sin(rotation);
    float c = cos(rotation);
    vec2 rotatedVertexPosition = vec2(scaledVertexPosition.x*c - scaledVertexPosition.y*s,scaledVertexPosition.x*s + scaledVertexPosition.y*c);

    // scale again with screen size
    vec2 screenScaledVertexPosition = rotatedVertexPosition / (screenSize/2);

    // offset stays the same
    vec2 combinedOffset = vec2(position.x,-position.y) + vec2(bgOffset.x,-bgOffset.y) + vec2(spriteOffset.x,-spriteOffset.y);
    vec2 scaledOffset = (combinedOffset/(screenSize/2))*screenZoom;

    gl_Position = vec4(screenScaledVertexPosition + scaledOffset, 0.0, 1.0);
}