package mesin

import "sort"

// Port difflib.SequenceMatcher.ratio() dan difflib.get_close_matches() dari CPython,
// agar saran "Maksud Anda ...?" sama persis dengan versi Python.

type pencocok struct {
	a, b []rune
	b2j  map[rune][]int
}

func pencocokBaru(b []rune) *pencocok {
	p := &pencocok{b: b, b2j: map[rune][]int{}}
	for i, r := range b {
		p.b2j[r] = append(p.b2j[r], i)
	}
	if n := len(b); n >= 200 { // autojunk: buang elemen yang terlalu sering muncul
		batas := n/100 + 1
		for r, idx := range p.b2j {
			if len(idx) > batas {
				delete(p.b2j, r)
			}
		}
	}
	return p
}

func (p *pencocok) cocokTerpanjang(alo, ahi, blo, bhi int) (int, int, int) {
	besti, bestj, bestsize := alo, blo, 0
	j2len := map[int]int{}
	for i := alo; i < ahi; i++ {
		baru := map[int]int{}
		for _, j := range p.b2j[p.a[i]] {
			if j < blo {
				continue
			}
			if j >= bhi {
				break
			}
			k := j2len[j-1] + 1
			baru[j] = k
			if k > bestsize {
				besti, bestj, bestsize = i-k+1, j-k+1, k
			}
		}
		j2len = baru
	}
	for besti > alo && bestj > blo && p.a[besti-1] == p.b[bestj-1] {
		besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
	}
	for besti+bestsize < ahi && bestj+bestsize < bhi && p.a[besti+bestsize] == p.b[bestj+bestsize] {
		bestsize++
	}
	return besti, bestj, bestsize
}

func (p *pencocok) rasio(a []rune) float64 {
	p.a = a
	cocok := 0
	antrian := [][4]int{{0, len(a), 0, len(p.b)}}
	for len(antrian) > 0 {
		q := antrian[len(antrian)-1]
		antrian = antrian[:len(antrian)-1]
		alo, ahi, blo, bhi := q[0], q[1], q[2], q[3]
		i, j, k := p.cocokTerpanjang(alo, ahi, blo, bhi)
		if k > 0 {
			cocok += k
			if alo < i && blo < j {
				antrian = append(antrian, [4]int{alo, i, blo, j})
			}
			if i+k < ahi && j+k < bhi {
				antrian = append(antrian, [4]int{i + k, ahi, j + k, bhi})
			}
		}
	}
	panjang := len(a) + len(p.b)
	if panjang == 0 {
		return 1.0
	}
	return 2.0 * float64(cocok) / float64(panjang)
}

// paling mirip: get_close_matches(kata, kandidat, n=1, cutoff) → "" bila tidak ada.
func palingMirip(kata string, kandidat []string, batas float64) string {
	p := pencocokBaru([]rune(kata))
	terbaik, skorTerbaik := "", -1.0
	for _, k := range kandidat {
		skor := p.rasio([]rune(k))
		if skor < batas {
			continue
		}
		// Seri: heapq.nlargest memilih pasangan (skor, kata) terbesar.
		if skor > skorTerbaik || (skor == skorTerbaik && k > terbaik) {
			terbaik, skorTerbaik = k, skor
		}
	}
	return terbaik
}

// saranNama sama dengan saran_nama() di src/environment.py.
func saranNama(nama string, kandidat []string) string {
	if m := palingMirip(nama, kandidat, 0.7); m != "" {
		return " Maksud Anda '" + m + "'?"
	}
	return ""
}

func kunciUrut[V any](m map[string]V) []string {
	hasil := make([]string, 0, len(m))
	for k := range m {
		hasil = append(hasil, k)
	}
	sort.Strings(hasil)
	return hasil
}
