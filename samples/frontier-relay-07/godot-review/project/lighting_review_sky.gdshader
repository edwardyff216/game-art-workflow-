shader_type sky;

// Static neutral studio radiance. World-space lobes are reflected by the asset's own BRDF.
void sky() {
	float fill = mix(0.065, 0.22, smoothstep(-0.25, 0.65, EYEDIR.y));
	float broad_key = smoothstep(0.74, 0.96, dot(EYEDIR, normalize(vec3(0.78, 0.39, -0.62))));
	float broad_fill = smoothstep(0.72, 0.97, dot(EYEDIR, normalize(vec3(0.22, 0.78, 0.60))));
	COLOR = vec3(fill + 0.64 * broad_key + 0.45 * broad_fill);
}
