#version 330 core

uniform vec2 screenSize;
uniform vec2 spriteSize;
uniform vec2 spriteOffset;
uniform vec2 bgOffset;
uniform vec2 position;
uniform float rotation;
uniform float zoom;

in vec2 vertexPosition;
in vec2 textureCoordinate;
out vec2 UV;

void main() {
    
    UV = textureCoordinate;

    // find rotation
    float s = sin(rotation);
    float c = cos(rotation);
    vec2 rotatedVertexPosition = vec2(vertexPosition.x*c - vertexPosition.y*s,vertexPosition.x*s + vertexPosition.y*c);

    // scale sprite down to its appropriate size, but it is still at 0,0
    vec2 scaledVertexPosition = rotatedVertexPosition * (spriteSize/screenSize) * zoom;

    // apply offset to move the the vertex coors where you want on the screen
    vec2 combinedOffset = vec2(position.x,-position.y) + vec2(bgOffset.x,-bgOffset.y) + vec2(spriteOffset.x,spriteOffset.y);

    vec2 scaledOffset = (combinedOffset/(screenSize/2))*zoom; 

    gl_Position = vec4(scaledVertexPosition + scaledOffset,0.0,1.0);



}

