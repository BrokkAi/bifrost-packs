package probe

import (
	"archive/zip"
	"os"
	"path/filepath"
)

// Positive: each stored entry name chooses an output path.
func extract(archive, dst string) error {
	r, err := zip.OpenReader(archive)
	if err != nil {
		return err
	}
	for _, f := range r.File {
		out, err := os.Create(filepath.Join(dst, f.Name))
		if err != nil {
			return err
		}
		out.Close()
	}
	return r.Close()
}
