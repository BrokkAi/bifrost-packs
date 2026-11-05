package repro

func input() string                 { return "" }
func wrap(s string) (string, error) { return s, nil }
func sink(s string)                 {}

func Run() {
	raw := input()
	wrapped, err := wrap(raw)
	if err != nil {
		return
	}
	sink(wrapped)
}
