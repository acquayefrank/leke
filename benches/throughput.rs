use criterion::{black_box, criterion_group, criterion_main, Criterion};
use _leke::normalizer::KwaNormalizer;
use tokenizers::Tokenizer;

fn bench_normalizer(c: &mut Criterion) {
    let norm = KwaNormalizer::default();
    let text = "Wɔfrɛ me Kofi na mefiri Kumasi wɔ Ghana man mu. Ŋkɔnye enye Yao le Kpalime kple Volta nutome.";

    c.bench_function("normalizer_throughput", |b| {
        b.iter(|| norm.normalize_str(black_box(text)))
    });
}

fn bench_tokenizer(c: &mut Criterion) {
    let model_path = "models/bpe-8k/tokenizer.json";
    if !std::path::Path::new(model_path).exists() {
        return;
    }

    let tokenizer = Tokenizer::from_file(model_path).expect("Failed to load tokenizer");
    let text = "Wɔfrɛ me Kofi na mefiri Kumasi wɔ Ghana man mu. Ŋkɔnye enye Yao le Kpalime.";

    let encoding = tokenizer.encode(text, false).unwrap();
    let ids = encoding.get_ids().to_vec();

    c.bench_function("bpe_encode", |b| {
        b.iter(|| tokenizer.encode(black_box(text), black_box(false)).unwrap())
    });

    c.bench_function("bpe_decode", |b| {
        b.iter(|| tokenizer.decode(black_box(&ids), black_box(true)).unwrap())
    });
}

criterion_group!(benches, bench_normalizer, bench_tokenizer);
criterion_main!(benches);
