from crisprmatch.fasta import Fasta


def test_fasta_compatibility_layer_returns_strings(tmp_path):
    fasta_path = tmp_path / "targets.fa"
    fasta_path.write_text(">target_A\nACGTACGT\n", encoding="utf-8")

    with Fasta(fasta_path) as fasta:
        assert fasta["target_A"][0].upper() == "A"
        assert fasta["target_A"][1:5].upper() == "CGTA"
        assert list(fasta.keys()) == ["target_A"]
