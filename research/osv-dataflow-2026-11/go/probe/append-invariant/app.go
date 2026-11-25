package repro

func input() string { return "" }
func sink(s string) {}

func Run() {
	v := input()
	var out []string
	out = append(out, v)
	sink(out[0])
}
