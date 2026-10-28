import json

from leke.corpus import CorpusProcessor, run_pipeline, split_dataset, temperature_upsample


def test_corpus_processor_cleaning():
    processor = CorpusProcessor(min_words=3, max_words=10)
    lines = [
        "  too short ",
        "Wɔfrɛ me Kofi na mefiri Kumasi yie.",
        "Wɔfrɛ me Kofi na mefiri Kumasi yie.",  # duplicate
        "   ε   kple   γ   le   Evegbe   me.   ",  # needs variant mapping
    ]
    cleaned = processor.process_lines(lines)
    # The first line has 2 words (filtered out)
    assert len(cleaned) == 2
    # Duplicate removed
    assert cleaned[0] == "Wɔfrɛ me Kofi na mefiri Kumasi yie."
    # Variants mapped
    assert cleaned[1] == "ɛ kple ɣ le Evegbe me."


def test_split_dataset_isolation():
    lines = [f"Sentence number {i} for testing splits" for i in range(100)]
    train, dev, test = split_dataset(lines, train_ratio=0.8, dev_ratio=0.1, test_ratio=0.1, seed=42)

    assert len(train) == 80
    assert len(dev) == 10
    assert len(test) == 10

    # Strict isolation
    assert set(train).isdisjoint(set(dev))
    assert set(train).isdisjoint(set(test))
    assert set(dev).isdisjoint(set(test))


def test_temperature_upsampling_balance():
    data = {
        "dominant": [f"Dominant line {i}" for i in range(1000)],
        "small": [f"Small line {i}" for i in range(10)],
    }
    # Alpha = 0.5 gives weight proportional to sqrt(count)
    # sqrt(1000) ~ 31.6, sqrt(10) ~ 3.16 -> small is ~9.1% instead of 1.0%!
    pooled = temperature_upsample(data, alpha=0.5, total_samples=1000, seed=42)
    small_count = sum(1 for line in pooled if "Small" in line)
    # small language share should be significantly boosted
    assert small_count > 40  # significantly more than the original 1%


def test_run_pipeline_end_to_end(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "twi.txt").write_text(
        "Wɔfrɛ me Kofi wɔ Kumasi.\nAkwaaba ba Ghana man mu.\nObi nkyerɛ abofra Nyame koraa.\n"
    )
    (raw_dir / "ewe.txt").write_text(
        "Ŋkɔnye enye Yao le Kpalime.\nEvegbe nye gbe nyui aɖe.\nMìedó gbe na mi nyuie.\n"
    )

    out_dir = tmp_path / "splits"
    manifest_path = tmp_path / "manifest.json"

    manifest = run_pipeline(
        raw_dir=raw_dir,
        output_dir=out_dir,
        manifest_path=manifest_path,
        seed=42,
    )

    assert manifest_path.exists()
    assert "twi" in manifest["languages"]
    assert "ewe" in manifest["languages"]
    assert (out_dir / "twi" / "train.txt").exists()
    assert (out_dir / "pooled_train.txt").exists()

    with open(manifest_path) as f:
        loaded = json.load(f)
    assert loaded["version"] == "1.0.0"
    assert loaded["pooled"]["sentences"] > 0
