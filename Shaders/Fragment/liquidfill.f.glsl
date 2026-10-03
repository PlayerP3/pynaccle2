#version 330 core

// fV = fill value
uniform float fV;
uniform sampler2D memSlot;
uniform int PI=2;
uniform float TIME;
uniform float alpha=1;

in vec2 UV;
out vec4 f_color;

void main() {
    vec2 uv = ((UV / -0.10)) + vec2(1.25,1.25);

    vec4 bb = texture(memSlot,UV);
    float ccc = alpha;

    float
		sdf=length(uv),c=step(sdf,.85),
		
        vB=smoothstep(.1,.9,sin(uv.x+(PI*.5))-.3),
		vBA=vB*sin(TIME*4.)*.1,
        
        fW=(sin(((TIME*2.)+uv.x)*2.)*.05)+vBA,
		bW=(sin(((TIME*-2.)+uv.x)*2.+PI)*.05)-vBA,
		
        fA=(sin(TIME*4.)*.05)*vB,
        
        fP=fV * 2.3 +(sin((TIME)*PI)*.1) - 1.1,
		
        fF=step(uv.y,(fA+fW)+fP)*c,
		bF=step(uv.y,(-fA+bW)+fP)*c;

    f_color =
		vec4((step(sdf,1.)-step(sdf,.9))+
		(fF+(clamp(bF-fF,0.,1.)*.8))+
		clamp(pow((sdf+.01)*
		((1.-(fF+bF))*c),5.),0.,1.));
		
}

