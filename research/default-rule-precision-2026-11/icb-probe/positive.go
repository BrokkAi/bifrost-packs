package fixture

func Adjacent(a, b bool, out []int) []int {
	if a {
		out = append(out, 1)
	} else if b {
		out = append(out, 1)
	} else {
		out = append(out, 2)
	}
	return out
}
