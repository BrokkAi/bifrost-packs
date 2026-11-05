package probe

import (
	"archive/tar"
	"os"
	"path/filepath"
)

// Positive: the stored header name chooses the output path.
func extractOne(tr *tar.Reader, dst string) error {
	hdr, err := tr.Next()
	if err != nil {
		return err
	}
	f, err := os.Create(filepath.Join(dst, hdr.Name))
	if err != nil {
		return err
	}
	return f.Close()
}

// Near miss: only the base name is kept.
func extractBase(tr *tar.Reader, dst string) error {
	hdr, err := tr.Next()
	if err != nil {
		return err
	}
	f, err := os.Create(filepath.Join(dst, filepath.Base(hdr.Name)))
	if err != nil {
		return err
	}
	return f.Close()
}

// Near miss: non-local names are rejected.
func extractLocal(tr *tar.Reader, dst string) error {
	hdr, err := tr.Next()
	if err != nil {
		return err
	}
	if !filepath.IsLocal(hdr.Name) {
		return nil
	}
	f, err := os.Create(filepath.Join(dst, hdr.Name))
	if err != nil {
		return err
	}
	return f.Close()
}
